import sqlite3
import hashlib
import pandas as pd
import os
import shutil
from datetime import datetime

def get_db_path():
    """Retourne le chemin de la base de données qui persiste"""
    # Toujours utiliser le répertoire courant pour garantir la persistance
    # Sur Streamlit Cloud, le répertoire courant persiste entre les sessions
    db_path = "app_database.db"
    return db_path

DB_NAME = get_db_path()

def ensure_db_exists():
    """S'assure que la base de données existe et est initialisée"""
    # Créer le répertoire si nécessaire (pour le cas où on voudrait changer de répertoire)
    db_dir = os.path.dirname(os.path.abspath(DB_NAME)) if os.path.dirname(DB_NAME) else os.getcwd()
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

def init_db():
    """Initialise les tables utilisateurs et historique si elles n'existent pas."""
    ensure_db_exists()
    # Utiliser check_same_thread=False pour éviter les problèmes de threading avec Streamlit
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    # Activer les foreign keys et améliorer la robustesse
    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging pour de meilleures performances
    c = conn.cursor()
    # Table Utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    # Table Historique
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  market_name TEXT, 
                  date TEXT, 
                  total_amount REAL, 
                  filename TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_user(username, password):
    """Crée un nouvel utilisateur dans la base de données"""
    try:
        ensure_db_exists()
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        c = conn.cursor()
        # Vérifier si l'utilisateur existe déjà
        c.execute("SELECT username FROM users WHERE username=?", (username,))
        if c.fetchone():
            conn.close()
            return False  # L'utilisateur existe déjà
        # Créer l'utilisateur
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False # L'utilisateur existe déjà
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur: {e}")
        return False

def check_login(username, password):
    """Vérifie les identifiants de connexion"""
    try:
        ensure_db_exists()
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
        result = c.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"Erreur lors de la vérification du login: {e}")
        return False

def add_to_history(username, market_name, total_amount, filename):
    """Ajoute une entrée à l'historique des factures"""
    try:
        ensure_db_exists()
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        c = conn.cursor()
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO history (username, market_name, date, total_amount, filename) VALUES (?, ?, ?, ?, ?)",
                  (username, market_name, date_now, total_amount, filename))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erreur lors de l'ajout à l'historique: {e}")

def get_user_history(username):
    """Récupère l'historique des factures d'un utilisateur"""
    try:
        ensure_db_exists()
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        df = pd.read_sql_query("SELECT market_name, date, total_amount, filename FROM history WHERE username = ? ORDER BY id DESC", conn, params=(username,))
        conn.close()
        return df
    except Exception as e:
        print(f"Erreur lors de la récupération de l'historique: {e}")
        return pd.DataFrame()  # Retourner un DataFrame vide en cas d'erreur

