from core.init_discord import *
from ..helpers.user_exists import *
from ..init.lore.names import *
from ..init.users.user import *

# TODO: Fix the response.
# TODO: TODO: TODO: idk.

@slimequest.command(name="register", description="TEMP: Registers you.")
async def register(ctx: discord.ApplicationContext):
    user_id = ctx.author.id

    if user_id in sq_online_users:
        await ctx.respond(f"TEMP: ERROR: User is already online!")
        return

    if SQUserExists(user_id):
        await ctx.respond(f"TEMP: ERROR: User {ctx.author.name} already exists in the database. Please use \"/slimequest login\" to log in.", ephemeral=True)
        return

    await ctx.respond("Just so you know, if you make a mistake, you have to start over. Please be careful with your inputs.")

    while True:
        
        # Username
        await ctx.respond("Please enter a name for your character (max 32 characters):")
        user_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        un_content = user_name.content.strip()

        if len(un_content) > 32:
            await ctx.respond("ERROR: Name is too long.")
            continue

        # if user_name is already taken, ask for a new name
        result = sq_cursor.execute(
            f"SELECT * FROM {TABLE_USERS} WHERE name = ?",
            (un_content,)
        ).fetchone() is not None

        if result:
            await ctx.respond(f"ERROR: Name {un_content} is already taken.")
            continue

        # Gender
        await ctx.respond("Please enter your gender.\n 1. Male\n 2. Female\n 3. other / Non-Binary")
        gender = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        g_content = gender.content.lower()
        is_male = False
        non_binary_mode = False
        int_gender = 0

        if g_content in ["1", "male", "man", "men", "boy", "m"]:
            is_male = True
            int_gender = 0
        elif g_content in ["2", "female", "woman", "women", "girl", "f"]:
            is_male = False
            int_gender = 1
        elif g_content in ["3", "other", "non-binary", "nonbinary", "non binary", "nb", "n", "o"]:
            non_binary_mode = True
            int_gender = 2
        else:
            await ctx.respond("ERROR: Invalid gender input.")
            continue

        # Generate a random true name for lore reasons.
        true_name = GetName(is_male, non_binary_mode)

        # Insert the user into the database
        sq_cursor.execute(
            f"INSERT INTO {TABLE_USERS} (id, name, true_name, gender) VALUES (?, ?, ?, ?)",
            (user_id, user_name.content, true_name, int_gender)
        )
        
        break

    # Other stuff.
    sq_cursor.execute(
        f"INSERT INTO {TABLE_CURRENCY} (id) VALUES (?)",
        (user_id,)
    )

    sq_cursor.execute(
        f"INSERT INTO {TABLE_STATS} (id) VALUES (?)",
        (user_id,)
    )

    # Add the user to the online users set
    sq_online_users.add(user_id)

    await ctx.respond(f"Successfully registered user {user_name.content} with true name {true_name} and gender {int_gender}.")
    sq_connection.commit()