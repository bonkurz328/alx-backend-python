import asyncio
import aiosqlite
from datetime import datetime

async def async_fetch_users():
    """
    Asynchronously fetches all users from the database
    
    Returns:
        list: All user records
    """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

async def async_fetch_older_users():
    """
    Asynchronously fetches users older than 40
    
    Returns:
        list: Users older than 40
    """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            return await cursor.fetchall()

async def fetch_concurrently():
    """
    Executes both fetch operations concurrently using asyncio.gather
    
    Returns:
        tuple: Results from both queries (all_users, older_users)
    """
    start_time = datetime.now()
    print("Starting concurrent queries...")
    
    # Execute both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    print(f"Completed concurrent queries in {duration:.2f} seconds")
    return all_users, older_users

async def initialize_db():
    """Initialize the test database with sample data"""
    async with aiosqlite.connect('users.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INTEGER PRIMARY KEY, 
                          name TEXT, 
                          email TEXT,
                          age INTEGER)''')
        
        # Check if table is empty
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        count = (await cursor.fetchone())[0]
        if count == 0:
            # Insert test data
            users = [
                (1, 'Alice', 'alice@example.com', 30),
                (2, 'Bob', 'bob@example.com', 45),
                (3, 'Charlie', 'charlie@example.com', 35),
                (4, 'Diana', 'diana@example.com', 50),
                (5, 'Eve', 'eve@example.com', 25)
            ]
            await db.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users)
            await db.commit()

def print_results(all_users, older_users):
    """Prints the query results"""
    print("\nAll users:")
    for user in all_users:
        print(user)
    
    print("\nUsers older than 40:")
    for user in older_users:
        print(user)

if __name__ == "__main__":
    # Initialize database and run queries
    asyncio.run(initialize_db())
    all_users, older_users = asyncio.run(fetch_concurrently())
    print_results(all_users, older_users)
