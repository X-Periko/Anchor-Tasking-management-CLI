import typer
import requests
import time
import readchar
import threading
from typing import Optional
from rich.prompt import Prompt, IntPrompt, Confirm
from . import session

token = "placeholder"

app = typer.Typer()
SERVER_URL = "http://localhost:8000"

def session_exists() -> bool:
	if session.load_session() not in [None, FileNotFoundError]:
		return True
	else:
		return False

@app.command("init")
def init_anchor(restore:Optional[bool] = False):
	if restore:
		session.restore_session()
		typer.echo("Session restored")
		return True
	nick = Prompt.ask("Enter your name")
	mail = Prompt.ask("Enter your email")
	password = Prompt.ask("Enter your password", password=True)
	USR_DATA = {
		"nick": nick,
		"mail": mail,
		"password": password
	}
	session.save_session(data=USR_DATA)
	typer.echo(USR_DATA)

@app.command("add")
def add(name:str):
	if session_exists():
		try:
			description = Prompt.ask("Description", default="No description was added")
			deadline = Prompt.ask("Deadline (YYYY-MM-DD)", default="No deadline was added")
			priority = IntPrompt.ask("Priority", default=1)
			response = requests.post(SERVER_URL + "/add", json={
				"name":name.title(),
				"description":description,
				"deadline":deadline,
				"priority":priority
			},
			headers={"Authorization": f"Bearer {token}"})
			typer.echo(response.json())
		except:
			typer.echo(f"Couldn't establish connection with server")
	else:
		typer.echo("Run anchor init to complete your authentication before using the system")

@app.command("list")
def list_tasks(simple:bool = False, sort:Optional[str] = False, pending:Optional[bool] = False, done:Optional[bool] = False, dynamic:Optional[bool] = False):
	if session_exists():
		def escuchar_salida(stop_event: threading.Event):
			while not stop_event.is_set():
				key = readchar.readkey()
				if key.lower() == "q":
					stop_event.set()
		def print_list():
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
						out += f"- {"☑" if t.get("done") else "☐"} {t.get("name")}\n\n"
					typer.echo(f"{out if out != "" else "Task list empty. Good job!"}")
				else:
					if response_list == []:
						typer.echo("Task list empty. Good job!")
					else:
						for t in response_list:
							typer.echo(f"-> {"☑" if t.get("done") else "☐"}   {t.get("id")}: {t.get("name")}")
							typer.echo(f"	· Description: {t.get("description") if t.get("description") != None else "No description was added"}")
							typer.echo(f"	· Deadline: {t.get("deadline") if t.get("deadline") != None else "No deadline was added"}")
							typer.echo(f"	· Priority: {t.get("priority")}\n")
			except requests.exceptions.ConnectionError:
				typer.echo("Couldn't establish connection with server")
			except requests.exceptions.HTTPError as e:
				typer.echo(f"Server error: \n{e}")
		if not dynamic:
			print_list()
		else:
			stop_event = threading.Event()
			listener = threading.Thread(target=escuchar_salida, args=(stop_event,), daemon=True)
			listener.start()
			while not stop_event.is_set():
				for _ in range(100):
					typer.echo("")
				print_list()
				typer.echo("\n\nPress q to exit dynamic listing")
				time.sleep(1)
	else:
		typer.echo("Run anchor init to complete your authentication before using the system")

@app.command("rm")
def delete(task_name):
	if session_exists():
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
		typer.echo("Run anchor init to complete your authentication before using the system")

@app.command("check")
def check_task(task, uncheck:Optional[bool] = False, rm:Optional[bool] = False):
	if session_exists():
		try:
			response = requests.post(SERVER_URL+"/check", json={"task_id":str(task),"uncheck":uncheck, "rm":rm})
			typer.echo(response.json())
		except requests.exceptions.ConnectionError:
			typer.echo("Couldn't establish connection with server")
		except requests.exceptions.HTTPError as e:
			typer.echo(f"Server error: \n{e}")
		except Exception as e:
			typer.echo(e)
	else:
		typer.echo("Run anchor init to complete your authentication before using the system")

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
	if session_exists():
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
		typer.echo("Run anchor init to complete your authentication before using the system")

@app.command("edit")
def edit_task(task_name):
	if session_exists():
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
		typer.echo("Run anchor init to complete your authentication before using the system")

if __name__ == "__main__":
	app()