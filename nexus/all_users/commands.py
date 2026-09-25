import discord
import secrets
from argon2.exceptions import VerifyMismatchError

from core.init_discord import (
    BasicIsBlacklistedMessage,
    BasicIsIDExistsMessage,
    BasicIsIDNotLoggedInMessage,
    bot,
    cursor,
    nexus,
    online_users,
    password_hasher,
    ranks_dict,
    xp_required,
)
from core.db_init import FetchLevelAndXP, TABLE_NAME, connection
from core.embeds_helper import GeneralEmbedRequirement


@nexus.command(name="register", description="Registers you to use the bot.")
async def register(ctx: discord.ApplicationContext, password: str):
    user_id = ctx.author.id

    print(f"LOG: User {ctx.author.name} attempted to register with password: {password}.")
    if user_id not in online_users:
        online_users.add(user_id)

        password_hash = password_hasher.hash(password)

        print(f"LOG: User {ctx.author.name} registered with hash: {password_hash}.")

        cursor.execute(
            f"INSERT INTO {TABLE_NAME} (user_id, rank, level, xp, password_hash, remember_login) VALUES (?, ?, ?, ?, ?, FALSE)",
            (user_id, ranks_dict['normal'], 0, 0, password_hash)
        )

        
        await ctx.respond("You have been registered!", ephemeral=True)
    else:
        print(f"LOG: User {ctx.author.name} attempted to register but is already registered.")
        await ctx.respond("You are already able to use the bot.", ephemeral=True)


@nexus.command(name="login", description="Logs you in to use the bot.")
async def login(ctx: discord.ApplicationContext, password: str):
    user_id = ctx.author.id

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

            

            print(f"LOG: User {ctx.author.name}'s password hash has been rehashed for security.")
    else:
        print(f"LOG: User {ctx.author.name} attempted to log in but is already logged in.")
        await ctx.respond("You are already able to use the bot.", ephemeral=True)


@nexus.command(name="logout", description="Logs you out of the bot.")
async def logout(ctx: discord.ApplicationContext):
    user_id = ctx.author.id

    if user_id in online_users:
        online_users.remove(user_id)
        await ctx.respond("You have been logged out!", ephemeral=True)

        print(f"LOG: User {ctx.author.name} logged out successfully.")
    else:
        print(f"LOG: User {ctx.author.name} attempted to log out but is not logged in.")
        await ctx.respond("You are not logged in.", ephemeral=True)


@nexus.command(name="remember", description="Remembers to log you in automatically upon bot startup because the user is lazy.")
async def remember(ctx: discord.ApplicationContext):
    user_id = ctx.author.id

    if await BasicIsIDNotLoggedInMessage(ctx, user_id):
        return

    cursor.execute(
        f"UPDATE {TABLE_NAME} SET remember_login = TRUE WHERE user_id = ?",
        (user_id,)
    )

    

    print(f"LOG: user {ctx.author.name} (ID: {user_id}) will now be remembered to log in automatically upon bot startup.")
    await ctx.respond("You will now be remembered to log in automatically upon bot startup.", ephemeral=True)


@nexus.command(name="forget", description="Forgets to log you in automatically upon bot startup.")
async def forget(ctx: discord.ApplicationContext):
    user_id = ctx.author.id

    if await BasicIsIDNotLoggedInMessage(ctx, user_id):
        return

    cursor.execute(
        f"UPDATE {TABLE_NAME} SET remember_login = FALSE WHERE user_id = ?",
        (user_id,)
    )

    

    print(f"LOG: user {ctx.author.name} (ID: {user_id}) will no longer be remembered to log in automatically upon bot startup.")
    await ctx.respond("You will no longer be remembered- wait, who are you?", ephemeral=True)


@nexus.command(name="random-number", description="Generates a random number.")
async def random_number(ctx: discord.ApplicationContext, min_value: int, max_value: int):
    if await BasicIsIDNotLoggedInMessage(ctx, ctx.author.id) or await BasicIsBlacklistedMessage(ctx):
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

    if await BasicIsIDNotLoggedInMessage(ctx, user_id) or await BasicIsBlacklistedMessage(ctx):
        return

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


@nexus.command(name="check", description="Checks a user's stats.")
async def check(ctx: discord.ApplicationContext, target: discord.Member):
    if await BasicIsIDNotLoggedInMessage(ctx, ctx.author.id) or await BasicIsBlacklistedMessage(ctx):
        return

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

    level, xp = FetchLevelAndXP(target_id)
    xp_needed = xp_required[level]
    total_xp = sum(xp_required[:level]) + xp
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="XP", value=f"{xp}/{xp_needed}", inline=True)
    embed.add_field(name="Total XP", value=total_xp, inline=True)

    cursor.execute(
        f"SELECT rank FROM {TABLE_NAME} WHERE user_id = ?",
        (target_id,)
    )
    result = cursor.fetchone()
    rank_value = result[0]
    rank_name = ["normal", "vip", "blacklisted"][rank_value]
    embed.add_field(name="Rank", value=rank_name, inline=True)

    await ctx.respond(embed=embed)
