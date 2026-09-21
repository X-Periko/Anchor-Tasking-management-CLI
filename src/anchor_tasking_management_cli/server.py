from fastapi import *
from pydantic import BaseModel
from typing import Optional
from . import task, database, security

app = FastAPI()

task_list = []
database.create_table()

@app.get("/health")
def health_check():
    return {"Status":"Server running"}

class SignUp(BaseModel):
    nick: str
    mail: str
    password: str
    created_at: str

@app.post("/signup")
def signup(data:SignUp):
    password_hash = security.hash_password(data.password)
    database.create_user(data.nick, data.mail, password_hash)

class Loing(BaseModel):
    nick: Optional[str]
    mail: Optional[str]
    password: str

@app.post("/login")
def login(data:login):
    found = database.get_user_by_nick(data.nick)
    if len(found) == 0:
        found = database.get_user_by_email(data.mail)
    if len(found) == 0:
        raise HTTPException(status_code=401, detail="Invalid nick or password")
    account = found[0]
    if security.verify_password(data.password, account.get("password_hash")):
        return {"Succes":True,
                "acces_token": security.create_access_token(account.get("id")),
                "token_type": "bearer"
                }

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
    rm:bool = False

@app.post("/check")
def check_task(task_param:CheckTask):
    try:
        id = int(task_param.task_id)
    except:
        tasks_founded = database.find_tasks_by_name(task_param.task_id)
        if len(tasks_founded) == 0:
            return "No task was found with that name"
        elif len(tasks_founded) > 1:
            return "Various tasks where found with that name"
        id = tasks_founded[0].get("id")
    database.set_done(id, done = not task_param.uncheck)
    if task_param.rm:
        database.delete_task(id)   
    return "Task checked succesfully"

class DelTask(BaseModel):
    task_name:str

@app.post("/del")
def del_task(task_param:DelTask):
    if task_param.task_name == ".":
        database.delete_task(1, all=True)
        return "All tasks have been removed"
    try:
        id = int(task_param.task_name)
    except:
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
    try:
        id = int(task_param.task_id)
    except:
        tasks_founded = database.find_tasks_by_name(task_param.task_name)
        if len(tasks_founded) == 0:
            return "No task was found with that name"
        elif len(tasks_founded) > 1:
            return "Various tasks where found with that name"
        id = tasks_founded[0].get("id")
    database.edit_task(id, description=task_param.description, deadline=task_param.deadline, priority=task_param.priority)
    return "Task eddited with succes"