import time
import sqlite3
import functools
import hashlib  # For creating cache keys
from datetime import datetime, timedelta  # For cache expiration

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

# Global query cache with expiration capability
query_cache = {}

def cache_query(func):
    """
    Decorator that caches database query results based on the query string
    
    Cache features:
    - Uses query string as cache key (hashed for security)
    - Includes automatic cache expiration (default 5 minutes)
    - Handles both positional and keyword arguments
    - Can be disabled with cache=False parameter
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from args or kwargs
        query = kwargs.get('query', args[0] if args else None)
        
        # Check if caching is disabled
        use_cache = kwargs.pop('cache', True)
        if not use_cache or not query:
            return func(*args, **kwargs)
        
        # Create a cache key by hashing the query
        cache_key = hashlib.sha256(query.encode()).hexdigest()
        
        # Check cache for valid entry
        if cache_key in query_cache:
            cached_time, cached_result = query_cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=5):  # 5 min expiry
                print("Returning cached results")
                return cached_result
            else:
                del query_cache[cache_key]  # Remove expired cache
        
        # Execute query and cache results
        result = func(*args, **kwargs)
        query_cache[cache_key] = (datetime.now(), result)
        print("Caching new results")
        return result
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetches users from database with query caching
    
    Args:
        conn (sqlite3.Connection): Database connection
        query (str): SQL query to execute
        
    Returns:
        list: Query results
    """
    cursor = conn.cursor()
    cursor.execute(query)
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
    
    # First call - caches results
    print("First call:")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Fetched {len(users)} users")
    
    # Second call - uses cached results
    print("\nSecond call:")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Fetched {len(users_again)} users (cached)")
    
    # Force fresh query
    print("\nThird call (forced fresh):")
    fresh_users = fetch_users_with_cache(query="SELECT * FROM users", cache=False)
    print(f"Fetched {len(fresh_users)} users (fresh query)")
