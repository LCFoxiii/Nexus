import sqlite3

import discord

from .env_setup import OWNER_ID

# --------------------------------------- #
#            NexusDB contents             #
# --------------------------------------- #
# users:                                  #
# - user_id (int (primary key))           #
# - level (int)                           #
# - xp (int)                              #
# - rank (int)                            #
# - password_hash (text (255 chars))      #
# - remember_login (boolean)              #
# --------------------------------------- #
# rank system:                            #
# - 0 = normal user                       #
# - 1 = VIP user                          #
# - 2 = blacklisted user                  #
# etc.                                    #
# --------------------------------------- #

online_users: set[int] = set()
connection = sqlite3.connect("nexus.db")
cursor = connection.cursor()

TABLE_NAME = "users"

print("ATTEMPT: Initializing ranks...")
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
        remember_login BOOLEAN DEFAULT FALSE
    )
"""
)
print(f"SUCCESS: Table {TABLE_NAME} created or already exists.")

print("ATTEMPT: Attempting migration check...")
cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
table_columns = {row[1] for row in cursor.fetchall()}

print("ATTEMPT: Migrating database schema to version 1...")
if "remember_login" not in table_columns:
    cursor.execute(
        f"ALTER TABLE {TABLE_NAME} ADD COLUMN remember_login BOOLEAN DEFAULT FALSE"
    )
if "created_at" in table_columns:
    cursor.execute(
        f"ALTER TABLE {TABLE_NAME} DROP COLUMN created_at"
    )
connection.commit()
print("SUCCESS: Migration check complete.")

print("ATTEMPT: Putting all users with remember_login = TRUE into the online_users set...")
cursor.execute(
    f"SELECT user_id FROM {TABLE_NAME} WHERE remember_login = TRUE"
)
ids = cursor.fetchall()
for id_tuple in ids:
    online_users.add(id_tuple[0])
print(f"SUCCESS: {len(online_users)} users used remember_login = TRUE and are now in the online_users set.")


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
    cursor.execute(
        f"SELECT level, xp FROM {TABLE_NAME} WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    return result[0], result[1]


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
