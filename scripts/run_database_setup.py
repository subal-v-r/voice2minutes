#!/usr/bin/env python3
"""
Database setup script for Meeting Tracker
Run this script to initialize or reset the database
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.db import init_database, DB_PATH

def run_sql_script(script_path: str, db_path: str = DB_PATH):
    """Execute SQL script file"""
    if not os.path.exists(script_path):
        print(f"Error: SQL script not found: {script_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        with open(script_path, 'r') as f:
            sql_script = f.read()
        
        # Execute script
        cursor.executescript(sql_script)
        conn.commit()
        conn.close()
        
        print(f"Successfully executed: {script_path}")
        return True
        
    except Exception as e:
        print(f"Error executing {script_path}: {e}")
        return False

def main():
    """Main setup function"""
    print("Meeting Tracker Database Setup")
    print("=" * 40)
    
    # Check if database exists
    db_exists = os.path.exists(DB_PATH)
    if db_exists:
        response = input(f"Database {DB_PATH} already exists. Reset it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
        
        # Backup existing database
        backup_path = f"{DB_PATH}.backup"
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(DB_PATH, backup_path)
        print(f"Existing database backed up to: {backup_path}")
    
    # Initialize database using Python function
    print("Initializing database schema...")
    init_database()
    print("Database schema created successfully!")
    
    # Ask if user wants to load sample data
    response = input("Load sample data for testing? (Y/n): ")
    if response.lower() != 'n':
        script_path = os.path.join(os.path.dirname(__file__), 'seed_sample_data.sql')
        if run_sql_script(script_path):
            print("Sample data loaded successfully!")
        else:
            print("Failed to load sample data.")
    
    print("\nDatabase setup complete!")
    print(f"Database location: {os.path.abspath(DB_PATH)}")
    
    # Show database info
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM meetings")
    meeting_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM actions")
    action_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Meetings: {meeting_count}")
    print(f"Actions: {action_count}")

if __name__ == "__main__":
    main()
