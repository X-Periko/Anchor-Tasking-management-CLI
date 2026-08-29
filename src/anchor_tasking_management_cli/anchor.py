import typer
import requests
from typing import Optional

app = typer.Typer()
SERVER_URL = "http://localhost:8000"

@app.command("add")
def add(name:str, description:Optional[str] = None, deadline:Optional[str] = None, priority:int = 1):
	response = requests.post(SERVER_URL + "/add", json={
		"name":name,
		"description":description,
		"deadline":deadline,
		"priority":priority
    })
	typer.echo(f"Status: {response.status_code}")
	typer.echo(response.json())

@app.command("list")
def list_tasks():
	pass

if __name__ == "__main__":
	app()