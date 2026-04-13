import sqlite3

def lift_ban():
    conn = sqlite3.connect('security_logs.db')
    cursor = conn.cursor()
    
    # This deletes all bans so you can get back in
    cursor.execute("DELETE FROM blacklist")
    
    conn.commit()
    print(f"Bans lifted! {cursor.rowcount} IP(s) removed from blacklist.")
    conn.close()

if __name__ == "__main__":
    lift_ban()