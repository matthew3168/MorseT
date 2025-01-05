import secrets

# Generate a random 32-byte secret key
secret_key = secrets.token_hex(32)

# You could save the secret key to an .env file here, e.g.
with open('.env', 'w') as env_file:
    env_file.write(f"FLASK_SECRET_KEY={secret_key}")
