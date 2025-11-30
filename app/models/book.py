from app.core.db import get_db
import mysql.connector

class Book:
    def __init__(self, id, title, author, description, cover_image, file_path, price_coins=0, views_count=0, created_at=None, genre=None):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.cover_image = cover_image
        self.file_path = file_path
        self.price_coins = price_coins
        self.views_count = views_count
        self.created_at = created_at
        self.genre = genre

def create_book(title, author, description, cover_image, file_path, price_coins, genre):
    db = get_db()
    cursor = db.cursor()
    try:
        query = """
            INSERT INTO books (title, author, description, cover_image, file_path, price_coins, genre)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (title, author, description, cover_image, file_path, price_coins, genre))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error creating book: {err}")
        return False
    finally:
        cursor.close()

def get_all_books():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books ORDER BY created_at DESC")
    books_data = cursor.fetchall()
    cursor.close()
    
    books = []
    for data in books_data:
        books.append(Book(**data))
    return books

def get_book_by_id(book_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    data = cursor.fetchone()
    cursor.close()
    
    if data:
        return Book(**data)
    return None

def search_books(query_text):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    search_pattern = f"%{query_text}%"
 
    query = """
        SELECT * FROM books 
        WHERE title LIKE %s OR author LIKE %s OR genre LIKE %s
        ORDER BY created_at DESC
    """
    cursor.execute(query, (search_pattern, search_pattern, search_pattern))
    books_data = cursor.fetchall()
    cursor.close()
    
    books = []
    for data in books_data:
        books.append(Book(**data))
    return books