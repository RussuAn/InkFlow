from app.core.db import get_db
import mysql.connector

class Book:
    def __init__(self, id, title, author,  description, cover_image, file_path, publication_year=None, price_coins=0, page_count=0, views_count=0, created_at=None, genre=None):
        self.id = id
        self.title = title
        self.author = author
        self.publication_year = publication_year
        self.description = description
        self.cover_image = cover_image
        self.file_path = file_path
        self.price_coins = price_coins
        self.page_count = page_count
        self.views_count = views_count
        self.created_at = created_at
        self.genre = genre

def create_book(title, author, publication_year, description, cover_image, file_path, price_coins, page_count, genre):
    db = get_db()
    cursor = db.cursor()
    try:
        query = """
            INSERT INTO books (title, author, publication_year, description, cover_image, file_path, price_coins, page_count, genre)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (title, author, publication_year, description, cover_image, file_path, price_coins, page_count, genre))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error creating book: {err}")
        return False
    finally:
        cursor.close()

def get_all_books(genre=None, only_free=False):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT * FROM books WHERE 1=1"
    params = []
    
    if genre:
        query += " AND genre = %s"
        params.append(genre)
    
    if only_free:
        query += " AND price_coins = 0"
        
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, tuple(params))
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

def delete_book(book_id):
    db = get_db()
    cursor = db.cursor()
    try:
        query = "DELETE FROM books WHERE id = %s"
        cursor.execute(query, (book_id,))
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error deleting book: {err}")
        return False
    finally:
        cursor.close()