import dotenv as env
from dotenv import *
import sys

print(f"ATTEMPT: Loading .env file...")
if(not env.load_dotenv()):
    sys.exit("ERROR: trouble loading .env file")
print(f"SUCCESS: .env file loaded successfully.")

PATH     = ".env"
TOKEN    = env.get_key(PATH, "TOKEN")
OWNER_ID = int(env.get_key(PATH, "OWNER_ID"))