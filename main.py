from init_discord import *
from env_setup import *
from db_init import *
from embeds_helper import *

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

@nexus.command(name="register", description="Registers you to use the bot.")
async def register(ctx: discord.ApplicationContext, password: str):
    user_id = ctx.author.id

    print(f"LOG: User {ctx.author.name} attempted to register with password: {password}.")
    # check if user_id exists in logged_users table, if not, add it.
    if user_id not in online_users:
        online_users.add(user_id)

        password_hash = password_hasher.hash(password)

        print(f"LOG: User {ctx.author.name} registered with hash: {password_hash}.")

        cursor.execute(
            f"INSERT INTO {TABLE_NAME} (user_id, rank, level, xp, password_hash) VALUES (?, ?, ?, ?, ?)",
            (user_id, ranks_dict['normal'], 0, 0, password_hash)
        )

        connection.commit()
        await ctx.respond("You have been registered!", ephemeral=True)
    else:

        print(f"LOG: User {ctx.author.name} attempted to register but is already registered.")
        await ctx.respond("You are already able to use the bot.", ephemeral=True)

@nexus.command(name="login", description="Logs you in to use the bot.")
async def login(ctx: discord.ApplicationContext, password: str):
    user_id = ctx.author.id

    # check if user_id exists in logged_users table, if not, add it.
    if user_id not in online_users:
        online_users.add(user_id)

        cursor.execute(
            f"SELECT password_hash FROM {TABLE_NAME} WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()

        if result is None:
            await ctx.respond("You are not registered. Please register first.", ephemeral=True)

            print(f"LOG: User {ctx.author.name} attempted to log in but is not registered.")
            return

        password_hash = result[0]

        print(f"LOG: User {ctx.author.name} attempted to log in.")
        try:
            password_hasher.verify(password_hash, password)
            await ctx.respond("You have been logged in!", ephemeral=True)

            print(f"LOG: User {ctx.author.name} logged in successfully.")
        except VerifyMismatchError:
            await ctx.respond("Incorrect password. Please try again.", ephemeral=True)

            print(f"LOG: User {ctx.author.name} failed to log in due to incorrect password.")
            return

        if password_hasher.check_needs_rehash(password_hash):
            new_hash = password_hasher.hash(password)
            cursor.execute(
                f"UPDATE {TABLE_NAME} SET password_hash = ? WHERE user_id = ?",
                (new_hash, user_id)
            )

            connection.commit()

            print(f"LOG: User {ctx.author.name}'s password hash has been rehashed for security.")
    else:

        print(f"LOG: User {ctx.author.name} attempted to log in but is already logged in.")
        await ctx.respond("You are already able to use the bot.", ephemeral=True)

@nexus.command(name="logout", description="Logs you out of the bot.")
async def logout(ctx: discord.ApplicationContext):
    user_id = ctx.author.id

    # check if user_id exists in logged_users table, if so, remove it.
    if user_id in online_users:
        online_users.remove(user_id)
        await ctx.respond("You have been logged out!", ephemeral=True)

        print(f"LOG: User {ctx.author.name} logged out successfully.")
    else:

        print(f"LOG: User {ctx.author.name} attempted to log out but is not logged in.")
        await ctx.respond("You are not logged in.", ephemeral=True)

@nexus.command(name="random-number", description="Generates a random number.")
async def random_number(ctx: discord.ApplicationContext, min_value: int, max_value: int):
    if await BasicIsNotLoggedInMessage(ctx) or await BasicIsBlacklistedMessage(ctx):
        return

    if min_value >= max_value:
        await ctx.respond("Error: Minimum value must be less than maximum value.", ephemeral=True)
        return
    
    number: int = secrets.randbelow(max_value - min_value + 1) + min_value

    print(f"LOG: User {ctx.author.name} generated a random number between {min_value} and {max_value}. Result: {number}.")
    await ctx.respond(f"Random number: {number}")

@nexus.command(name="level", description="Checks your level and XP.")
async def level(ctx: discord.ApplicationContext):
    user_id = ctx.author.id

    if await BasicIsNotLoggedInMessage(ctx) or await BasicIsBlacklistedMessage(ctx):
        return

    # grab the xp and level from the database
    cursor.execute(
        "SELECT level, xp FROM user_levels WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()

    if result is None:
        await ctx.respond("You have no level or XP yet. Start chatting to gain XP!", ephemeral=True)
        return

    level = result[0]
    xp = result[1]
    xp_needed = xp_required[level]

    print(f"LOG: User {ctx.author.name} checked their level and XP. Level: {level}, XP: {xp}/{xp_needed}.")
    await ctx.respond(
        f"Your level: {level}\n"
        f"Your XP: {xp}/{xp_needed}\n"
        f"Your total XP: {sum(xp_required[:level]) + xp}\n"
        f"XP needed for next level: {xp_needed - xp}",
        ephemeral=True
    )

@nexus.command(name="id", description="Checks your discord ID")
async def id_(ctx: discord.ApplicationContext):
    await ctx.respond(f"Your ID is: {ctx.author.id}")

@owner_exclusive.command(name="grant", description="Grant a user VIP.")
async def grant(ctx: discord.ApplicationContext, target: discord.Member):
    if await BasicIsNotOwnerMessage(ctx):
        return

    mention = target.mention
    user_id = target.id

    # add the user to the granted list (nexus.db)
    GrantIDVIP(user_id)

    print(f"LOG: Owner granted VIP to user {target.name} (ID: {user_id}).")
    await ctx.respond(f"Granted {mention} cool stuff!", ephemeral=True)

@owner_exclusive.command(name="revoke", description="Revokes a user from being a VIP.")
async def revoke(ctx: discord.ApplicationContext, target: discord.Member):
    if await BasicIsNotOwnerMessage(ctx):
        return

    mention = target.mention
    user_id = target.id

    # remove the user from the granted list (nexus.db)
    RevokeIDVIP(user_id)

    print(f"LOG: Owner revoked VIP from user {target.name} (ID: {user_id}).")
    await ctx.respond(f"Ungranted {mention} from cool stuff!", ephemeral=True)

@owner_exclusive.command(name="blacklist", description="Blacklists a user.")
async def blacklist(ctx: discord.ApplicationContext, target: discord.Member):
    if await BasicIsNotOwnerMessage(ctx):
        return

    mention = target.mention
    user_id = target.id

    # add the user to the blacklist (nexus.db)
    cursor.execute(
        f"UPDATE {TABLE_NAME} SET rank = {ranks_dict['blacklisted']} WHERE user_id = ?",
        (user_id,)
    )

    connection.commit()

    print(f"LOG: Owner blacklisted user {target.name} (ID: {user_id}).")
    await ctx.respond(f"Blacklisted {mention}!", ephemeral=True)

@owner_exclusive.command(name="unblacklist", description="Unblacklists a user.")
async def unblacklist(ctx: discord.ApplicationContext, target: discord.Member):
    if await BasicIsNotOwnerMessage(ctx):
        return

    mention = target.mention
    user_id = target.id

    # remove the user from the blacklist (nexus.db)
    cursor.execute(
        f"UPDATE {TABLE_NAME} SET rank = {ranks_dict['normal']} WHERE user_id = ?",
        (user_id,)
    )

    connection.commit()

    print(f"LOG: Owner unblacklisted user {target.name} (ID: {user_id}).")
    await ctx.respond(f"Unblacklisted {mention}!", ephemeral=True)

@nexus.command(name="check", description="Checks a user's stats.")
async def check(ctx: discord.ApplicationContext, target: discord.Member):
    if await BasicIsNotLoggedInMessage(ctx):
        return

    # Check if the target exists in the database
    target_id = target.id
    if await BasicIsIDExistsMessage(bot, ctx, target_id):
        return

    print(f"LOG: User {ctx.author.name} checked stats for user {target.name} (ID: {target_id}).")
    embed = discord.Embed(
        title=f"{target.name}'s Stats",
        description=f"Stats for {target.name}",
        color=discord.Colour.blurple(),
    )
    GeneralEmbedRequirement(ctx, embed)

    embed.set_thumbnail(url=target.display_avatar.url)

    embed.add_field(name="Name", value=target.name, inline=True)
    embed.add_field(name="Display Name", value=target.display_name, inline=True)
    embed.add_field(name="ID", value=target.id, inline=True)
    embed.add_field(name="Account Created", value=target.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Joined Server", value=target.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

    # Database stuff

    # 1. Level and XP
    level, xp = FetchLevelAndXP(target_id)
    xp_needed = xp_required[level]
    total_xp = sum(xp_required[:level]) + xp
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="XP", value=f"{xp}/{xp_needed}", inline=True)
    embed.add_field(name="Total XP", value=total_xp, inline=True)

    # 2. Rank
    cursor.execute(
        f"SELECT rank FROM {TABLE_NAME} WHERE user_id = ?",
        (target_id,)
    )
    result = cursor.fetchone()
    rank_value = result[0] # this will always be a valid rank. Hopefully.
    rank_name = ranks[rank_value]
    embed.add_field(name="Rank", value=rank_name, inline=True)

    await ctx.respond(embed=embed)


print("ATTEMPT: Running the bot...")
bot.run(TOKEN)

print("ATTEMPT: Closing the database connection...")
connection.close()
print("SUCCESS: Database connection closed.")
print("Thank you for using the bot! Have a great day!")