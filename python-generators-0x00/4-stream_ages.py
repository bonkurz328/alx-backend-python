def stream_user_ages():
    """
    Simulates streaming of user ages from a large dataset.
    Replace the list below with a data source (e.g., file or DB cursor) for real use.
    """
    user_ages = [25, 30, 35, 40, 29, 22, 31, 50]  # Simulated large dataset
    for age in user_ages:
        yield age

def calculate_average_age():
    total_age = 0
    count = 0

    for age in stream_user_ages():
        total_age += age
        count += 1

    if count == 0:
        print("No users to calculate average age.")
    else:
        average = total_age / count
        print(f"Average age of users: {average:.2f}")

# Run the script
calculate_average_age()

