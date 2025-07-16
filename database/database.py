import sqlite3
import threading
import os
from datetime import datetime

db_lock = threading.Lock()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'waf_bypass_results.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_results_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            target_waf TEXT,
            payload TEXT NOT NULL,
            status TEXT NOT NULL,
            reason TEXT,
            response_time REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_result(target_waf, payload, status, reason, response_time):
    with db_lock:
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO results (timestamp, target_waf, payload, status, reason, response_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), target_waf, payload, status, reason, response_time))
            conn.commit()
        finally:
            conn.close()

if __name__ == '__main__':
    create_results_table()
    print("Database and results table created successfully.")
    insert_result("TestWAF", "<script>alert(1)</script>", "blocked", "XSS attempt detected", 0.5)
    print("Example result inserted.")