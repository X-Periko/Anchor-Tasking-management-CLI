from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from . import task, database

app = FastAPI()

task_list = []
database.create_table()

@app.get("/health")
def health_check():
    return {"Status":"Server running"}

class AddTask(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    priority: int = 1

@app.post("/add")
def add(task_param:AddTask):    
    database.add_task(name=task_param.name, description=task_param.description, deadline=task_param.deadline, priority=task_param.priority)
    return "Task created succesfully"

@app.get("/list")
def list_tasks():
    task_list = database.list_tasks()
    return task_list

class CheckTask(BaseModel):
    task_id:str 
    uncheck:bool = False

@app.post("/check")
def check_task(task_param:CheckTask):
    if task_param.task_id is str:
        tasks_founded = database.find_tasks_by_name(task_param.task_id)
        if len(tasks_founded) == 0:
            return "No task was found with that name"
        elif len(tasks_founded) > 1:
            return "Various tasks where found with that name"
        
    return "Task not found"

class DelTask(BaseModel):
    task_name:str

@app.post("/del")
def del_task(task_param:DelTask):
    if task_param.task_name == ".":
        database.delete_task(1, all=True)
        return "All tasks have been removed"
    id = database.find_tasks_by_name(task_param.task_name)
    if len(id) > 1:
        return "More than one task was found with that name. Refer to the task by its id"
    if len(id) == 0:
        return "No task was found with that name"
    id = id[0].get("id")
    database.delete_task(id)
    return "Task removed with succes"

class EditTask(BaseModel):
    task_name:str
    deadline:str
    priority:int
    description:str

@app.post("/edit")
def edit_task(task_param:EditTask):
    for i, t in enumerate(task_list):
        if t.name.lower() == task_param.task_name.lower():
            t.description = task_param.description
            t.deadline = task_param.deadline
            t.priority = task_param.priority
            return "Task eddited with succes"
    return "Task not found"