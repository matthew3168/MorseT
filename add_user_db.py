from database_handler2 import MorseDBHandler  

def add_users_to_database(db_path):
    handler = MorseDBHandler(db_path, key_file="SQLite Database/key.txt")

    # Add users
    users = [
        ("user2", "user2"),
    ]

    for username, password in users:
        if handler.create_user(username, password):  
            print(f"User {username} added successfully.")
        else:
            print(f"Failed to add user {username}.")

if __name__ == "__main__":
    db_path = "SQLite Database/morse_decoder.db"  
    add_users_to_database(db_path)
