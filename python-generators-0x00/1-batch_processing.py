#!/usr/bin/python3
"""
Batch Processing Module

This module provides generator functions to:
1. Stream users in batches from the database
2. Process batches to filter users over age 25
"""

import mysql.connector

def stream_users_in_batches(batch_size):
    """
    Generator that fetches users from database in batches

    Args:
        batch_size (int): Number of records to fetch per batch

    Yields:
        list: A batch of user records (each as a dictionary)
    """
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Execute query to select all users
        cursor.execute("SELECT * FROM user_data")
        
        while True:
            # Fetch batch of records
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
            
    except mysql.connector.Error as err:
        print(f"Database error occurred: {err}")
        raise
    finally:
        # Clean up resources
        try:
            cursor.close()
            connection.close()
        except:
            pass

def batch_processing(batch_size):
    """
    Processes batches of users and filters those over age 25

    Args:
        batch_size (int): Number of records to process per batch

    Yields:
        dict: Individual user records (as dicts) where age > 25
    """
    # Outer loop: process each batch
    for batch in stream_users_in_batches(batch_size):
        # Inner loop: process each user in batch
        for user in batch:
            if user['age'] > 25:
                yield user

if __name__ == "__main__":
    # Demonstration code
    for idx, user in enumerate(batch_processing(50)):
        print(user)
        if idx >= 4:  # Print first 5 for demo
            break
