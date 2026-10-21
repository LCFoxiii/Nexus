from core.init_discord import *

async def FindUserByID(user_id: int) -> discord.User | None:
    user = bot.get_user(user_id)
    if user is None:
        try:
            user = await bot.fetch_user(user_id)
        except discord.NotFound:
            return None
    return user