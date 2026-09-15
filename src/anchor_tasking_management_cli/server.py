from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from . import task, database

app = FastAPI()

task_list = []
database.create_table()

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
    uncheck:bool

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
        global task_list
        task_list = []
        return "All tasks have been removed"
    for i, t in enumerate(task_list):
        if t.name.lower() == task_param.task_name.lower():
            task_list.pop(i)
            return "Task removed with succes"
    return "Task not found"

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