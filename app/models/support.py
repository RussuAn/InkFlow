import mysql.connector

from app.core.db import get_db


def create_message(user_id, subject, message):
    db = get_db()
    cursor = db.cursor()
    try:
        query = """
            INSERT INTO support_messages (user_id, subject, message)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_id, subject, message))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error sending message: {err}")
        return False
    finally:
        cursor.close()