from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.db import get_db
import mysql.connector
from datetime import date, timedelta

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, role='user', avatar_url=None, balance=0, bio=None, display_name=None, streak_count=0, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.avatar_url = avatar_url
        self.balance = balance
        self.bio = bio
        self.display_name = display_name or username
        self.streak_count = streak_count
        self.created_at = created_at

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
def create_user(username, email, password, display_name=None):
    db = get_db()
    cursor = db.cursor()
    hashed_password = generate_password_hash(password)
    
    if not display_name:
        display_name = username

    try:
        query = """
            INSERT INTO users (username, display_name, email, password_hash, streak_count, last_login_date) 
            VALUES (%s, %s, %s, %s, 1, CURDATE())
        """
        cursor.execute(query, (username, display_name, email, hashed_password))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"DB Error: {err}")
        return False
    finally:
        cursor.close()


def get_user_by_email(email):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user_data = cursor.fetchone()
    cursor.close()
    
    if user_data:
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            role=user_data['role'],
            avatar_url=user_data['avatar_url'],
            balance=user_data['balance'],
            bio=user_data.get('bio'),
            display_name=user_data.get('display_name'),
            streak_count=user_data.get('streak_count'),
            created_at=user_data.get('created_at')
        )
    return None

def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    
    if user_data:
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            role=user_data['role'],
            avatar_url=user_data['avatar_url'],
            balance=user_data['balance'],
            bio=user_data.get('bio'),
            display_name=user_data.get('display_name'),
            streak_count=user_data.get('streak_count'),
            created_at=user_data.get('created_at')
        )
    return None

def get_user_by_username(username):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()
    cursor.close()
    
    if user_data:
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            role=user_data['role'],
            avatar_url=user_data['avatar_url'],
            balance=user_data['balance'],
            bio=user_data.get('bio'),
            display_name=user_data.get('display_name'),
            streak_count=user_data.get('streak_count'),
            created_at=user_data.get('created_at')
        )
    return None

def update_user_profile(user_id, username, display_name, bio, avatar_url=None):
    db = get_db()
    cursor = db.cursor()
    try:
        if avatar_url:
            query = "UPDATE users SET username=%s, display_name=%s, bio=%s, avatar_url=%s WHERE id=%s"
            cursor.execute(query, (username, display_name, bio, avatar_url, user_id))
        else:
            query = "UPDATE users SET username=%s, display_name=%s, bio=%s WHERE id=%s"
            cursor.execute(query, (username, display_name, bio, user_id))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error updating profile: {err}")
        return False
    finally:
        cursor.close()

def update_user_streak(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT streak_count, last_login_date FROM users WHERE id = %s", (user_id,))
    data = cursor.fetchone()
    
    if not data:
        cursor.close()
        return

    last_login = data['last_login_date'] 
    current_streak = data['streak_count']
    today = date.today()

    if not last_login:
        new_streak = 1
    elif last_login == today:
        cursor.close()
        return
    elif last_login == today - timedelta(days=1):
        new_streak = current_streak + 1
    else:
        new_streak = 1

    cursor.execute("UPDATE users SET streak_count = %s, last_login_date = %s WHERE id = %s", 
                   (new_streak, today, user_id))
    db.commit()
    cursor.close()
    
    return new_streak

def update_password(user_id, new_password):
    db = get_db()
    cursor = db.cursor()
    hashed = generate_password_hash(new_password)
    try:
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id))
        db.commit()
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        return False
    finally:
        cursor.close()

def delete_user(user_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        cursor.close()