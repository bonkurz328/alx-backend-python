import sqlite3

class ExecuteQuery:
    """
    A reusable context manager for executing parameterized database queries.
    
    Handles both connection management and query execution automatically.
    """
    
    def __init__(self, query, params=None, db_name='users.db'):
        """
        Initialize the context manager with query and parameters.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Parameters for the query
            db_name (str): Database file name/path
        """
        self.query = query
        self.params = params if params is not None else ()
        self.db_name = db_name
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        """
        Enter the runtime context, execute the query, and return results.
        
        Returns:
            list: Query results as rows
        """
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context and clean up resources.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        # Don't suppress any exceptions
        return False

# Example usage
if __name__ == "__main__":
    # Initialize test database
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, 
                       name TEXT, 
                       email TEXT,
                       age INTEGER)''')
        if not conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com', 30)")
            conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com', 22)")
            conn.execute("INSERT INTO users VALUES (3, 'Charlie', 'charlie@example.com', 35)")
            conn.commit()
    
    # Execute query using our context manager
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    
    print("Users over 25:")
    with ExecuteQuery(query, params) as results:
        for row in results:
            print(row)
