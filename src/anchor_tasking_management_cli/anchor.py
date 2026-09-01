import typer
import requests
from typing import Optional
from rich.prompt import Prompt, IntPrompt, Confirm

app = typer.Typer()
SERVER_URL = "http://localhost:8000"
USR_DATA = None
USER_INITIATED = False

@app.command("init")
def init_anchor():
	nick = Prompt.ask("Enter your name")
	mail = Prompt.ask("Enter your email")
	password = Prompt.ask("Enter your password", password=True)
	global USR_DATA 
	global USER_INITIATED
	USR_DATA = {
		"nick": nick,
		"mail": mail,
		"password": password
	}
	USER_INITIATED = True
	typer.echo(USR_DATA)

@app.command("add")
def add(name:str, description:Optional[str] = None, deadline:Optional[str] = None, priority:int = 1):
	if USER_INITIATED == True:
		try:
			response = requests.post(SERVER_URL + "/add", json={
				"name":name.title(),
				"description":description,
				"deadline":deadline,
				"priority":priority
			})
			typer.echo(f"Status: {response.status_code}")
			typer.echo(response.json())
		except:
			typer.echo(f"Couldn't establish connection with server")
	else:
		typer.echo("Run anchor init to complete your authentication before using the sistem")

@app.command("list")
def list_tasks(simple:bool = False, sort:Optional[str] = False, pending:Optional[bool] = False, done:Optional[bool] = False):
	if USER_INITIATED:
		try:
			response = requests.get(SERVER_URL+"/list")
			response_list = response.json()
			if sort == "priority":
				new_list = []
				prior_list = []
				for t in response_list:
					prior_list.append(t.get("priority"))
				for x in range(len(prior_list)):
					min_prior = max(prior_list)
					index = prior_list.index(min_prior)
					prior_list.remove(min_prior)
					new_list.append(response_list[index])
					response_list.pop(index)
				response_list = new_list
			if pending:
				response_list = [t for t in response_list if not t.get("done")]
			if done:
				response_list = [t for t in response_list if t.get("done")]
			if pending and done:
				typer.echo("Can't use --pending and --done flags in same command")
				return True
			if simple:
				out = ""
				for t in response_list:
					out += f"- {t.get("name")}\n"
				typer.echo(f"{out if out != "" else "Task list empty. Good job!"}")
			else:
				if response_list == []:
					typer.echo("Task list empty. Good job!")
				else:
					for t in response_list:
						typer.echo(f"-> {"☑" if t.get("done") else "☐"} {t.get("name")}")
						typer.echo(f"	· Description: {t.get("description") if t.get("description") != None else "No description was added"}")
						typer.echo(f"	· Deadline: {t.get("deadline") if t.get("deadline") != None else "No deadline was added"}")
						typer.echo(f"	· Priority: {t.get("priority")}")
		except requests.exceptions.ConnectionError:
			typer.echo("Couldn't establish connection with server")
		except requests.exceptions.HTTPError as e:
			typer.echo(f"Server error: \n{e}")
	else:
		typer.echo("Run anchor init to complete your authentication before using the sistem")

@app.command("check")
def check_task(task, uncheck:Optional[bool] = False):
	if USER_INITIATED:
		try:
			response = requests.post(SERVER_URL+"/check", json={"task_name":task,"uncheck":uncheck})
			typer.echo(response.json())
		except requests.exceptions.ConnectionError:
			typer.echo("Couldn't establish connection with server")
		except requests.exceptions.HTTPError as e:
			typer.echo(f"Server error: \n{e}")
		except Exception as e:
			typer.echo(e)
	else:
		typer.echo("Run anchor init to complete your authentication before using the sistem")

def progress_bar(done: int, total: int, width: int = 20) -> str:
    if total == 0:
        return f"[{'░' * width}] 0%"
    ratio = done / total
    filled = int(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    percent = int(ratio * 100)
    return f"[{bar}] {percent}%"

@app.command("status")
def status():
	if USER_INITIATED:
		try:
			response = requests.get(SERVER_URL+"/list")
			response_list = response.json()
			done = 0
			for t in response_list:
				if t.get("done"):
					done += 1
			if len(response_list) == 0:
				typer.echo("You don't have any task today.")
			else:
				typer.echo(progress_bar(done=done, total= len(response_list)))
				typer.echo(f"{done} tasks completed out of {len(response_list)}") 
				if done == len(response_list):
					typer.echo("Congratulations. You have no tasks left!")
		except requests.exceptions.ConnectionError:
			typer.echo("Couldn't establish connection with server")
		except requests.exceptions.HTTPError as e:
			typer.echo(f"Server error: \n{e}")
		except Exception as e:
			typer.echo(e)
	else:
		typer.echo("Run anchor init to complete your authentication before using the sistem")

@app.command("rm")
def delete(task_name):
	if USER_INITIATED:
		try:
			response = requests.post(SERVER_URL+"/del", json={"task_name":task_name})
			typer.echo(response.json())
		except requests.exceptions.ConnectionError:
			typer.echo("Couldn't establish connection with server")
		except requests.exceptions.HTTPError as e:
			typer.echo(f"Server error: \n{e}")
		except Exception as e:
			typer.echo(e)
	else:
		typer.echo("Run anchor init to complete your authentication before using the sistem")

@app.command("edit")
def edit_task(task_name):
	if USER_INITIATED:
		try:
			response = requests.get(SERVER_URL+"/list")
			task_list = response.json()
			for t in task_list:
				if t.get("name").lower() == task_name.lower():
					current = t
			if current:
				description = Prompt.ask("Description", default=current.get("description") or "")
				deadline = Prompt.ask("Deadline (YYYY-MM-DD)", default=current.get("deadline") or "")
				priority = IntPrompt.ask("Priority", default=current.get("priority", 1))
				typer.echo(f"\nSummary:\n  Description: {description}\n  Deadline: {deadline}\n  Priority: {priority}")
				if Confirm.ask("¿Confirm changes?"):
					response = requests.post(SERVER_URL+"/edit", json={
						"task_name":task_name,
						"priority":priority,
						"deadline":deadline,
						"description":description
					})
					typer.echo(response.json())
		except requests.exceptions.ConnectionError:
			typer.echo("Couldn't establish connection with server")
		except requests.exceptions.HTTPError as e:
			typer.echo(f"Server error: \n{e}")
		except Exception as e:
			typer.echo(e)
	else:
		typer.echo("Run anchor init to complete your authentication before using the sistem")

if __name__ == "__main__":
	app()