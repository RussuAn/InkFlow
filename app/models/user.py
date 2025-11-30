from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.db import get_db
import mysql.connector

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, role='user', avatar_url=None, balance=0, bio=None, display_name=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.avatar_url = avatar_url
        self.balance = balance
        self.bio = bio
        self.display_name = display_name or username

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
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (username, email, hashed_password))
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
    
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
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
            display_name=user_data.get('display_name')
        )
    return None

def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
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
            display_name=user_data.get('display_name')
        )
    return None

def get_user_by_username(username):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
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
            display_name=user_data.get('display_name')
        )
    return None


def update_user_profile(user_id, username, display_name, bio, avatar_url=None):
    db = get_db()
    cursor = db.cursor()
    
    try:
        if avatar_url:
            query = """
                UPDATE users 
                SET username = %s, display_name = %s, bio = %s, avatar_url = %s 
                WHERE id = %s
            """
            cursor.execute(query, (username, display_name, bio, avatar_url, user_id))
        else:
            query = """
                UPDATE users 
                SET username = %s, display_name = %s, bio = %s 
                WHERE id = %s
            """
            cursor.execute(query, (username, display_name, bio, user_id))
            
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error updating profile: {err}")
        return False
    finally:
        cursor.close()

def update_password(user_id, new_password):
    db = get_db()
    cursor = db.cursor()
    hashed = generate_password_hash(new_password)
    try:
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, user_id))
        db.commit()
        return True
    except Exception as e:
        print(e)
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
        print(e)
        return False
    finally:
        cursor.close()