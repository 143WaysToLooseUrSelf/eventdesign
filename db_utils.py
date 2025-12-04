import sqlite3
import hashlib
import os

# Путь к базе данных
DB_PATH = os.path.join(os.path.dirname(__file__), 'eventdesign.db')

def get_connection():
    """Создаем и возвращаем подключение к базе данных"""
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Инициализация базы данных и создание таблиц"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Создаем таблицу пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL
    )''')
    
    # Создаем таблицу категорий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL,
        description TEXT
    )''')
    
    # Создаем таблицу событий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT NOT NULL,
        category INTEGER,
        location TEXT,
        event_date TEXT,
        description TEXT,
        note TEXT,
        favorite BOOLEAN DEFAULT 0,
        FOREIGN KEY (category) REFERENCES Categories(category_id) ON DELETE SET NULL
    )''')
    
    # Создаем таблицу избранного
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Favorites (
        user_id INTEGER,
        event_id INTEGER,
        PRIMARY KEY (user_id, event_id),
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (event_id) REFERENCES Events(event_id) ON DELETE CASCADE
    )''')
    
    conn.commit()
    cursor.close()
    conn.close()

def hash_password(password):
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, login, password, email):
    """Регистрация нового пользователя"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Проверка существования логина
        cursor.execute('SELECT * FROM Users WHERE login = ?', (login,))
        if cursor.fetchone():
            return False, "Пользователь с таким логином уже существует"
        
        # Хеширование пароля
        hashed_password = hash_password(password)
        
        # Добавление пользователя
        cursor.execute('''
        INSERT INTO Users (user_name, login, password, email) 
        VALUES (?, ?, ?, ?)
        ''', (name, login, hashed_password, email))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def authenticate_user(login, password):
    """Аутентификация пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Хеширование введенного пароля
    hashed_password = hash_password(password)
    
    # Проверка логина и пароля
    cursor.execute('''
    SELECT user_id, user_name FROM Users 
    WHERE login = ? AND password = ?
    ''', (login, hashed_password))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return user

def get_categories():
    """Получение списка категорий"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT category_id, category_name, description FROM Categories')
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return categories

def add_category(name, description=''):
    """Добавление новой категории"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO Categories (category_name, description) 
        VALUES (?, ?)
        ''', (name, description))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def update_category(category_id, name, description=''):
    """Обновление категории"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE Categories 
        SET category_name = ?, description = ? 
        WHERE category_id = ?
        ''', (name, description, category_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def delete_category(category_id):
    """Удаление категории"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM Categories WHERE category_id = ?', (category_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def get_events():
    """Получение списка событий с названием категории"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        e.event_id, 
        e.event_name, 
        c.category_name, 
        e.location, 
        e.event_date, 
        e.description, 
        e.favorite 
    FROM Events e
    LEFT JOIN Categories c ON e.category = c.category_id
    ''')
    events = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return events

def add_event(name, category_id, date, location, description='', note='', favorite=False):
    """Добавление нового события"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO Events 
        (event_name, category, event_date, location, description, note, favorite) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, category_id, date, location, description, note, favorite))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def update_event(event_id, name, category_id, date, location, description='', note='', favorite=False):
    """Обновление события"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE Events 
        SET event_name = ?, category = ?, event_date = ?, 
            location = ?, description = ?, note = ?, favorite = ? 
        WHERE event_id = ?
        ''', (name, category_id, date, location, description, note, favorite, event_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def delete_event(event_id):
    """Удаление события"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM Events WHERE event_id = ?', (event_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def get_favorites(user_id):
    """Получение избранных событий для пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        e.event_id, 
        e.event_name, 
        c.category_name, 
        e.location, 
        e.event_date, 
        e.description, 
        e.favorite 
    FROM Events e
    JOIN Favorites f ON e.event_id = f.event_id
    LEFT JOIN Categories c ON e.category = c.category_id
    WHERE f.user_id = ?
    ''', (user_id,))
    
    favorites = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return favorites

def add_favorite(user_id, event_id):
    """Добавление события в избранное"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Проверяем, не добавлено ли уже в избранное
        cursor.execute('SELECT * FROM Favorites WHERE user_id = ? AND event_id = ?', (user_id, event_id))
        if cursor.fetchone():
            return True, None
        
        cursor.execute('''
        INSERT INTO Favorites (user_id, event_id) 
        VALUES (?, ?)
        ''', (user_id, event_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def remove_favorite(user_id, event_id):
    """Удаление события из избранного"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        DELETE FROM Favorites 
        WHERE user_id = ? AND event_id = ?
        ''', (user_id, event_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e) 