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
				out += t.get("name")
			typer.echo(f" - {out if out != "" else "Task list empty. Good job!"}")
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

if __name__ == "__main__":
	app()