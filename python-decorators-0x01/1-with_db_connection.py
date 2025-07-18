import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles database connection lifecycle
    
    Opens a connection before function execution, passes it to the function,
    and ensures the connection is closed afterward.
    
    Args:
        func: The function to be decorated (should accept a connection parameter)
    
    Returns:
        The wrapped function with automatic connection handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Establish database connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass the connection as first argument if not already provided
            if 'conn' not in kwargs and not (args and isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            
            # Execute the function
            result = func(*args, **kwargs)
            return result
        finally:
            # Ensure connection is always closed
            conn.close()
    
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Retrieves a user by their ID from the database
    
    Args:
        conn (sqlite3.Connection): Active database connection
        user_id (int): The ID of the user to retrieve
    
    Returns:
        tuple: The user record or None if not found
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Example usage
if __name__ == "__main__":
    # Create test database and table if they don't exist
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                       (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
        # Insert test data if empty
        if not conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            conn.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')")
            conn.execute("INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com')")
            conn.commit()

    # Fetch user by ID with automatic connection handling
    user = get_user_by_id(user_id=1)
    print(user)  # Output: (1, 'Alice', 'alice@example.com')
