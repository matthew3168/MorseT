import os
from database_handler2 import MorseDBHandler

def test_database():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create database path
    db_path = os.path.join(current_dir, 'SQLite Database', 'morse_decoder.db')
    
    # Initialize database handler
    db = MorseDBHandler(db_path)
    
    # Test connection
    if not db.test_connection():
        print("Database connection failed!")
        return
    
    # Test message saving
    test_vessel_sender = "RFA ROYALIST"
    test_vessel_recipient = "PACIFIC EXPRESS 7"
    test_message_received = ""
    test_message_sent = "POSITION UPDATE: LAT 9.2345 S, LONG 148.3456 E. ACKNOWLEDGED. NAVIGATING TO SHIPWRECK SITE." 
    
    # Save message with the new parameters
    if db.save_message(test_vessel_sender, test_vessel_recipient, test_message_received, test_message_sent):
        print("Message saved successfully!")
    else:
        print("Failed to save message!")
    
    # Test message retrieval
    messages = db.get_messages(test_vessel_sender, test_vessel_recipient)
    if messages:
        print("\nRetrieved Messages:")
        for msg in messages:
            print(f"ID: {msg['id']}")
            print(f"Vessel Sender: {msg['vessel_sender']}")
            print(f"Vessel Recipient: {msg['vessel_recipient']}")
            print(f"Message Received: {msg['message_received']}")
            print(f"Message Sent: {msg['message_sent']}")
            print(f"Timestamp: {msg['timestamp']}\n")
    else:
        print("No messages found!")

if __name__ == "__main__":
    test_database()
