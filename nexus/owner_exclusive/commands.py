import discord

from core.init_discord import *
from core.db_init import *


@owner_exclusive.command(name="grant", description="Grant a user VIP.")
async def grant(ctx: discord.ApplicationContext, target: discord.Member):
    if await BasicIsNotOwnerMessage(ctx):
        return

    mention = target.mention
    user_id = target.id

    GrantIDVIP(user_id)

    print(f"LOG: Owner granted VIP to user {target.name} (ID: {user_id}).")
    await ctx.respond(f"Granted {mention} cool stuff!", ephemeral=True)


@owner_exclusive.command(name="revoke", description="Revokes a user from being a VIP.")
async def revoke(ctx: discord.ApplicationContext, target: discord.Member):
    if await BasicIsNotOwnerMessage(ctx):
        return

    mention = target.mention
    user_id = target.id

    RevokeIDVIP(user_id)

    print(f"LOG: Owner revoked VIP from user {target.name} (ID: {user_id}).")
    await ctx.respond(f"Ungranted {mention} from cool stuff!", ephemeral=True)


@owner_exclusive.command(name="blacklist", description="Blacklists a user.")
async def blacklist(ctx: discord.ApplicationContext, target: discord.Member):
    if await BasicIsNotOwnerMessage(ctx):
        return

    mention = target.mention
    user_id = target.id

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

    cursor.execute(
        f"UPDATE {TABLE_NAME} SET rank = {ranks_dict['normal']} WHERE user_id = ?",
        (user_id,)
    )

    connection.commit()

    print(f"LOG: Owner unblacklisted user {target.name} (ID: {user_id}).")
    await ctx.respond(f"Unblacklisted {mention}!", ephemeral=True)
