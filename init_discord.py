import discord
from discord.ext import *
import dotenv as env
import numpy as np
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from db_init import *

INTENTS  = discord.Intents.all()
PREFIX   = "nexus!" # rare, since we're using slash commands.

print(f"STATS:")
print(f"LOG: Token: {TOKEN}")
print(f"LOG: Owner ID: {OWNER_ID}")
print(f"LOG: Intents: {INTENTS}")
print(f"LOG: Prefix: \"{PREFIX}\"")

print(f"ATTEMPT: Initializing password hasher...")
password_hasher = PasswordHasher()
print(f"SUCCESS: Password hasher initialized.")


# use the user's current level as index.
print("ATTEMPT: Initializing XP system...")
xp_required = [round(level ** 3 / (0.80002 * level + 1)) for level in range(101)]
print("SUCCESS: XP initialized.")

print(f"ATTEMPT: Initializing Discord bot...")
bot = discord.Bot(intents=INTENTS, command_prefix=PREFIX)
print(f"SUCCESS: Discord bot initialized.")

# helpers

async def GetUserFromID(user_id: int):
    user = bot.get_user(user_id) or await bot.fetch_user(user_id)
    return user
    

async def BasicIsIDNotLoggedInMessage(ctx: discord.ApplicationContext, user_id: int):
    if user_id not in online_users:
        user = await GetUserFromID(user_id)

        await ctx.respond(f"{user.name} is not logged in. Please log in first.", ephemeral=True)
        print(f"LOG: User {user.name} attempted to login but is not logged in.")
        return True
    return False

# slash command groups
nexus = bot.create_group("nexus", "Nexus commands")
vip_exclusive = nexus.create_subgroup("vip", "VIP exclusive commands")
owner_exclusive = nexus.create_subgroup("owner", "Owner exclusive commands")