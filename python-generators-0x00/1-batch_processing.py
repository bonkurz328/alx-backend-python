# 1-batch_processing.py

def stream_users_in_batches(batch_size):
    """
    Generator that yields users in batches of size `batch_size`
    """
    users = [
        {'id': 1, 'age': 22},
        {'id': 2, 'age': 26},
        {'id': 3, 'age': 30},
        {'id': 4, 'age': 18},
        {'id': 5, 'age': 40},
        {'id': 6, 'age': 24},
        {'id': 7, 'age': 29},
        {'id': 8, 'age': 20},
        {'id': 9, 'age': 35},
        {'id': 10, 'age': 27},
        # Add more if needed for testing
    ]

    for i in range(0, len(users), batch_size):
        yield users[i:i + batch_size]  # this is one loop

def batch_processing(batch_size):
    """
    Processes each batch and prints users over age 25
    """
    for batch in stream_users_in_batches(batch_size):  # loop 2
        for user in batch:  # loop 3
            if user['age'] > 25:
                print(f"User ID: {user['id']}, Age: {user['age']}")
