import sqlite3
import functools
from datetime import datetime  # For timestamp in logs

def log_queries(func):
    """
    Decorator that logs SQL queries before execution
    
    Args:
        func: The function to be decorated (should execute SQL queries)
    
    Returns:
        The wrapped function with logging capability
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from kwargs or first positional argument
        query = kwargs.get('query', args[0] if args else None)
        
        # Log the query with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Executing query: {query}")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    """
    Fetches all users from the database
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        list: Results from the query execution
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example usage
if __name__ == "__main__":
    # Create test database and table if they don't exist
    conn = sqlite3.connect('users.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                   (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
    conn.commit()
    conn.close()
    
    # Fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")
    print(f"Found {len(users)} users")
