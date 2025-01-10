from cryptography.fernet import Fernet
import os

# this file is just for generating .env secret keys

# Generate a valid 32-byte Fernet key
session_secret_key = Fernet.generate_key().decode()  # The key is already base64-encoded and valid

# Open the .env file to append the session secret key
with open('.env', 'a') as env_file:
    env_file.write(f"\nSESSION_SECRET_KEY={session_secret_key}")  # Append the session secret key

print("Session secret key saved to .env")
