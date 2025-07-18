import time
import sqlite3
import functools
from random import random  # For simulating transient errors

# Reusing our connection decorator from previous tasks
def with_db_connection(func):
    """Decorator that handles database connection lifecycle"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            if 'conn' not in kwargs and not (args and isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            return func(*args, **kwargs)
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a function on failure with exponential backoff
    
    Args:
        retries (int): Maximum number of retry attempts
        delay (float): Initial delay between retries in seconds
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(retries + 1):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)
                except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                    last_exception = e
                    if attempt == retries:  # Don't sleep on last attempt
                        break
                    # Exponential backoff with jitter
                    sleep_time = current_delay * (2 ** attempt) * (0.5 + random())
                    print(f"Attempt {attempt + 1} failed. Retrying in {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
            
            print(f"All {retries} retry attempts failed")
            raise last_exception
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    Fetches all users from the database with automatic retry on failure
    
    Simulates transient errors 50% of the time for demonstration
    """
    if random() > 0.5:  # 50% chance of failure for demo purposes
        raise sqlite3.OperationalError("Simulated database connection error")
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Example usage
if __name__ == "__main__":
    # Initialize test database
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                       (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
        if not conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
            conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
            conn.commit()
    
    # Attempt to fetch users with automatic retry
    try:
        users = fetch_users_with_retry()
        print("Successfully fetched users:")
        for user in users:
            print(user)
    except Exception as e:
        print(f"Final error after retries: {e}")
