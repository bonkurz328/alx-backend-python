import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles database connection lifecycle.
    Opens a connection before function execution and closes it afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            # Pass connection if not already provided
            if 'conn' not in kwargs and not (args and isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            return func(*args, **kwargs)
        finally:
            conn.close()
    return wrapper

def transactional(func):
    """
    Decorator that manages database transactions.
    Commits if function succeeds, rolls back if exception occurs.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Find the connection in args or kwargs
        conn = None
        for arg in args:
            if isinstance(arg, sqlite3.Connection):
                conn = arg
                break
        if not conn:
            conn = kwargs.get('conn')
        
        if not conn:
            raise ValueError("No database connection provided")
        
        try:
            result = func(*args, **kwargs)
            conn.commit()  # Commit if no exceptions
            return result
        except Exception as e:
            conn.rollback()  # Rollback on error
            raise e  # Re-raise the exception
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """
    Updates a user's email address with automatic transaction handling.
    
    Args:
        conn (sqlite3.Connection): Database connection
        user_id (int): ID of user to update
        new_email (str): New email address
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email = ? WHERE id = ?", 
        (new_email, user_id)
    if cursor.rowcount == 0:
        raise ValueError(f"No user found with ID {user_id}")

# Example usage
if __name__ == "__main__":
    # Initialize test database
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                       (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
        # Insert test data if empty
        if not conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
            conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
            conn.commit()
    
    # Successful update
    print("Updating email...")
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
    
    # Verify update
    with sqlite3.connect('users.db') as conn:
        email = conn.execute("SELECT email FROM users WHERE id = 1").fetchone()[0]
        print(f"New email: {email}")  # Should show the updated email
    
    # Failed update (will rollback)
    try:
        print("\nAttempting invalid update...")
        update_user_email(user_id=99, new_email='invalid@example.com')
    except ValueError as e:
        print(f"Error: {e}")  # Should show "No user found with ID 99"
