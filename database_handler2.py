import os
import sqlite3
import logging
import bcrypt
from datetime import datetime
import pytz
from cryptography.fernet import Fernet, InvalidToken
from tabulate import tabulate  

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_decoder.log')
    ]
)
logger = logging.getLogger(__name__)

class MorseDBHandler:
    def __init__(self, db_path, key_file):
        """Initialize database handler with encryption"""
        self.db_path = os.path.abspath(os.path.normpath(db_path))
        self.db_dir = os.path.dirname(self.db_path)
        self.timezone = pytz.timezone('Asia/Singapore')
        self.logger = logger
        self.logger.info(f"Initializing database handler for path: {self.db_path}")

        # Load key.txt encryption key
        self.PREDEFINED_KEY = self._load_encryption_key(key_file)

        # Setup encryption and database
        self._setup_encryption()
        self._setup_database()

    def _load_encryption_key(self, key_file):
        """Load encryption key from a file"""
        try:
            key_path = os.path.abspath(os.path.normpath(key_file))
            self.logger.debug(f"Loading encryption key from: {key_path}")

            if key_file.endswith(".txt"):
                with open(key_path, "r") as f:
                    return f.read().strip().encode()
            else:
                raise ValueError("Unsupported key file format.")
        except Exception as e:
            self.logger.error(f"Error loading encryption key: {str(e)}")
            raise

    def _setup_encryption(self):
        try:
            self.cipher_suite = Fernet(self.PREDEFINED_KEY)
            self.logger.debug("Encryption setup completed successfully")
        except Exception as e:
            self.logger.error(f"Error setting up encryption: {str(e)}")
            raise

    def _setup_database(self):
        try:
            self.logger.debug(f"Creating database directory: {self.db_dir}")
            os.makedirs(self.db_dir, exist_ok=True)

            with sqlite3.connect(self.db_path, timeout=20) as conn:
                cursor = conn.cursor()

                # messages table
                self.logger.debug("Creating messages table if not exists")
                cursor.execute(''' 
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        vessel_sender TEXT NOT NULL,
                        vessel_recipient TEXT NOT NULL,
                        message_received TEXT,
                        message_sent TEXT,
                        timestamp DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
                    )
                ''')

                # login table
                self.logger.debug("Creating login table if not exists")
                cursor.execute(''' 
                    CREATE TABLE IF NOT EXISTS login (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                    )
                ''')

                # Commit the changes explicitly
                conn.commit()
                self.logger.info("Database setup completed successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Database setup error: {str(e)}")
            raise

    @staticmethod
    def hash_password(password):
        """Encrypt a password using bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password, hashed_password):
        """Verify a password against a hashed password."""
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    def create_user(self, username, password):
        """Create a new user with encrypted password."""
        self.logger.info(f"Creating user: {username}")
        try:
            hashed_password = self.hash_password(password)
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO login (username, password) VALUES (?, ?)
                ''', (username, hashed_password))
                conn.commit()
                self.logger.info(f"User {username} created successfully")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error creating user: {str(e)}")
            return False

    def authenticate_user(self, username, password):
        """Authenticate a user with their username and password."""
        self.logger.info(f"Authenticating user: {username}")
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT password FROM login WHERE username = ?', (username,))
                row = cursor.fetchone()
                if row and self.verify_password(password, row[0]):
                    self.logger.info(f"User {username} authenticated successfully")
                    return True
                else:
                    self.logger.warning(f"Authentication failed for user: {username}")
                    return False
        except sqlite3.Error as e:
            self.logger.error(f"Error during authentication: {str(e)}")
            return False
    
    def get_all_users(self):
        """Retrieve all users and their encrypted passwords."""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, password FROM login')
                rows = cursor.fetchall()
                
                users = []
                for row in rows:
                    id, username, hashed_password = row
                    users.append({
                        'id': id,
                        'username': username,
                        'password': hashed_password  # Do not decrypt as bcrypt is a hash, not reversible
                    })
                return users
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving users: {str(e)}")
            return []

    def encrypt_message(self, message):
        try:
            if not message:
                self.logger.warning("Attempted to encrypt empty message")
                return None
            encrypted = self.cipher_suite.encrypt(message.encode())
            self.logger.debug("Message encrypted successfully")
            return encrypted.decode()
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}")
            return None
        
    def _connect_to_db(self):
        """Establish a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        return conn
        
    def get_user_password_hash(self, username):
        conn = self._connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM login WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]  
        return None

    def get_unique_vessels(self):
        query = "SELECT DISTINCT vessel_sender FROM messages"
        result = self.execute_query(query)
        return [row[0] for row in result]  
    
    def execute_query(self, query, params=()):
        """Execute a query on the database and return the result."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute(query, params)  # Execute the query with the provided parameters
        result = cursor.fetchall()  # Fetch all results
        connection.close()  # Close the connection
        return result

    def decrypt_message(self, encrypted_message):
        try:
            if not encrypted_message:
                self.logger.warning("Attempted to decrypt empty or NULL message")
                return None
            decrypted = self.cipher_suite.decrypt(encrypted_message.encode())
            self.logger.debug("Message decrypted successfully")
            return decrypted.decode()
        except InvalidToken:
            self.logger.warning("Invalid token encountered during decryption")
            return "[Decryption Failed]"
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            return "[Decryption Error]"

    def save_message(self, vessel_sender, vessel_recipient, message_received, message_sent):
        self.logger.info(f"Attempting to save message from vessel: {vessel_sender} to {vessel_recipient}")
        if not vessel_sender or not vessel_recipient:
            self.logger.warning("Empty vessel sender or recipient provided")
            return False
        try:
            encrypted_received = self.encrypt_message(message_received.strip()) if message_received else None
            encrypted_sent = self.encrypt_message(message_sent.strip()) if message_sent else None
            
            sg_time = datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')

            with sqlite3.connect(self.db_path, timeout=20) as conn:
                cursor = conn.cursor()
                cursor.execute('BEGIN TRANSACTION')
                try:
                    cursor.execute('''
                        INSERT INTO messages (vessel_sender, vessel_recipient, message_received, message_sent, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (vessel_sender, vessel_recipient, encrypted_received, encrypted_sent, sg_time))
                    conn.commit()
                    self.logger.info(f"Message saved successfully from {vessel_sender} to {vessel_recipient}")
                    return True
                except sqlite3.Error as e:
                    conn.rollback()
                    self.logger.error(f"Database error in transaction: {str(e)}")
                    return False
        except Exception as e:
            self.logger.error(f"Error saving message: {str(e)}")
            return False

    def get_messages(self, vessel_sender=None, vessel_recipient=None, limit=None):
        self.logger.info(f"Retrieving messages for sender: {vessel_sender} and recipient: {vessel_recipient}")
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                cursor = conn.cursor()
                query = 'SELECT id, vessel_sender, vessel_recipient, message_received, message_sent, timestamp FROM messages '
                conditions = []
                params = []

                if vessel_sender:
                    conditions.append("vessel_sender = ?")
                    params.append(vessel_sender)
                if vessel_recipient:
                    conditions.append("vessel_recipient = ?")
                    params.append(vessel_recipient)

                if conditions:
                    query += "WHERE " + " AND ".join(conditions)
                query += " ORDER BY timestamp DESC"
                #params.append(limit)

                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor.execute(query, tuple(params))
                messages = []
                for row in cursor.fetchall():
                    decrypted_received = self.decrypt_message(row[3]) or "[No Message Received]"
                    decrypted_sent = self.decrypt_message(row[4]) or "[No Message Sent]"
                    messages.append({
                        'id': row[0],
                        'vessel_sender': row[1],
                        'vessel_recipient': row[2],
                        'message_received': decrypted_received,
                        'message_sent': decrypted_sent,
                        'timestamp': row[5]
                    })
                return messages
        except Exception as e:
            self.logger.error(f"Error retrieving messages: {str(e)}")
            raise

    def test_connection(self):
        """Test database connection"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                result = cursor.fetchone()[0] == 1
                self.logger.debug("Database connection test successful")
                return result
        except sqlite3.Error as e:
            self.logger.error(f"Database connection test failed: {str(e)}")
            return False

# --- Helper Functions ---
def get_database_path():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'SQLite Database', 'morse_decoder.db')
        if not os.path.exists(db_path):
            logger.error(f"Database file not found at: {db_path}")
            raise FileNotFoundError(f"Database file not found at: {db_path}")
        return db_path
    except Exception as e:
        logger.error(f"Error getting database path: {str(e)}")
        raise

def decode_messages(vessel_sender_filter=None, vessel_recipient_filter=None, key_file="key.txt"):
    db_path = get_database_path()
    db = MorseDBHandler(db_path, key_file)
    messages = db.get_messages(vessel_sender_filter, vessel_recipient_filter)
    headers = ['ID', 'Vessel Sender', 'Vessel Recipient', 'Message Received', 'Message Sent', 'Timestamp']
    rows = [
        [msg['id'], msg['vessel_sender'], msg['vessel_recipient'], msg['message_received'], msg['message_sent'], msg['timestamp']]
        for msg in messages
    ]
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def view_login(key_file="key.txt"):
        db_path = get_database_path()
        db = MorseDBHandler(db_path, key_file)
        users = db.get_all_users()
        
        headers = ['ID', 'Username', 'Encrypted Password']
        rows = [
            [user['id'], user['username'], user['password']]
            for user in users
        ]
        print(tabulate(rows, headers=headers, tablefmt='grid'))

def main():
    print("\nMorse Code Database Decoder")
    db_path = get_database_path()
    key_file = os.path.join(os.path.dirname(db_path), "key.txt")  

    while True:
        print("\n1. View all messages\n2. View login\n3. Exit")
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            decode_messages(key_file=key_file)
        elif choice == '2':
            view_login(key_file=key_file)  
        elif choice == '3':
            break

if __name__ == "__main__":
    main()
