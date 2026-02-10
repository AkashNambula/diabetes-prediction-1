"""
SQLite-based Authentication Module
Use this as an alternative if MySQL is not available
This is suitable for development and testing
For production, use MySQL version (auth.py)
"""

import sqlite3
import bcrypt
import streamlit as st
from datetime import datetime
from pathlib import Path

# Database file path
DB_FILE = Path(__file__).parent / 'diabetes_app.db'

def get_db_connection():
    """Create and return SQLite database connection"""
    try:
        conn = sqlite3.connect(str(DB_FILE))
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as err:
        st.error(f"Database connection error: {err}")
        return None

def init_database():
    """Initialize SQLite database and create tables"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    full_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    pregnancies INTEGER,
                    glucose REAL,
                    blood_pressure REAL,
                    skin_thickness REAL,
                    insulin REAL,
                    bmi REAL,
                    diabetes_pedigree_function REAL,
                    age INTEGER,
                    prediction INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return False

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username, email, password, full_name):
    """Register a new user"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "Username or email already exists"
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)",
            (username, email, hashed_password, full_name)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Registration successful! You can now login."
    except Exception as err:
        return False, f"Registration error: {err}"

def login_user(username, password):
    """Authenticate a user"""
    conn = get_db_connection()
    if not conn:
        return False, None, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Fetch user by username
        cursor.execute(
            "SELECT id, username, password, full_name FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and verify_password(password, user[2]):
            return True, {'id': user[0], 'username': user[1], 'full_name': user[3]}, "Login successful"
        else:
            return False, None, "Invalid username or password"
    except Exception as err:
        return False, None, f"Login error: {err}"

def save_prediction(user_id, pregnancies, glucose, blood_pressure, skin_thickness, 
                   insulin, bmi, dpf, age, prediction):
    """Save prediction to database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO predictions 
            (user_id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, 
             diabetes_pedigree_function, age, prediction) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, 
             bmi, dpf, age, prediction)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as err:
        return False

def get_user_predictions(user_id):
    """Get all predictions for a user"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, 
                     bmi, diabetes_pedigree_function, age, prediction, created_at 
              FROM predictions WHERE user_id = ? ORDER BY created_at DESC""",
            (user_id,)
        )
        predictions = cursor.fetchall()
        cursor.close()
        conn.close()
        return predictions
    except Exception as err:
        return []

def get_user_by_id(user_id):
    """Get user information by ID"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, full_name FROM users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return {'id': user[0], 'username': user[1], 'email': user[2], 'full_name': user[3]}
        return None
    except Exception as err:
        return None
