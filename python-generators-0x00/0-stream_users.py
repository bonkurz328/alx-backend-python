#!/usr/bin/python3
"""
User Data Streaming Module

This module provides a generator function to stream user data from the database
one row at a time, using Python's yield keyword for memory efficiency.
"""

import mysql.connector


def stream_users():
    """
    Generator function that streams rows from user_data table one by one.

    Yields:
        dict: A dictionary representing a single user record with keys:
              - user_id: UUID string
              - name: Full name string
              - email: Email address string
              - age: Integer age

    Raises:
        mysql.connector.Error: If database connection or query fails.
    """
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username if different
            password="",  # Replace with your MySQL password if set
            database="ALX_prodev"
        )
        
        # Use a buffered cursor to fetch rows one by one
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        # Execute query to select all users
        cursor.execute("SELECT * FROM user_data")
        
        # Stream rows one by one using yield
        row = cursor.fetchone()
        while row is not None:
            yield row
            row = cursor.fetchone()
            
    except mysql.connector.Error as err:
        print(f"Database error occurred: {err}")
        raise
    finally:
        # Clean up resources when generator is exhausted
        try:
            cursor.close()
            connection.close()
        except:
            pass


if __name__ == "__main__":
    # Demonstration of the generator
    for idx, user in enumerate(stream_users()):
        print(user)
        if idx >= 5:  # Print only first 6 rows for demo
            break
