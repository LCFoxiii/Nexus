import discord
import numpy as np
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from .db_init import *
from .env_setup import *

INTENTS = discord.Intents.all()
PREFIX = "nexus!"

print("STATS:")
print(f"LOG: Token: {TOKEN}")
print(f"LOG: Owner ID: {OWNER_ID}")
print(f"LOG: Intents: {INTENTS}")
print(f"LOG: Prefix: \"{PREFIX}\"")

print("ATTEMPT: Initializing password hasher...")
password_hasher = PasswordHasher()
print("SUCCESS: Password hasher initialized.")

print("ATTEMPT: Initializing XP system...")
xp_required = [round(level ** 3 / (0.80002 * level + 1)) for level in range(101)]
print("SUCCESS: XP initialized.")

print("ATTEMPT: Initializing Discord bot...")
bot = discord.Bot(intents=INTENTS, command_prefix=PREFIX)
print("SUCCESS: Discord bot initialized.")


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


nexus = bot.create_group("nexus", "Nexus commands")
vip_exclusive = nexus.create_subgroup("vip", "VIP exclusive commands")
owner_exclusive = nexus.create_subgroup("owner", "Owner exclusive commands")

slimequest = bot.create_group("slimequest", "SlimeQuest commands")