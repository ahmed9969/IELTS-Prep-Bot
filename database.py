import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            username TEXT,
            subscription_status TEXT DEFAULT 'trial',
            trial_start TEXT,
            subscription_end TEXT,
            stars_paid INTEGER DEFAULT 0,
            joined_date TEXT,
            tests_remaining INTEGER DEFAULT 5,
            is_admin INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            test_type TEXT,
            score INTEGER,
            total INTEGER,
            band TEXT,
            date TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            total_score INTEGER DEFAULT 0,
            tests_taken INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()

def add_user(telegram_id, name, username):
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    trial_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    joined_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO users (telegram_id, name, username, trial_start, joined_date)
            VALUES (?, ?, ?, ?, ?)
        """, (telegram_id, name, username, trial_start, joined_date))
        conn.commit()
    except:
        pass
    conn.close()

def get_user(telegram_id):
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def can_take_test(telegram_id):
    user = get_user(telegram_id)
    if not user:
        return False, "not_found"
    
    # Admin always has access
    if user[10] == 1:
        return True, "admin"
    
    # Active subscription
    if user[4] == "active":
        sub_end = datetime.strptime(user[6], "%Y-%m-%d %H:%M:%S")
        if datetime.now() < sub_end:
            return True, "subscribed"
    
    # Has remaining tests
    if user[9] > 0:
        return True, "has_tests"
    
    return False, "no_tests"

def use_test(telegram_id):
    user = get_user(telegram_id)
    if not user:
        return
    # Don't deduct for admins or active subscribers
    if user[10] == 1:
        return
    if user[4] == "active":
        sub_end = datetime.strptime(user[6], "%Y-%m-%d %H:%M:%S")
        if datetime.now() < sub_end:
            return
    # Deduct one test
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET tests_remaining = tests_remaining - 1 WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()

def add_tests(telegram_id, amount):
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET tests_remaining = tests_remaining + ? WHERE telegram_id = ?", (amount, telegram_id))
    conn.commit()
    conn.close()

def activate_subscription(telegram_id, stars):
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    sub_end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE users SET subscription_status = 'active', subscription_end = ?, stars_paid = stars_paid + ?
        WHERE telegram_id = ?
    """, (sub_end, stars, telegram_id))
    conn.commit()
    conn.close()

def admin_unlock(telegram_id):
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_admin = 1, tests_remaining = 9999 WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()

def save_progress(telegram_id, test_type, score, total, band):
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO progress (telegram_id, test_type, score, total, band, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (telegram_id, test_type, score, total, band, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    cursor.execute("""
        INSERT INTO leaderboard (telegram_id, name, total_score, tests_taken)
        VALUES (?, (SELECT name FROM users WHERE telegram_id = ?), ?, 1)
        ON CONFLICT(telegram_id) DO UPDATE SET
        total_score = total_score + ?,
        tests_taken = tests_taken + 1
    """, (telegram_id, telegram_id, score, score))
    
    conn.commit()
    conn.close()

def get_progress(telegram_id):
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress WHERE telegram_id = ? ORDER BY date DESC LIMIT 10", (telegram_id,))
    progress = cursor.fetchall()
    conn.close()
    return progress

def get_leaderboard():
    conn = sqlite3.connect("ielts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, total_score, tests_taken FROM leaderboard ORDER BY total_score DESC LIMIT 10")
    leaders = cursor.fetchall()
    conn.close()
    return leaders