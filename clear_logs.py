import sqlite3
import os

def maintenance_wipe():
    # 1. Path to your database
    db_path = 'security_logs.db'
    
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found. Are you in the right folder?")
        return

    try:
        # 2. Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 3. Execute the delete command
        # This clears the logs but keeps the table structure
        cursor.execute("DELETE FROM intrusions")
        
        # 4. Reset the ID counter (Optional)
        # This makes the next log start at ID 1 again
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='intrusions'")
        
        conn.commit()
        print(f"--- DATABASE MAINTENANCE COMPLETE ---")
        print(f"Successfully deleted {cursor.rowcount} intrusion logs.")
        print(f"ID counters have been reset.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    confirm = input("Are you sure you want to WIPE ALL LOGS? (y/n): ")
    if confirm.lower() == 'y':
        maintenance_wipe()
    else:
        print("Operation cancelled.")