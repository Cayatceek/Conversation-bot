import psycopg2
from datetime import datetime


DB_CONFIG = {
    "dbname": "diary",
    "user": "diary_user",
    "password": "f333f9de8e984d75bc2f8ffc6bda9314",
    "host": "localhost",
    "port": 5432,
}

def connect_db():
    """Создаёт подключение к базе данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return None


def create_tables():
    """Создаёт таблицы, если их нет"""
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diary (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            text TEXT NOT NULL,
            mood VARCHAR(20),
            is_important BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            registered_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            role VARCHAR(10) NOT NULL,  -- 'user' или 'assistant'
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );


    """)
    conn.commit()
    cursor.close()
    conn.close()

def add_entry(user_id, date, time, text, mood=None, is_important=False):
    """Добавляет запись в дневник"""
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO diary (user_id, date, time, text, mood, is_important) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, date, time, text, mood, is_important))
    conn.commit()
    cursor.close()
    conn.close()

def get_entries(user_id, date):
    """Получает записи за определённую дату"""
    conn = connect_db()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT id, time, text, mood, is_important FROM diary WHERE user_id = %s AND date = %s", (user_id, date))
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return entries

def edit_entry(entry_id, new_text):
    """Редактирует запись"""
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE diary SET text = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s
    """, (new_text, entry_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_entry(entry_id):
    """Удаляет запись"""
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diary WHERE id = %s", (entry_id,))
    conn.commit()
    cursor.close()
    conn.close()

def save_user(user_id, username, first_name, last_name):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, first_name, last_name, registered_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING;
    """, (user_id, username, first_name, last_name, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

def save_message(user_id, role, content):
    """Сохраняет сообщение в базу данных."""
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, role, content) VALUES (%s, %s, %s)",
        (user_id, role, content)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_chat_history(user_id, limit=10):
    """Загружает последние сообщения пользователя."""
    conn = connect_db()
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit)
        )
        history = cursor.fetchall()  # Сохраняем результат перед закрытием
    except Exception as e:
        print(f"Ошибка при получении истории чата: {e}")
        history = []
    finally:
        cursor.close()
        conn.close()

    return history


def save_diary_entry(user_id, text):
    """Сохраняет запись в дневник"""
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO diary (user_id, date, time, text) VALUES (%s, CURRENT_DATE, CURRENT_TIME, %s)",
        (user_id, text)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_diary_entries(user_id, limit=10):
    """Получает последние записи из дневника"""
    conn = connect_db()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, time, text FROM diary WHERE user_id = %s ORDER BY date DESC, time DESC LIMIT %s",
        (user_id, limit)
    )
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return entries
