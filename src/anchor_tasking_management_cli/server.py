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