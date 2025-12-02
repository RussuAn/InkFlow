import mysql.connector

from app.core.db import get_db


def add_review(user_id, book_id, rating, comment):
    db = get_db()
    cursor = db.cursor()
    try:
        query = "INSERT INTO reviews (user_id, book_id, rating, comment) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (user_id, book_id, rating, comment))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error adding review: {err}")
        return False
    finally:
        cursor.close()


def get_book_reviews(book_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT r.*, u.username, u.display_name, u.avatar_url 
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.book_id = %s
        ORDER BY r.created_at DESC
    """
    cursor.execute(query, (book_id,))
    reviews = cursor.fetchall()
    cursor.close()
    return reviews