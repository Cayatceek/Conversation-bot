import sqlite3
from datetime import datetime

DB_PATH = "diary.db"

def connect_db():
    """Создаёт подключение к базе данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Создаёт таблицы, если их нет"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            text TEXT NOT NULL,
            mood TEXT,
            is_important BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,  -- 'user' или 'assistant'
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def add_entry(user_id, date, time, text, mood=None, is_important=False):
    """Добавляет запись в дневник"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO diary (user_id, date, time, text, mood, is_important) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, date, time, text, mood, is_important))
    conn.commit()
    cursor.close()
    conn.close()

def get_entries(user_id, date):
    """Получает записи за определённую дату"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, time, text, mood, is_important FROM diary WHERE user_id = ? AND date = ?", (user_id, date))
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return entries

def edit_entry(entry_id, new_text):
    """Редактирует запись"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE diary SET text = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_text, entry_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_entry(entry_id):
    """Удаляет запись"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diary WHERE id = ?", (entry_id,))
    conn.commit()
    cursor.close()
    conn.close()

def save_user(user_id, username, first_name, last_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, first_name, last_name, registered_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO NOTHING;
    """, (user_id, username, first_name, last_name, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

def save_message(user_id, role, content):
    """Сохраняет сообщение в базу данных."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    cursor.close()
    conn.close()

def get_chat_history(user_id, limit=10):
    """Загружает последние сообщения пользователя."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return history

def save_diary_entry(user_id, text):
    """Сохраняет запись в дневник"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO diary (user_id, date, time, text) VALUES (?, DATE('now'), TIME('now'), ?)", (user_id, text))
    conn.commit()
    cursor.close()
    conn.close()

def get_diary_entries(user_id, limit=10):
    """Получает последние записи из дневника"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, time, text FROM diary WHERE user_id = ? ORDER BY date DESC, time DESC LIMIT ?", (user_id, limit))
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return entries
