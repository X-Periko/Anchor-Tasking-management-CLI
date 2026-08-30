import typer
import requests
from typing import Optional

app = typer.Typer()
SERVER_URL = "http://localhost:8000"

@app.command("add")
def add(name:str, description:Optional[str] = None, deadline:Optional[str] = None, priority:int = 1):
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

@app.command("list")
def list_tasks(simple:bool = False):
	try:
		response = requests.get(SERVER_URL+"/list")
		response_list = response.json()
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

@app.command("check")
def check_task(task):
	try:
		response = requests.post(SERVER_URL+"/check", json={"task_name":task})
		typer.echo(response.json())
	except requests.exceptions.ConnectionError:
		typer.echo("Couldn't establish connection with server")
	except requests.exceptions.HTTPError as e:
		typer.echo(f"Server error: \n{e}")
	except Exception as e:
		typer.echo(e)

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

@app.command("rm")
def delete(task_name):
	try:
		response = requests.post(SERVER_URL+"/del", json={"task_name":task_name})
		typer.echo(response.json())
	except requests.exceptions.ConnectionError:
		typer.echo("Couldn't establish connection with server")
	except requests.exceptions.HTTPError as e:
		typer.echo(f"Server error: \n{e}")
	except Exception as e:
		typer.echo(e)

if __name__ == "__main__":
	app()