import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

DB_NAME = "app_database.db"

def init_db():
    """Initialise les tables utilisateurs et historique si elles n'existent pas."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Table Utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    # Table Historique
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  market_name TEXT, 
                  date TEXT, 
                  total_amount REAL, 
                  filename TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_user(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False # L'utilisateur existe déjà

def check_login(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result is not None

def add_to_history(username, market_name, total_amount, filename):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO history (username, market_name, date, total_amount, filename) VALUES (?, ?, ?, ?, ?)",
              (username, market_name, date_now, total_amount, filename))
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT market_name, date, total_amount, filename FROM history WHERE username = ? ORDER BY id DESC", conn, params=(username,))
    conn.close()
    return df

