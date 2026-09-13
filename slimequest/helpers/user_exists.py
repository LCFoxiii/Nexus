from ..init.database.creation import *
import discord

def SQUserExists(user_id: int) -> bool:
    sq_cursor.execute(
        f"SELECT * FROM {TABLE_USERS} WHERE id = ?",
        (user_id,)
    )
    result = sq_cursor.fetchone()
    return result is not None

async def SQUserExistsMessage(ctx: discord.ApplicationContext) -> bool:
    user_id = ctx.author.id
    if not SQUserExists(user_id):
        await ctx.respond(f"ERROR: User {ctx.author.name} does not exist in the database. Please use \"/slimequest register\" to register yourself.", ephemeral=True)
        print(f"LOG: User {ctx.author.name} attempted to use a SlimeQuest command but does not exist in the database.")
        return True
    return False