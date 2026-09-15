# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Installation
- Install dependencies: `uv sync`
- Install the project in editable mode: `uv pip install -e .`

### Running the Application
- Start the server: `uv run uvicorn anchor_tasking_management_cli.server:app --reload`
- Run the CLI: `uv run anchor <command>`

### Common CLI Commands
- `anchor init`: Initialize user profile
- `anchor add "Task Name" [options]`: Add a new task
- `anchor list [options]`: List all tasks
- `anchor check "Task Name"`: Toggle task completion status
- `anchor status`: Show overall task completion progress
- `anchor rm "Task Name"`: Remove a task
- `anchor edit "Task Name"`: Edit task details

## Architecture

The project is a client-server task management system.

### High-Level Structure
- **CLI Layer (`anchor.py`)**: A Typer-based command-line interface that sends HTTP requests to the server.
- **API Layer (`server.py`)**: A FastAPI server that exposes endpoints for task management and interfaces with the database.
- **Data Layer (`database.py`)**: A SQLite3 implementation for persistent storage of tasks.
- **Session Management (`session.py`)**: Handles local user authentication data stored in `~/.config/usr_data.json`.
- **Model (`task.py`)**: Defines the basic `Task` object structure.

### Data Flow
`CLI` $\rightarrow$ `FastAPI Server` $\rightarrow$ `SQLite Database`
