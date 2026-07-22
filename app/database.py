import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../database/jobs.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_consulta TEXT NOT NULL,
            empresa TEXT,
            puesto TEXT NOT NULL,
            nivel TEXT,
            area TEXT,
            ubicacion TEXT,
            modalidad TEXT,
            salario_min REAL,
            salario_max REAL,
            salario_promedio REAL,
            moneda TEXT DEFAULT 'MXN',
            fuente TEXT NOT NULL,
            url TEXT UNIQUE,
            experiencia TEXT,
            ingles TEXT,
            tecnologias TEXT,
            certificaciones TEXT,
            descripcion TEXT,
            observaciones TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

if __name__ == "__main__":
    init_db()
    print("Base de datos SQLite inicializada exitosamente.")
