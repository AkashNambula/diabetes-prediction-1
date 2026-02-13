
import sqlite3
import os

# Database file
DB_FILE = 'diabetes_app.db'

def view_data():
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        print("\n=== USERS TABLE ===")
        try:
            cursor.execute("SELECT * FROM users")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            if rows:
                # Calculate column widths
                widths = [len(col) for col in columns]
                for row in rows:
                    for i, val in enumerate(row):
                        widths[i] = max(widths[i], len(str(val)))
                
                # Print header
                header = " | ".join(f"{col:<{width}}" for col, width in zip(columns, widths))
                print(header)
                print("-" * len(header))
                
                # Print rows
                for row in rows:
                    line = " | ".join(f"{str(val):<{width}}" for val, width in zip(row, widths))
                    print(line)
            else:
                print("No users found.")
        except Exception as e:
            print(f"Error reading users table: {e}")

        print("\n" + "="*50 + "\n")

        print("=== PREDICTIONS TABLE ===")
        try:
            cursor.execute("SELECT * FROM predictions")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            if rows:
                # Calculate column widths (capped at 50 chars for readability)
                widths = [len(col) for col in columns]
                for row in rows:
                    for i, val in enumerate(row):
                        widths[i] = min(50, max(widths[i], len(str(val))))
                
                # Print header
                header = " | ".join(f"{col:<{width}}" for col, width in zip(columns, widths))
                print(header)
                print("-" * len(header))
                
                # Print rows
                for row in rows:
                    line = " | ".join(f"{str(val)[:50]:<{width}}" for val, width in zip(row, widths))
                    print(line)
            else:
                print("No predictions found.")
        except Exception as e:
            print(f"Error reading predictions table: {e}")

        conn.close()

    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    view_data()
