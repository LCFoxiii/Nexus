from core.init_discord import *
from core.env_setup import *
from core.db_init import *
from core.embeds_helper import *
from nexus_commands import *

@bot.event
async def on_ready():
    print(f"SUCCESS: {bot.user} has been connected.")

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    # initialize for message level thingy
    user_id = message.author.id

    print(f"LOG: {message.author.name} talked. ID: {user_id}. Message: {message.content}")

    # check if user_id exists in logged_users table, if not, ignore the message and return.
    if user_id not in online_users:
        return

    # grab the xp and level from the database 
    result = FetchLevelAndXP(user_id)
    xp    = result[1]
    level = result[0]

    # just to be safe.
    if level < 0:
        level = 0

    # this whole system is basically is just a glorified message counter.
    # but it works, and i wanna level up my coding skills, so here we are.
    xp += 1

    if xp >= xp_required[level] and level < 100:
        level += 1
        xp = 0  # reset xp after leveling up
        await message.channel.send(f"Congratulations {message.author.mention}, you've leveled up to level {level}!")
        print(f"LOG: User {message.author.name} leveled up to level {level}.")

    # update the database with the new xp and level
    cursor.execute(
        f"UPDATE {TABLE_NAME} SET level = ?, xp = ? WHERE user_id = ?",
        (level, xp, user_id)
    )

    connection.commit()

    print(f"LOG: User {message.author.name} talked. Level: {level}, XP: {xp}/{xp_required[level]}.")

print("ATTEMPT: Running the bot...")
bot.run(TOKEN)

print("ATTEMPT: Closing the database connection...")
connection.close()
print("SUCCESS: Database connection closed.")
print("Thank you for using the bot! Have a great day!")