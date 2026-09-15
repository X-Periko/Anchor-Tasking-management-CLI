import os
import sqlite3
from pathlib import Path

# En Android/iOS, Flet expone FLET_APP_STORAGE_PATH apuntando a un directorio
# privado escribible de la app. En escritorio no existe, así que caemos al
# directorio del propio módulo.
_APP_STORAGE = os.environ.get("FLET_APP_STORAGE_PATH")
DB_DIR = Path(_APP_STORAGE) if _APP_STORAGE else Path(__file__).parent
DB_PATH = DB_DIR / "tasks.db"


def connect():
    # Asegurar que el directorio existe (Android lo crea vacío al instalar)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acceder a las columnas por nombre: fila["nombre"]
    return conn


def create_table():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                deadline TEXT,
                priority INTEGER NOT NULL DEFAULT 1,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)

def add_task(name, description=None, deadline=None, priority=1):
    with connect() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (name, description, deadline, priority) VALUES (?, ?, ?, ?)",
            (name, description, deadline, priority)
        )
        return cursor.lastrowid


def list_tasks():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
        return [dict(r) for r in rows]


def get_task(task_id):
    with connect() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None


def set_done(task_id, done: bool):
    with connect() as conn:
        conn.execute("UPDATE tasks SET done = ? WHERE id = ?", (int(done), task_id))


def edit_task(task_id, description, deadline, priority):
    with connect() as conn:
        conn.execute(
            "UPDATE tasks SET description = ?, deadline = ?, priority = ? WHERE id = ?",
            (description, deadline, priority, task_id)
        )

def delete_task(task_id):
    with connect() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

def find_tasks_by_name(name):
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE name LIKE ?",
            (name,)
        ).fetchall()
        return [dict(r) for r in rows]

if __name__ == "__main__":
    create_table()
    print(f"Base de datos creada en: {DB_PATH}")
