from cryptography.fernet import Fernet
import uuid

# Test encryption and decryption
key = "YOIL3nPbCj7_EUzgjA9mu7s0ks3yWxXJNPWYpJOAIdM="  # Replace with the key you're using
cipher_suite = Fernet(key)

# Encrypt session ID
session_id = str(uuid.uuid4())
encrypted_session_id = cipher_suite.encrypt(session_id.encode()).decode()
print("Encrypted session ID:", encrypted_session_id)

# Decrypt session ID
decrypted_session_id = cipher_suite.decrypt(encrypted_session_id.encode()).decode()
print("Decrypted session ID:", decrypted_session_id)
