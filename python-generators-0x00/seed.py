#!/usr/bin/python3
"""
Database Seeding Module for ALX_prodev Project

This module handles the setup and population of the MySQL database
with user data for the Python generators project.
"""

import csv
import uuid
import mysql.connector
from mysql.connector import errorcode


def connect_db():
    """
    Connects to the MySQL database server.

    Returns:
        mysql.connector.connection.MySQLConnection: A connection object
        to the MySQL server or None if connection fails.

    Raises:
        mysql.connector.Error: If connection to MySQL server fails.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username if different
            password=""   # Replace with your MySQL password if set
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None


def create_database(connection):
    """
    Creates the ALX_prodev database if it doesn't exist.

    Args:
        connection (mysql.connector.connection.MySQLConnection): Active
            MySQL server connection.

    Returns:
        None
    """
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created successfully")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
    finally:
        cursor.close()


def connect_to_prodev():
    """
    Connects directly to the ALX_prodev database in MySQL.

    Returns:
        mysql.connector.connection.MySQLConnection: A connection object
        to the ALX_prodev database or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username if different
            password="",   # Replace with your MySQL password if set
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev database: {err}")
        return None


def create_table(connection):
    """
    Creates the user_data table with required fields if it doesn't exist.

    Args:
        connection (mysql.connector.connection.MySQLConnection): Active
            MySQL connection to ALX_prodev database.

    Returns:
        None
    """
    cursor = connection.cursor()
    table_description = (
        "CREATE TABLE IF NOT EXISTS user_data ("
        "  user_id CHAR(36) PRIMARY KEY,"
        "  name VARCHAR(255) NOT NULL,"
        "  email VARCHAR(255) NOT NULL,"
        "  age DECIMAL(10,0) NOT NULL,"
        "  INDEX (user_id)"
        ")")
    try:
        cursor.execute(table_description)
        print("Table user_data created successfully")
    except mysql.connector.Error as err:
        print(f"Failed creating table: {err}")
    finally:
        cursor.close()


def insert_data(connection, filename):
    """
    Inserts data from CSV file into user_data table if records don't exist.

    Args:
        connection (mysql.connector.connection.MySQLConnection): Active
            MySQL connection to ALX_prodev database.
        filename (str): Path to CSV file containing user data.

    Returns:
        None
    """
    cursor = connection.cursor()
    try:
        with open(filename, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                # Check if user already exists
                cursor.execute(
                    "SELECT user_id FROM user_data WHERE user_id = %s",
                    (row['user_id'],)
                )
                result = cursor.fetchone()
                
                if not result:
                    # Insert new user
                    cursor.execute(
                        "INSERT INTO user_data (user_id, name, email, age) "
                        "VALUES (%s, %s, %s, %s)",
                        (row['user_id'], row['name'], row['email'], int(row['age']))
                    )
        
        connection.commit()
        print(f"Data from {filename} inserted successfully")
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
    except mysql.connector.Error as err:
        print(f"Failed to insert data: {err}")
        connection.rollback()
    finally:
        cursor.close()


if __name__ == "__main__":
    # For testing the module directly
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close()
        
        conn = connect_to_prodev()
        if conn:
            create_table(conn)
            insert_data(conn, 'user_data.csv')
            conn.close()
