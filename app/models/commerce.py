from app.core.db import get_db
import mysql.connector

def is_book_purchased(user_id, book_id):
    db = get_db()
    cursor = db.cursor()
    query = "SELECT id FROM purchases WHERE receiver_id = %s AND book_id = %s"
    cursor.execute(query, (user_id, book_id))
    result = cursor.fetchone()
    cursor.close()
    return result is not None

def purchase_book(buyer_id, book_id, price, receiver_id=None):
    db = get_db()
    cursor = db.cursor()

    target_id = receiver_id if receiver_id else buyer_id

    is_gift = 1 if (receiver_id and receiver_id != buyer_id) else 0
    
    try:

        if is_book_purchased(target_id, book_id):
            return False, "У користувача вже є ця книга"

        cursor.execute("SELECT balance FROM users WHERE id = %s", (buyer_id,))
        balance_row = cursor.fetchone()
        
        if not balance_row:
            return False, "Користувача не знайдено"
            
        balance = balance_row[0]
        
        if balance < price:
            return False, "Недостатньо коштів на рахунку"

        new_balance = balance - price
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, buyer_id))

        query = """
            INSERT INTO purchases (buyer_id, receiver_id, book_id, price_paid, is_gift) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (buyer_id, target_id, book_id, price, is_gift))
        
        db.commit()
        
        if is_gift:
            return True, "Подарунок успішно відправлено!"
        else:
            return True, "Книгу успішно придбано!"
        
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Transaction Error: {err}")
        return False, "Помилка транзакції"
    finally:
        cursor.close()

def top_up_balance(user_id, amount):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, user_id))
        db.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        cursor.close()