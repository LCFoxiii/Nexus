from core.init_discord import *

from ..helpers.user_exists import *
from ..helpers.slime_damage import *
from ..helpers.slimes import *
from ..helpers.adjust_to_percentage import *

from general_helpers.db_helpers import *

from ..init.database.creation import *

import random
import asyncio

# delays (in seconds)
MESSAGE_DELETE_DELAY = 1.0
ASYNCIO_SLEEP_DELAY  = 0.5

class SQAttackUI(discord.ui.View):

    def __init__(self, slime_info, author, adjustions, slime_choice, battle_state, chances):
        super().__init__()
        self.author       = author

        self.slime_info   = slime_info
        self.slime_choice = slime_choice

        self.battle_state = battle_state
        self.chances      = chances

        self.adjustions   = adjustions

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your battle!", ephemeral=True)
            return False

        return True

    @discord.ui.button(label="Attack", row=0, style=discord.ButtonStyle.red)
    async def attack_button(self, button: discord.ui.Button, interaction: discord.Interaction):

        if self.slime_choice == ATTACK:
            await interaction.response.send_message(
                "TEMP: both attacked, clashed, no damage dealt, -1 for both.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["slime_turn_count"] -= 1
            self.battle_state["player_turn_count"] -= 1

        elif self.slime_choice == BLOCK:
            # TODO: Implement a chance for the player to break through the slime's block and deal damage, based on the player's sword PEN stat.

            await interaction.response.send_message(
                "TEMP: you attack, the slime blocks. -1 turn.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["player_turn_count"] -= 1

        elif self.slime_choice == PARRY:
            await interaction.response.send_message(
                "TEMP: you attack, the slime parries. -2 turns.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["player_turn_count"] -= 2

        elif self.slime_choice == NOTHING:

            # TODO: also add a crit chance stat to the player (0-200)
            critical_chance = self.chances["critical"]
            d1f = random.uniform(0, 1)
            base_adjusted_damage = self.adjustions["player_damage"]
            
            if critical_chance > d1f:
                critical_damage = base_adjusted_damage * 2

                await interaction.response.send_message(
                    f"CRITICAL HIT! You dealt {critical_damage} damage to the slime!",
                    delete_after=MESSAGE_DELETE_DELAY
                )

                self.slime_info["health"] -= critical_damage

            else:
                await interaction.response.send_message(
                    f"+{base_adjusted_damage} damage to the slime!",
                    delete_after=MESSAGE_DELETE_DELAY
                )

                self.slime_info["health"] -= base_adjusted_damage

        self.stop()

    @discord.ui.button(label="Defend", row=0, style=discord.ButtonStyle.green)
    async def defend_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # TODO: Add defense success & failure chance mechanic based on player's DEX stat. and also the shield's base block percentage stat.
        # TODO: Add slime's attack penetration mechanic based on slime's PEN stat. (0-100)
        # for now, 100% success rate of blocking the slime's attack. and no penetration damage.

        if self.slime_choice == ATTACK:
            await interaction.response.send_message(
                "TEMP: you defend, slime attacked, no damage dealt. -1 turn for slime.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["slime_turn_count"] -= 1

        elif self.slime_choice == BLOCK:
            await interaction.response.send_message(
                "TEMP: both defended, no damage dealt, -1 for both.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["slime_turn_count"] -= 1
            self.battle_state["player_turn_count"] -= 1

        elif self.slime_choice == PARRY:
            await interaction.response.send_message(
                "TEMP: you defend, slime parries, no damage dealt. -1 for both.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["slime_turn_count"] -= 1
            self.battle_state["player_turn_count"] -= 1

        else:
            await interaction.response.send_message(
                "TEMP: You defend, slime did nothing. -1 turn.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["player_turn_count"] -= 1

        self.stop()

    @discord.ui.button(label="Parry", row=0, style=discord.ButtonStyle.blurple)
    async def parry_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        d1f = random.uniform(0, 1)
        parry_chance = self.chances["parry"]

        if parry_chance > d1f:
            await interaction.response.send_message(
                "TEMP: you failed, -1 turn.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["player_turn_count"] -= 1

            self.stop()
            return

        if self.slime_choice == ATTACK:
            await interaction.response.send_message(
                "TEMP: you parry, slime attacked, no damage dealt. -2 turns for slime.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["slime_turn_count"] -= 2

        elif self.slime_choice == BLOCK:
            await interaction.response.send_message(
                "TEMP: you parry, slime blocked, no damage dealt. -1 turn.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["player_turn_count"] -= 1

        elif self.slime_choice == PARRY:
            await interaction.response.send_message(
                "TEMP: both parried, no damage dealt. -1 for both.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["slime_turn_count"] -= 1
            self.battle_state["player_turn_count"] -= 1

        else:
            await interaction.response.send_message(
                "TEMP: You parry, slime did nothing. -1 turn.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["player_turn_count"] -= 1

        self.stop()

    @discord.ui.button(label="Run", row=0, style=discord.ButtonStyle.blurple)
    async def run_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        d1f = random.uniform(0, 1)
        escape_chance = self.chances["escape"]

        if escape_chance > d1f:
            await interaction.response.send_message(
                "You successfully escaped from the slime!",
                ephemeral=True,
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["is_running"] = True

        else:
            await interaction.response.send_message(
                "You failed to escape from the slime! -1 turn.",
                ephemeral=True,
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["player_turn_count"] -= 1

        self.stop()


@slimequest.command(name="attack", description="TEMP: Creates a slime and put you in a simulated battle with it.")
async def attack(ctx: discord.ApplicationContext):

    if await SQUserExistsMessage(ctx):
        return

    random_slime = random.choice(list(slime_entries.keys()))

    # Inits
    author = ctx.author
    user_id = author.id

    slime_info = slime_entries[random_slime]

    battle_states = {
        "player_turn_count": 0,
        "slime_turn_count": 0,
        "is_running": False
    }

    slime_name        = slime_info["name"]
    slime_description = slime_info["description"]
    slime_damage      = slime_info["damage"]
    slime_defense     = slime_info["defense"]
    slime_speed       = slime_info["speed"]
    
    # fancy slime stuff
    slime_moveset     = slime_info["moveset"] # think of this as the slime's "personality".

    embed = discord.Embed(
        title=slime_name,
        description=slime_description,
        color=discord.Color.blue()
    )

    # Grab some stuff from the database.
    player_base_damage, player_defense, player_health, player_speed, player_dexterity = DBGrab(
        user_id,
        TABLE_STATS,
        ["damage", "defense", "health", "speed", "dexterity"],
        ID_NAME,
        sq_cursor
    )

    # Adjustions
    adjustions = {
        "player_damage": SQGetDamage(slime_defense, player_base_damage),
        "slime_damage":  SQGetDamage(player_defense, slime_damage)
    }

    # Chances
    chances = {
        "escape":   SQAdjustToPercentage(player_speed, slime_speed, 200),
        "critical": SQAdjustToPercentage(player_dexterity, slime_speed, 100),
        "parry":    SQAdjustToPercentage(player_dexterity, 0, 100)
    }
    
    # embeds
    embed.add_field(name="Slime Health", value=f"{slime_info['health']}", inline=True)
    embed.add_field(name="Your Health", value=f"{player_health}", inline=True)
    embed.add_field(name="Your turn(s)", value=f"{battle_states['player_turn_count']}", inline=True)
    embed.add_field(name="Slime turn(s)", value=f"{battle_states['slime_turn_count']}", inline=True)
    
    # battle loop
    fight_msg = await ctx.respond(f"You encountered a {slime_name}!")

    while True:
        await asyncio.sleep(ASYNCIO_SLEEP_DELAY)

        embed.set_field_at(0, name="Slime Health", value=f"{slime_info['health']}", inline=True)
        embed.set_field_at(1, name="Your Health", value=f"{player_health}", inline=True)
        embed.set_field_at(2, name="Your turn(s)", value=f"{battle_states['player_turn_count']}", inline=True)
        embed.set_field_at(3, name="Slime turn(s)", value=f"{battle_states['slime_turn_count']}", inline=True)

        if slime_info["health"] <= 0:
            await ctx.send(f"You defeated the {slime_name}!")

            # TODO: get the rewards.

            break

        if player_health <= 0:
            await ctx.send(f"You were defeated by the {slime_name}!")

            player_health = 0 # just in case, to avoid negative health values.
            break

        if battle_states["is_running"]:
            await ctx.send(f"You ran away from the {slime_name}!")
            break

        # This should make the slime attack the player until the player has turns again.
        if battle_states["player_turn_count"] < 0:
            player_health -= adjustions["slime_damage"]
            battle_states["player_turn_count"] += 1

            await ctx.send(
                f"The {slime_name} attacked you for {adjustions["slime_damage"]} damage! Your health is now {player_health}.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            continue

        # TODO: Implement something that makes the slime's choice more intelligent, based on the slime's INT stat.

        # This has a chance of beating your ass, so i hope you are lucky.
        slime_choice = NOTHING

        if battle_states["slime_turn_count"] >= 0:
            slime_choice = random.choice(slime_moveset)
        else:
            battle_states["slime_turn_count"] += 1

        battle_view = SQAttackUI(slime_info, author, adjustions, slime_choice, battle_states, chances)

        await fight_msg.edit(embed=embed, view=battle_view)
        await battle_view.wait()

    # Update the player's health in the database after the battle.
    DBUpdate(user_id, TABLE_STATS, {"health": player_health}, ID_NAME, sq_cursor, sq_connection)