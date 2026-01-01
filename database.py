import sqlite3
from datetime import datetime

DB_NAME = "fitness_logs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Table for individual workout logs
    c.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            exercise_type TEXT,
            reps INTEGER,
            score INTEGER
        )
    ''')
    # Table for user profile (Notice the fixed commas and 'goal' column)
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            calorie_goal INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_workout(workout):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO workouts (timestamp, exercise_type, reps, score)
        VALUES (?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        workout['exercise_type'],
        workout['reps'],
        workout['score']
    ))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM workouts ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    return rows

# --- NEW: Helper to calculate total calories for TODAY ---
def get_today_calories():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Get today's date string (YYYY-MM-DD)
    today = datetime.now().strftime("%Y-%m-%d")
    # Sum scores where the timestamp starts with today's date
    c.execute("SELECT SUM(score) FROM workouts WHERE timestamp LIKE ?", (today + '%',))
    result = c.fetchone()[0]
    conn.close()
    return result if result else 0

def save_user_info(name, age, goal):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Clear old profile to keep only one user
    c.execute('DELETE FROM user_info')
    c.execute('''
        INSERT INTO user_info (name, age, calorie_goal)
        VALUES (?, ?, ?)
    ''', (name, age, goal))
    conn.commit()
    conn.close()

def get_user_info():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Safety check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_info'")
    if not c.fetchone():
        return None

    c.execute('SELECT name, age, calorie_goal FROM user_info LIMIT 1')
    row = c.fetchone()
    conn.close()

    if row:
        return {'name': row[0], 'age': row[1], 'calorie_goal': row[2]}
    return None

if __name__ == "__main__":
    init_db()