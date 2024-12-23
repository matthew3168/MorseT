import bcrypt
import json

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# load
with open("config.json", "r") as file:
    config = json.load(file)

# update
for username, password in config.get("users", {}).items():
    config["users"][username] = hash_password(password)

# save updated config.json
with open("config.json", "w") as file:
    json.dump(config, file, indent=4)

print("Passwords hashed and saved in config.json.")
