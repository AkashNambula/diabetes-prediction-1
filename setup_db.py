"""
Quick setup script for Diabetes Prediction App
This script helps you configure MySQL connection and test the database
"""

import mysql.connector
import sys

def setup_mysql_config():
    """Interactive setup for MySQL configuration"""
    print("=" * 60)
    print("Diabetes Prediction App - MySQL Configuration Setup")
    print("=" * 60)
    
    print("\nPlease provide your MySQL connection details:")
    print("(Press Enter to use default value shown in brackets)\n")
    
    host = input("MySQL Host [localhost]: ").strip() or "localhost"
    user = input("MySQL Username [root]: ").strip() or "root"
    password = input("MySQL Password []: ").strip()
    
    print("\n" + "=" * 60)
    print("Testing MySQL Connection...")
    print("=" * 60 + "\n")
    
    try:
        # Test connection
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✓ Successfully connected to MySQL!")
        print(f"  MySQL Version: {version[0]}\n")
        
        # Create database
        print("Creating database 'diabetes_app'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS diabetes_app")
        print("✓ Database created successfully!\n")
        
        # Connect to the database and create tables
        conn.close()
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database="diabetes_app"
        )
        cursor = conn.cursor()
        
        print("Creating tables...")
        
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
        print("✓ Users table created!")
        
        # Create predictions table
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
        print("✓ Predictions table created!\n")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Save configuration
        print("=" * 60)
        print("Saving configuration to auth.py...")
        print("=" * 60 + "\n")
        
        config_content = f"""import mysql.connector
import bcrypt
import streamlit as st
from datetime import datetime

# Database configuration
DB_CONFIG = {{
    'host': '{host}',
    'user': '{user}',
    'password': '{password}',
    'database': 'diabetes_app'
}}
"""
        
        # Read the rest of auth.py and append it
        try:
            with open('auth.py', 'r') as f:
                content = f.read()
                # Find where DB_CONFIG ends
                db_config_end = content.find('\ndef get_db_connection')
                if db_config_end > 0:
                    rest_of_file = content[db_config_end:]
                else:
                    rest_of_file = ""
            
            with open('auth.py', 'w') as f:
                f.write(config_content + rest_of_file)
            
            print("✓ Configuration saved successfully!")
            print("\nYour database is now ready to use!")
            print(f"Database: diabetes_app")
            print(f"Host: {host}")
            print(f"User: {user}\n")
            print("=" * 60)
            print("Setup Complete! You can now run the app:")
            print("$ streamlit run app.py")
            print("=" * 60)
            
        except Exception as e:
            print(f"✗ Error saving configuration: {e}")
            print("\nYou can manually update the DB_CONFIG in auth.py:")
            print(f"  'host': '{host}',")
            print(f"  'user': '{user}',")
            print(f"  'password': '{password}',")
            return False
            
        return True
        
    except mysql.connector.Error as err:
        print(f"✗ Connection Error: {err}")
        print("\nPlease check:")
        print("1. MySQL server is running")
        print("2. Host address is correct")
        print("3. Username and password are correct")
        print("\nYou may need to:")
        print("  - Start MySQL service")
        print("  - Verify your credentials")
        print("  - Check MySQL is installed\n")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}\n")
        return False

if __name__ == "__main__":
    success = setup_mysql_config()
    sys.exit(0 if success else 1)
