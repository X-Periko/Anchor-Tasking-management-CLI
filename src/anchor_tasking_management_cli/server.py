from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class AddTask(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    priority: int = 1

@app.post("/add")
def add(task:AddTask):
    return {
        "name":task.name,
        "description":task.description,
        "deadline":task.deadline,
        "priority": task.priority
            }