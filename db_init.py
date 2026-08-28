import sqlite3
import discord
from discord.ext import *
import dotenv as env
from env_setup import *

# --------------------------------------- #
#            NexusDB contents             #
# --------------------------------------- #
# users:                                  #
# - user_id (int (primary key))           #
# - level (int)                           #
# - xp (int)                              #
# - rank (int)                            #
# - password_hash (text (255 chars))      #
# - created_at (timestamp)                #
# db_version:                             #
# - version (int)                         #
# --------------------------------------- #
# rank system:                            #
# - 0 = normal user                       #
# - 1 = VIP user                          #
# - 2 = blacklisted user                  #
# etc.                                    #
# --------------------------------------- #

# storing user ids is i think the best way to do this
# since i think i can get the name and discriminator from the user id using this library.

online_users: set[int] = set()
connection = sqlite3.connect("nexus.db")
cursor = connection.cursor()

TABLE_NAME = "users"
VERSION_TABLE_NAME = "db_version"

# 👀 sneak peek?
GAME_TABLE_NAME = "slimequest"

print(f"ATTEMPT: Initializing ranks...")
ranks = ["normal", "vip", "blacklisted"]
ranks_dict = {rank: i for i, rank in enumerate(ranks)}
print(f"SUCCESS: Ranks initialized. {ranks_dict}")


print(f"ATTEMPT: Creating table {TABLE_NAME} if it does not exist...")
connection.execute(
    f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        user_id INTEGER PRIMARY KEY,
        level INTEGER DEFAULT {ranks_dict['normal']},
        xp INTEGER DEFAULT 0,
        rank INTEGER DEFAULT 0,
        password_hash VARCHAR(255) DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)
print(f"SUCCESS: Table {TABLE_NAME} created or already exists.")

print(f"ATTEMPT: Creating table {VERSION_TABLE_NAME} if it does not exist...")
connection.execute(
    f"""
    CREATE TABLE IF NOT EXISTS {VERSION_TABLE_NAME} (
        version INTEGER DEFAULT 0
    )
"""
)
print(f"SUCCESS: Table {VERSION_TABLE_NAME} created or already exists.")


print("ATTEMPT: Attempting migration check...")
cursor.execute(
    "SELECT version FROM db_version"
)

version_result = cursor.fetchone()
version = version_result[0]

# TODO: add migration logic here whenever I need to update the database schema in the future.
print(f"SUCCESS: Migration check complete. Current version: {version}")



def IsOwner(ctx: discord.ApplicationContext) -> bool:
    return ctx.author.id == OWNER_ID

def IsIDVIP(user_id: int) -> bool:
    cursor.execute(
        f"SELECT * FROM {TABLE_NAME} WHERE user_id = ? AND rank = {ranks_dict['vip']}",
        (user_id,)
    )
    result = cursor.fetchone()
    return result is not None

def IsAuthorVIP(ctx: discord.ApplicationContext) -> bool:
    user_id = ctx.author.id
    return IsIDVIP(user_id)

def GrantIDVIP(user_id: int) -> None:
    cursor.execute(
        f"UPDATE {TABLE_NAME} SET rank = {ranks_dict['vip']} WHERE user_id = ?",
        (user_id,)
    )

    connection.commit()

def RevokeIDVIP(user_id: int) -> None:
    cursor.execute(
        f"UPDATE {TABLE_NAME} SET rank = {ranks_dict['normal']} WHERE user_id = ?",
        (user_id,)
    )

def FetchLevelAndXP(user_id: int) -> tuple[int, int]:
    # grab the xp and level from the database
    cursor.execute(
        f"SELECT level, xp FROM {TABLE_NAME} WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    return result[0], result[1]  # level, xp

def IsIDBlacklisted(user_id: int) -> bool:
    cursor.execute(
        f"SELECT * FROM {TABLE_NAME} WHERE user_id = ? AND rank = {ranks_dict['blacklisted']}",
        (user_id,)
    )
    result = cursor.fetchone()
    return result is not None

async def BasicIsNotOwnerMessage(ctx: discord.ApplicationContext) -> bool:
    if not IsOwner(ctx):
        await ctx.respond("ERROR: You are NOT the owner!", ephemeral=True)
        print(f"LOG: User {ctx.author.name} attempted to use an owner command without being the owner.")
        return True
    return False

async def BasicIsNotVIPMessage(ctx: discord.ApplicationContext) -> bool:
    if not IsAuthorVIP(ctx):
        await ctx.respond("ERROR: You are NOT a VIP!", ephemeral=True)
        print(f"LOG: User {ctx.author.name} attempted to use a VIP command without being a VIP.")
        return True
    return False

async def BasicIsBlacklistedMessage(ctx: discord.ApplicationContext) -> bool:
    if IsIDBlacklisted(ctx.author.id):
        await ctx.respond("ERROR: Womp womp, you're not able to use the bot now.", ephemeral=True)
        return True
    return False

async def BasicIsNotLoggedInMessage(ctx: discord.ApplicationContext) -> bool:
    if ctx.author.id not in online_users:
        await ctx.respond("ERROR: You are NOT logged in!", ephemeral=True)
        print(f"LOG: User {ctx.author.name} attempted to use a command without being logged in.")
        return True
    return False

def IsIDExists(user_id: int) -> bool:
    cursor.execute(
        f"SELECT * FROM {TABLE_NAME} WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    return result is not None

async def BasicIsIDExistsMessage(bot: discord.Bot, ctx: discord.ApplicationContext, user_id: int) -> bool:
    if not IsIDExists(user_id):
        user = bot.get_user(user_id) or await bot.fetch_user(user_id)
        await ctx.respond(f"ERROR: User {user.name} does NOT exist in the system!", ephemeral=True)
        print(f"LOG: User {ctx.author.name} attempted to check rank of unregistered user with ID {user_id}.")
        return True
    return False