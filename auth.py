import mysql.connector
import bcrypt
import streamlit as st
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'akash2005',  # Change this to your MySQL password
    'database': 'diabetes_app'
}

def get_db_connection():
    """Create and return a MySQL database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        st.error(f"Database connection error: {err}")
        return None

def init_database():
    """Initialize the database and create users table if it doesn't exist"""
    try:
        # Connect to MySQL server without selecting a database first
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        conn.close()
        
        # Now connect to the specific database
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Create predictions table to store user prediction history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    pregnancies INT,
                    glucose FLOAT,
                    blood_pressure FLOAT,
                    skin_thickness FLOAT,
                    insulin FLOAT,
                    bmi FLOAT,
                    diabetes_pedigree_function FLOAT,
                    age INT,
                    prediction INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
    """Register a new user in the database"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "Username or email already exists"
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (username, email, password, full_name) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_password, full_name)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Registration successful! You can now login."
    except mysql.connector.Error as err:
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
            "SELECT id, username, password, full_name FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and verify_password(password, user[2]):
            return True, {'id': user[0], 'username': user[1], 'full_name': user[3]}, "Login successful"
        else:
            return False, None, "Invalid username or password"
    except mysql.connector.Error as err:
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, 
             bmi, dpf, age, prediction)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
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
              FROM predictions WHERE user_id = %s ORDER BY created_at DESC""",
            (user_id,)
        )
        predictions = cursor.fetchall()
        cursor.close()
        conn.close()
        return predictions
    except mysql.connector.Error as err:
        return []

def get_user_by_id(user_id):
    """Get user information by ID"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, full_name FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return {'id': user[0], 'username': user[1], 'email': user[2], 'full_name': user[3]}
        return None
    except mysql.connector.Error as err:
        return None
