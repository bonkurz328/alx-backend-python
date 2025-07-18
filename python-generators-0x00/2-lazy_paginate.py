#!/usr/bin/python3
"""
Lazy Pagination Module

This module implements paginated data fetching with lazy loading,
only retrieving the next page when needed.
"""

# Import the seed module which contains database connection utilities
# seed.py provides connect_to_prodev() for database connections
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetches a specific page of users from the database

    Args:
        page_size (int): Number of records per page
        offset (int): Starting position for the records

    Returns:
        list: A list of dictionaries representing user records
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    
    # Execute paginated query
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    
    # Clean up resources
    cursor.close()
    connection.close()
    
    return rows


def lazy_paginate(page_size):
    """
    Generator that lazily loads paginated user data

    Args:
        page_size (int): Number of records per page

    Yields:
        list: One page of user records at a time
    """
    offset = 0
    while True:
        # Fetch the next page only when needed
        page = paginate_users(page_size, offset)
        
        # Stop if no more records
        if not page:
            break
            
        yield page
        offset += page_size


if __name__ == "__main__":
    # Demonstration code
    for idx, page in enumerate(lazy_paginate(100)):
        print(f"Page {idx + 1}:")
        for user in page[:3]:  # Print first 3 users of each page
            print(user)
        if idx >= 1:  # Show only 2 pages for demo
            break
