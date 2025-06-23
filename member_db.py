import sqlite3

def init_db():
    conn = sqlite3.connect('members.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS members (
            user_id TEXT PRIMARY KEY,
            is_approved INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def is_member(user_id):
    conn = sqlite3.connect('members.db')
    cur = conn.cursor()
    cur.execute("SELECT is_approved FROM members WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row and row[0] == 1

def apply_member(user_id):
    conn = sqlite3.connect('members.db')
    conn.execute("INSERT OR IGNORE INTO members (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()