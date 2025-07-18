#!/usr/bin/python3
"""
Memory-Efficient Age Aggregation Module

This module calculates the average age of users without loading
all ages into memory at once, using Python generators.
"""

import mysql.connector  # For MySQL database connectivity

def stream_user_ages():
    """
    Generator that streams user ages one at a time from the database

    Yields:
        int: Individual user ages as they're fetched from the database
    """
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # MySQL username
            password="",   # MySQL password
            database="ALX_prodev"
        )
        
        # Use unbuffered cursor for memory efficiency
        cursor = connection.cursor(buffered=False)
        
        # Execute query to select only age column
        cursor.execute("SELECT age FROM user_data")
        
        # Stream ages one by one
        row = cursor.fetchone()
        while row is not None:
            yield row[0]  # Yield just the age value
            row = cursor.fetchone()
            
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

def calculate_average_age():
    """
    Calculates the average age of users using generator streaming

    Returns:
        float: The average age of all users
    """
    total = 0
    count = 0
    
    # Single loop through all ages using generator
    for age in stream_user_ages():
        total += age
        count += 1
    
    # Calculate average if we have data
    return total / count if count > 0 else 0

if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age:.2f}")
