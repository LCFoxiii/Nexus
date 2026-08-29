import sys

import dotenv as env

print("ATTEMPT: Loading .env file...")
if not env.load_dotenv():
    sys.exit("ERROR: trouble loading .env file")
print("SUCCESS: .env file loaded successfully.")

PATH = ".env"
TOKEN = env.get_key(PATH, "TOKEN")
OWNER_ID = int(env.get_key(PATH, "OWNER_ID"))
