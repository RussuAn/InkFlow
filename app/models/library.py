from app.core.db import get_db
import mysql.connector

from app.models.book import Book

def add_to_shelf(user_id, book_id, status):
    db = get_db()
    cursor = db.cursor()
    
    try:
        query = """
            INSERT INTO library_items (user_id, book_id, status)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE status = %s
        """
        cursor.execute(query, (user_id, book_id, status, status))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Library Error: {err}")
        return False
    finally:
        cursor.close()

def get_user_book_status(user_id, book_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT status FROM library_items WHERE user_id = %s AND book_id = %s"
    cursor.execute(query, (user_id, book_id))
    result = cursor.fetchone()
    cursor.close()
    
    if result:
        return result['status']
    return None

def get_books_by_shelf(user_id, status):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT b.* FROM books b
        JOIN library_items li ON b.id = li.book_id
        WHERE li.user_id = %s AND li.status = %s
        ORDER BY li.added_at DESC
    """
    cursor.execute(query, (user_id, status))
    books_data = cursor.fetchall()
    cursor.close()
    
    books = []
    for data in books_data:
        books.append(Book(**data))
    return books