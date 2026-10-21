from ..helpers.delays import *
from ..helpers.items import *
from ..helpers.user_exists import *
from ..helpers.adjust_to_percentage import *

from core.init_discord import *
from ..init.database.creation import *

from general_helpers.find_user import *

@slimequest.command(name="profile", description="Displays a user's profile")
async def profile(ctx: discord.ApplicationContext, user: discord.User = None):
    if user is None:
        user = ctx.author

    user_id = user.id

    if not SQUserExists(user_id):
        await ctx.respond(f"ERROR: User {user.name} does not exist in the database. Please use \"/slimequest register\" to register yourself.", ephemeral=True)
        print(f"LOG: User {user.name} attempted to view a profile but does not exist in the database.")
        return
    
    # no need to check if user is None.
    user = await FindUserByID(user_id)

    result_user = sq_cursor.execute(
        f"SELECT name, gender FROM {TABLE_USERS} WHERE {ID_NAME} = ?",
        (user_id,)
    ).fetchone()
    
    result_currency = sq_cursor.execute(
        f"SELECT {COPPER}, {SILVER}, {GOLD} FROM {TABLE_CURRENCY} WHERE {ID_NAME} = ?",
        (user_id,)
    ).fetchone()

    result_stats = sq_cursor.execute(
        f"SELECT {LEVEL}, {XP}, {HEALTH}, {MANA}, {DEXTERITY}, {STRENGTH}, {DEFENSE}, {SPEED}, {DAMAGE}, {CRITICAL_CHANCE} FROM {TABLE_STATS} WHERE {ID_NAME} = ?",
        (user_id,)
    ).fetchone()
    
    # checks are not needed as I found out just now, whoops.
    
    name, gender = result_user
    copper, silver, gold = result_currency
    level, xp, health, mana, dexterity, strength, defense, speed, damage, critical_chance = result_stats
    
    critical_chance = str(SQAdjustToPercentage(critical_chance, 0, 200) * 100) + "%"
    gender_str = "Male" if gender == 0 else "Female" if gender == 1 else "Other / Non-Binary"
    
    currency_str = None
    
    if 0 == copper == silver == gold:
        currency_str = "Broke LMAOAOAOA 😭🫵🫵🫵🫵🫵"
    else:
        currency_str = f"Copper: {copper}\nSilver: {silver}\nGold: {gold}"
    
    # TODO: Add a check for the user's most dominant color for all embeds, also rearange this a bit.
    embed = discord.Embed(
        title=f"{name}'s Profile",
        description=f"Level: {level}\nGender: {gender_str}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Currency", value=currency_str, inline=False)
    embed.add_field(
        name="Stats",
        value=f"XP: {xp}\nHealth: {health}\nMana: {mana}\nDexterity: {dexterity}\nStrength: {strength}\nDefense: {defense}\nSpeed: {speed}\nDamage: {damage}\nCritical Chance: {critical_chance}",
        inline=False
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    
    await ctx.respond(embed=embed, ephemeral=True)