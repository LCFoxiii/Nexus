from datetime import date

import discord


def GeneralEmbedRequirement(ctx: discord.ApplicationContext, embed_: discord.Embed):
    embed_.set_author(name="Nexus Contributors", icon_url=ctx.bot.user.display_avatar.url)
    embed_.set_footer(
        text=f"Made with 💕 by the Nexus contributors - {date.today()}",
        icon_url=ctx.bot.user.display_avatar.url,
    )
