from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from . import task

app = FastAPI()

task_list = []

class AddTask(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    priority: int = 1

@app.post("/add")
def add(task_param:AddTask):
    created_task = task.Task(name = task_param.name, description=task_param.description, deadline=task_param.deadline, priority=task_param.priority)
    task_list.append(created_task)
    return "Task created succesfully"

@app.get("/list")
def list_tasks():
    return task_list

class CheckTask(BaseModel):
    task_name:str
    uncheck:bool

@app.post("/check")
def check_task(task_param:CheckTask):
    for t in task_list:
        if t.name.lower() == task_param.task_name.lower():
            if t.done:
                if not task_param.uncheck:
                    return "Task was already completed"
                else:
                    t.done = False
                    return "Task check reverted"
            else:
                if task_param.uncheck:
                    return "Task wasn't completed"
                else:
                    t.done = True
                return "Task checked succesfully"
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