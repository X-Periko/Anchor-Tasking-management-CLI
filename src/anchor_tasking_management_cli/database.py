import os
import sqlite3
from pathlib import Path

# En Android/iOS, Flet expone FLET_APP_STORAGE_PATH apuntando a un directorio
# privado escribible de la app. En escritorio no existe, así que caemos al
# directorio del propio módulo.
_APP_STORAGE = os.environ.get("FLET_APP_STORAGE_PATH")
DB_DIR = Path(_APP_STORAGE) if _APP_STORAGE else Path(__file__).parent
DB_PATH = DB_DIR / "tareas.db"


def conectar():
    # Asegurar que el directorio existe (Android lo crea vacío al instalar)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acceder a las columnas por nombre: fila["nombre"]
    return conn


def crear_tablas():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                frecuencia TEXT NOT NULL,       -- 'd' diario, 's' semanal, 'm' mensual
                duracion INTEGER NOT NULL,      -- minutos
                cumplido INTEGER NOT NULL DEFAULT 0,   -- 0/1 (SQLite no tiene booleano nativo)
                ultima_actualizacion TEXT       -- fecha ISO (YYYY-MM-DD) de la última vez marcado
            )
        """)


if __name__ == "__main__":
    crear_tablas()
    print(f"Base de datos creada en: {DB_PATH}")
