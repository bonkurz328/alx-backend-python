import sqlite3

class DatabaseConnection:
    """
    A context manager for handling database connections automatically.
    
    This class ensures proper opening and closing of database connections
    using Python's context manager protocol (__enter__ and __exit__ methods).
    """
    
    def __init__(self, db_name='users.db'):
        """
        Initialize the context manager with a database name.
        
        Args:
            db_name (str): Name/path of the SQLite database file
        """
        self.db_name = db_name
        self.conn = None
    
    def __enter__(self):
        """
        Enter the runtime context and return the database connection.
        
        Returns:
            sqlite3.Connection: An active database connection
        """
        self.conn = sqlite3.connect(self.db_name)
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context and close the database connection.
        
        Args:
            exc_type: Exception type if any occurred
            exc_val: Exception value if any occurred
            exc_tb: Exception traceback if any occurred
        """
        if self.conn:
            self.conn.close()
        # Return False to propagate any exceptions
        return False

# Example usage
if __name__ == "__main__":
    # Initialize test database
    with DatabaseConnection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                       (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
        if not conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
            conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
            conn.commit()
    
    # Perform query using the context manager
    print("Querying users:")
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            print(row)
