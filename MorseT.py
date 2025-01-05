from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from database_handler2 import MorseDBHandler
from static.js.design import setup_js_route
from io import StringIO
from dotenv import load_dotenv
import csv
import os
import json
from datetime import datetime
import pytz
from cryptography.fernet import Fernet
import bcrypt
import socket
from ESP32_Static_IP import IP_ADDRESS, PORT

class FlaskMorseApp:
    def __init__(self):
        load_dotenv(dotenv_path='login_encryption/.env')
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('FLASK_SECRET_KEY')
        self.app.config['SESSION_TYPE'] = 'filesystem'
        setup_js_route(self.app)
        self.db = self.initialize_database()
        self.timezone = pytz.timezone('Asia/Singapore')
        self.setup_routes()

        if self.app.secret_key is None:
            raise ValueError("secret key is not set in the environment variables!")
    
    def initialize_database(self):
        """Initialize the database connection."""
        key_file = os.path.join(os.path.dirname(__file__), "SQLite Database/key.txt")  
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, 'SQLite Database', 'morse_decoder.db')
        return MorseDBHandler(db_path, key_file)

    def send_to_esp32(self, message_data):
        """Send data to ESP32 via TCP socket."""
        try:
            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to ESP32
            server_address = (IP_ADDRESS, PORT)  
            sock.settimeout(5)  # Set timeout to 5 seconds
            sock.connect(server_address)
            
            try:
                # Send data
                message_json = json.dumps(message_data)
                sock.sendall(message_json.encode())
                return True, "Message sent successfully"
            except socket.timeout:
                return False, "Connection timed out"
            except Exception as e:
                return False, f"Error sending message: {str(e)}"
            finally:
                sock.close()
        except Exception as e:
            return False, f"Connection error: {str(e)}"
                    
    def setup_routes(self):
        """Set up all Flask routes."""
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                
                # Fetch the encrypted password from the database
                user_password_hash = self.db.get_user_password_hash(username)
                
                # Verify password using bcrypt
                if user_password_hash and bcrypt.checkpw(password.encode(), user_password_hash.encode()):
                    session['user'] = username
                    session['menu_state'] = False  # Menu state for user session
                    return redirect(url_for('index'))
                else:
                    return render_template('auth.html', error_message="Invalid credentials")
                        
            return render_template('auth.html')
        
        @self.app.route('/logout')
        def logout():
            """Handle logout functionality."""
            session.clear()
            return redirect(url_for('login'))
        
        @self.app.route('/')
        def index():
            """Main application page."""
            if 'user' not in session:
                return redirect(url_for('login'))

            messages = self.get_messages()
            vessels = self.db.get_unique_vessels()

            vessels = [vessel for vessel in vessels if vessel.lower() not in ['all', 'all channels']]
            
            vessel_messages = {}

            for vessel in vessels:
                vessel_msgs = self.db.get_messages(vessel_sender=vessel, vessel_recipient=None)
                
                if vessel_msgs:
                    vessel_msgs.sort(key=lambda x: x['timestamp'], reverse=True)
                    vessel_messages[vessel] = vessel_msgs[0]

            sorted_vessels = sorted(vessel_messages.keys(), key=lambda vessel: vessel_messages[vessel]['timestamp'], reverse=True)

            return render_template(
                'index.html',
                messages=self.format_messages(messages),
                vessels=sorted_vessels,  
                vessel_messages=vessel_messages  
            )
        
        @self.app.route('/get_messages/<vessel>')
        def get_vessel_messages(vessel):
            """Get messages for a specific vessel."""
            if 'user' not in session:
                return redirect(url_for('login'))
            
            if vessel.lower() in ['all', 'all channels']:
                return jsonify([])
                
            messages = self.db.get_messages(vessel_sender=vessel, vessel_recipient=None)
            return jsonify(self.format_messages(messages))
        
        @self.app.route('/get_messages')
        def get_all_messages():
            """Get all messages."""
            if 'user' not in session:
                return redirect(url_for('login'))
            messages = self.get_messages()
            return jsonify(self.format_messages(messages))
        
        @self.app.route('/send_message', methods=['POST'])
        def send_message():
            """
            Handle message sending - stores message in database and forwards to ESP32.
            Returns success only if both operations complete successfully.
            """
            if 'user' not in session:
                return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
            
            try:
                #print("Receiving message data...")  # Debug log
                data = request.json
                message = data.get('message')
                sender = data.get('sender')
                duration = data.get('duration', 500)  # Default duration 500ms
                repeat = data.get('repeat', 1)  # Default repeat count 1

                if not message or not sender:
                    return jsonify({'status': 'error', 'message': 'No message provided'}), 400
 
                
                # Get current timestamp
                timestamp = datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')
                
                # 1. Save to database
                db_success = self.db.save_message(
                    vessel_sender=sender,
                    vessel_recipient='All',
                    message_sent=message,
                    message_received='[No Message Received]'
                )
                
                if not db_success:
                    return jsonify({'status': 'error', 'message': 'Failed to save message to database'}), 500

                # 2. Send to ESP32
                esp32_data = {
                    'message': message,
                    'duration': int(duration),
                    'repeat': int(repeat)
                }
                
                esp32_success, esp32_status = self.send_to_esp32(esp32_data)
                
                if not esp32_success:
                    # Even if ESP32 send fails, we keep the database record but return an error
                    return jsonify({
                        'status': 'partial_success',
                        'message': f'Message saved to database but ESP32 communication failed: {esp32_status}',
                        'esp32_error': esp32_status
                    }), 500

                # Both operations successful - prepare response
                new_message = {
                    'message_sent': message,
                    'message_received': '[No Message Received]',
                    'vessel_sender': sender,
                    'vessel_recipient': 'All',
                    'timestamp': timestamp,
                    'header': f"From: {sender} To: All",
                    'formatted_time': timestamp
                }
                
                print(f"Message processed successfully: {new_message}")  # Debug log
                
                return jsonify({
                    'status': 'success',
                    'message': new_message,
                    'esp32_status': esp32_status if esp32_success else 'ESP32 communication failed'
                })
                
            except Exception as e:
                print(f"Error in send_message: {str(e)}")  # Debug log
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/toggle_menu', methods=['POST'])
        def toggle_menu():
            """Handle menu state toggling."""
            if 'user' not in session:
                return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
            
            try:
                data = request.json
                menu_state = data.get('menuOpen', False)
                session['menu_state'] = menu_state
                return jsonify({'status': 'success'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
            
        @self.app.route('/export')
        def export():
            morse_app = FlaskMorseApp()
            messages = morse_app.get_messages()
            
            #string IO to write CSV content
            si = StringIO()
            cw = csv.writer(si)
            
            #header row based on table columns
            cw.writerow(['id', 'vessel_sender', 'vessel_recipient', 'message_received', 'message_sent', 'timestamp'])
            
            #write each message
            for message in messages:
                cw.writerow([
                    message['id'], 
                    message['vessel_sender'], 
                    message['vessel_recipient'], 
                    message['message_received'], 
                    message['message_sent'], 
                    message['timestamp']
                ])
            
            #move to the beginning of the StringIO object
            si.seek(0)
            
            #use response to send the CSV file as a response
            return Response(si.getvalue(), mimetype='text/csv', headers={
                'Content-Disposition': 'attachment;filename=messages.csv'
            })
    
    def format_messages(self, messages):
        """Format messages for display."""
        formatted_messages = []
        for msg in messages:
            formatted_msg = msg.copy()
            formatted_msg['header'] = f"From: {msg['vessel_sender']} To: {msg['vessel_recipient']}"
            
            try:
                dt = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S')
                sg_dt = self.timezone.localize(dt)
                formatted_msg['formatted_time'] = sg_dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                formatted_msg['formatted_time'] = msg['timestamp']  
            formatted_messages.append(formatted_msg)
        return formatted_messages
    
    def get_messages(self):
        """Retrieve all messages from database."""
        messages = self.db.get_messages(limit=None)
        #messages.sort(key=lambda x: x['timestamp'])
        return messages
    
    def run(self, debug=True, host='0.0.0.0', port=5000):
        """Run the Flask application."""
        self.app.run(debug=debug, host=host, port=port)

if __name__ == '__main__':
    app = FlaskMorseApp()
    app.run(debug=True)
