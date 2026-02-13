
import mysql.connector
import sqlite3
import sys
from datetime import datetime

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'akash2005',
    'database': 'diabetes_app'
}

# SQLite Database
SQLITE_DB = 'diabetes_app.db'

def setup_mysql():
    print("=" * 60)
    print("Starting MySQL Setup and Migration...")
    print("=" * 60)

    try:
        # 1. Connect to MySQL Server
        print("\n1. Connecting to MySQL server...")
        try:
            conn_server = mysql.connector.connect(
                host=MYSQL_CONFIG['host'],
                user=MYSQL_CONFIG['user'],
                password=MYSQL_CONFIG['password']
            )
            cursor_server = conn_server.cursor()
        except mysql.connector.Error as err:
            print(f"   Error connecting to MySQL server: {err}")
            return False
        
        # 2. Create Database
        print(f"2. Creating database '{MYSQL_CONFIG['database']}' if not exists...")
        cursor_server.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
        cursor_server.close()
        conn_server.close()
        
        # 3. Connect to Database
        print("3. Connecting to the database...")
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # 4. Create Tables
        print("4. Creating tables...")
        
        # Users Table
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
        print("   - Users table created (or already exists)")
        
        # Predictions Table
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
        print("   - Predictions table created (or already exists)")
        
        # 5. Migrate Data from SQLite
        print("\n5. Migrating data from SQLite...")
        
        try:
            sqlite_conn = sqlite3.connect(SQLITE_DB)
            sqlite_conn.row_factory = sqlite3.Row
            sqlite_cursor = sqlite_conn.cursor()
            
            # Migrate Users
            print("   - Migrating users...")
            try:
                users = sqlite_cursor.execute("SELECT * FROM users").fetchall()
                users_migrated = 0
                for user in users:
                    try:
                        cursor.execute(
                            "INSERT INTO users (username, email, password, full_name, created_at) VALUES (%s, %s, %s, %s, %s)",
                            (user['username'], user['email'], user['password'], user['full_name'], user['created_at'])
                        )
                        users_migrated += 1
                    except mysql.connector.Error as err:
                        if err.errno == 1062: # Duplicate entry
                            print(f"     Skipping duplicate user: {user['username']}")
                        else:
                            print(f"     Error migrating user {user['username']}: {err}")
                print(f"     -> Migrated {users_migrated} new users")
            except sqlite3.OperationalError:
                 print("   - No 'users' table found in SQLite DB (it might be empty)")

            
            # Migrate Predictions
            # We need to map old SQLite user IDs to new MySQL user IDs
            # But since we are likely migrating into an empty DB or with same structure, distinct usernames are key
            
            print("   - Migrating predictions...")
            try:
                predictions = sqlite_cursor.execute("SELECT * FROM predictions").fetchall()
                preds_migrated = 0
                
                for pred in predictions:
                    # Get the username for the old user_id
                    old_user = sqlite_cursor.execute("SELECT username FROM users WHERE id = ?", (pred['user_id'],)).fetchone()
                    if old_user:
                        username = old_user['username']
                        # Get new user_id from MySQL
                        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                        new_user = cursor.fetchone()
                        
                        if new_user:
                            new_user_id = new_user[0]
                            # Insert prediction
                            try:
                                cursor.execute("""
                                    INSERT INTO predictions 
                                    (user_id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, 
                                    bmi, diabetes_pedigree_function, age, prediction, created_at) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    new_user_id, pred['pregnancies'], pred['glucose'], pred['blood_pressure'], 
                                    pred['skin_thickness'], pred['insulin'], pred['bmi'], 
                                    pred['diabetes_pedigree_function'], pred['age'], pred['prediction'], pred['created_at']
                                ))
                                preds_migrated += 1
                            except mysql.connector.Error as err:
                                print(f"     Error migrating prediction: {err}")
                
                print(f"     -> Migrated {preds_migrated} predictions")
            except sqlite3.OperationalError:
                 print("   - No 'predictions' table found in SQLite DB")
            
            sqlite_conn.close()
            
        except sqlite3.Error as e:
            print(f"   ! SQLite Error (maybe file doesn't exist or is empty): {e}")
        except Exception as e:
            print(f"   ! Migration Error: {e}")

        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("Setup and Migration Complete!")
        print("=" * 60)
        return True

    except mysql.connector.Error as err:
        print(f"\n✗ MySQL Error: {err}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = setup_mysql()
    sys.exit(0 if success else 1)
