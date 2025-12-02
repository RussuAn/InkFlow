import mysql.connector

from app.core.db import get_db


def is_book_purchased(user_id, book_id):
    db = get_db()
    cursor = db.cursor()
    try:
        query = "SELECT id FROM purchases WHERE receiver_id = %s AND book_id = %s"
        cursor.execute(query, (user_id, book_id))
        result = cursor.fetchone()
        return result is not None
    finally:
        cursor.close()


def purchase_book(buyer_id, book_id, price, receiver_id = None):
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
            
        current_balance = balance_row[0]
        
        if current_balance < price:
            return False, "Недостатньо коштів на рахунку"

        new_balance = current_balance - price
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, buyer_id))

        query = """
            INSERT INTO purchases (buyer_id, receiver_id, book_id, price_paid, is_gift) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (buyer_id, target_id, book_id, price, is_gift))

        db.commit()
        
        success_msg = "Подарунок успішно відправлено!" if is_gift else "Книгу успішно придбано!"
        return True, success_msg
        
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
        query = "UPDATE users SET balance = balance + %s WHERE id = %s"
        cursor.execute(query, (amount, user_id))
        db.commit()
        return True
    except Exception as e:
        print(f"Error topping up balance: {e}")
        return False
    finally:
        cursor.close()