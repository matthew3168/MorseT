import sqlite3

# use this file if you're getting "this account is already logged in on another device" 
# msg triggered when there's an existing session id associated with the user in db, can happen when someone forgets to logout
# for clearing session id 


# Path to the database file (adjust this path as needed)
db_path = 'SQLite Database/morse_decoder.db'

def clear_session(username):
    """Clear the session_id for the selected user."""
    try:
        # Connect to the SQLite database
        with sqlite3.connect(db_path, timeout=20) as conn:
            cursor = conn.cursor()

            # Update the session_id to NULL for the user
            cursor.execute('''
                UPDATE login
                SET session_id = NULL
                WHERE username = ?
            ''', (username,))

            # Commit the changes to the database
            conn.commit()

            print(f"Session ID for user '{username}' has been cleared.")
    except sqlite3.Error as e:
        print(f"Error clearing session ID: {e}")

def main():
    # Prompt for the username whose session should be cleared
    username = input("Enter the username whose session ID you want to clear: ")

    # Clear the session for the specified user
    clear_session(username)

if __name__ == '__main__':
    main()
