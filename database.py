import sqlite3
from datetime import datetime 

def init_db():
    conn = sqlite3.connect("pomodoro_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_time INTEGER,
            break_time INTEGER,
            figure_set TEXT,
            date TEXT  
        )
    ''')
    conn.commit()
    conn.close()

def save_session(work, break_m, figure):
    conn = sqlite3.connect("pomodoro_data.db")
    cursor = conn.cursor()
 
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO sessions (work_time, break_time, figure_set, date) VALUES (?, ?, ?, ?)", 
                   (work, break_m, figure, local_time))
    conn.commit()
    conn.close()
def get_all_sessions():
    conn = sqlite3.connect("pomodoro_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT work_time, break_time, figure_set, date FROM sessions ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows