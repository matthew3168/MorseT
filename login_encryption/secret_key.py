import secrets
import os

# generate a random 32-byte secret key
secret_key = secrets.token_hex(32)
print(f"Generated Secret Key: {secret_key}")

# export key to env variable
os.system(f"set FLASK_SECRET_KEY={secret_key}")
