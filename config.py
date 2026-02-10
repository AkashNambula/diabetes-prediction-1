"""
MySQL Configuration Manager
Helps manage database credentials securely using environment variables
"""

import os
from pathlib import Path

def get_db_config():
    """
    Get database configuration from environment variables or defaults.
    Use this function to keep sensitive credentials out of code.
    
    Environment Variables:
    - DB_HOST: MySQL host (default: localhost)
    - DB_USER: MySQL username (default: root)
    - DB_PASSWORD: MySQL password (default: empty)
    - DB_NAME: Database name (default: diabetes_app)
    """
    
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'diabetes_app')
    }
    return config

def create_env_file():
    """Create a template .env file for users to fill in"""
    env_template = """# Database Configuration
# Copy this file to .env and fill in your MySQL credentials
# Then uncomment the DB_CONFIG section in auth.py to use environment variables

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=diabetes_app

# For production, use:
# DB_HOST=your_remote_host
# DB_USER=your_username
# DB_PASSWORD=your_secure_password
"""
    
    env_path = Path(__file__).parent / '.env.example'
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write(env_template)
        print(f"Created {env_path}")
        print("Copy this file to .env and update with your credentials")

if __name__ == "__main__":
    create_env_file()
