from core.init_discord import *

from ..helpers.user_exists import *
from ..helpers.slime_damage import *
from ..helpers.slimes import *
from ..helpers.adjust_to_percentage import *
from ..helpers.items import *
from ..helpers.put_in_inventory import *

from general_helpers.db_helpers import *

from ..init.database.creation import *

import random
import asyncio

# delays (in seconds)
MESSAGE_DELETE_DELAY = 1.0
ASYNCIO_SLEEP_DELAY  = 0.5

# helper function
async def Attack(adjustions, chances, player_health, interaction, slime_info):
    await interaction.response.defer()

    critical_chance = chances["critical"]
    d1f = random.uniform(0, 1)
    base_adjusted_damage = adjustions["player_damage"]

    if critical_chance > d1f:
        critical_damage = base_adjusted_damage * 2

        await interaction.followup.send(
            f"CRITICAL HIT! You dealt {critical_damage} damage to the slime!",
            delete_after=MESSAGE_DELETE_DELAY
        )

        slime_info["health"] -= critical_damage

    else:
        await interaction.followup.send(
            f"+{base_adjusted_damage} damage to the slime!",
            delete_after=MESSAGE_DELETE_DELAY
        )

        slime_info["health"] -= base_adjusted_damage

    # 25% chance to get splashed by the slime's toxic body when you attack it.
    d1f = random.uniform(0, 1)

    if d1f < 0.25:
        splash_damage = round(adjustions["slime_damage"] * (1 - chances["splash_reduction"]))
        player_health -= splash_damage

        await interaction.followup.send(
            f"You were splashed by the slime's toxic body! "
            f"You took {splash_damage} damage. Your health is now {player_health}.",
            delete_after=MESSAGE_DELETE_DELAY
        )

    return player_health

class SQAttackUI(discord.ui.View):

    def __init__(self, slime_info, author, adjustions, slime_choice, battle_state, chances, player_health, slime_moveset):
        super().__init__()
        self.author       = author

        self.slime_info   = slime_info
        self.slime_choice = slime_choice

        self.battle_state = battle_state
        self.chances      = chances
        self.slime_moveset = slime_moveset

        self.adjustions   = adjustions
        
        self.player_health = player_health

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your battle!", ephemeral=True)
            return False

        return True
    
    def choose_slime_move(self, player_move):
        
        if self.battle_state["slime_turn_count"] < 0:
            self.battle_state["slime_turn_count"] += 1
            return NOTHING

        d1f = random.uniform(0, 1)
        if self.chances["slime_intelligence"] > d1f:

            # move ordered in:
            # most to the least likely to hit player.
            if player_move == ATTACK:
                priorities = [PARRY, BLOCK, ATTACK, NOTHING]

            elif player_move == BLOCK:
                priorities = [NOTHING, BLOCK, PARRY, ATTACK]

            elif player_move == PARRY:
                priorities = [NOTHING, BLOCK, PARRY, ATTACK]

            for move in priorities:
                if move in self.slime_moveset:
                    return move

        # Unintelligent slime just picks randomly.
        return random.choice(self.slime_moveset)

    @discord.ui.button(label="Attack", row=0, style=discord.ButtonStyle.red)
    async def attack_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        
        self.slime_choice = self.choose_slime_move(ATTACK)

        if self.slime_choice == ATTACK:
            await interaction.response.send_message(
                "TEMP: both attacked, clashed, no damage dealt, -1 for both.",
                delete_after=MESSAGE_DELETE_DELAY
            )

            self.battle_state["slime_turn_count"] -= 1
            self.battle_state["player_turn_count"] -= 1

        elif self.slime_choice == BLOCK:
            
            # in theory, this should be a good compensation for slime's splash damage stuff.
            d1f = random.uniform(0, 1)
            if self.chances["block_penetration"] > d1f:
                await interaction.response.send_message(
                    f"TEMP: you attack, the slime blocks, but your weapon penetrates the block!",
                    delete_after=MESSAGE_DELETE_DELAY
                )
                
                self.player_health = await Attack(self.adjustions, self.chances, self.player_health, interaction, self.slime_info)
                self.stop()
                return

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
            self.player_health = await Attack(self.adjustions, self.chances, self.player_health, interaction, self.slime_info)

        self.stop()

    @discord.ui.button(label="Defend", row=0, style=discord.ButtonStyle.green)
    async def defend_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        
        self.slime_choice = self.choose_slime_move(BLOCK)
        
        if self.slime_choice == ATTACK:
            
            d1f = random.uniform(0, 1)
            
            # block penetration
            if self.chances["block_penetration"] > d1f:
                await interaction.response.send_message(
                    "TEMP: you defend, slime penetrates your block, you take damage!",
                    delete_after=MESSAGE_DELETE_DELAY
                )
                self.player_health -= round(self.adjustions["slime_damage"] / 1.5) # 66% of the damage is dealt to the player.
                self.stop()
                return

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
        
        self.slime_choice = self.choose_slime_move(PARRY)

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
    await ctx.defer()

    if await SQUserExistsMessage(ctx):
        return

    random_slime = random.choice(list(slime_entries.keys()))

    # Inits
    author = ctx.author
    user_id = author.id

    # this should fix the bug where the slime's health is not reset after the battle.
    slime_info_ = slime_entries[random_slime]
    slime_info = slime_info_.copy()

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
    slime_penetration = slime_info["penetration"]

    # fancy slime stuff
    slime_moveset      = slime_info["moveset"] # think of this as the slime's "personality".
    guaranteed_loot    = slime_info["guaranteed_loot"]
    randomized_loot    = slime_info["possible_loot"]
    slime_intelligence = slime_info["intelligence"]
    
    # fancy inventory stuff
    
    shield_defense_boost = 0
    helmet_defense_boost = 0
    chestplate_defense_boost = 0
    leggings_defense_boost = 0
    boots_defense_boost = 0

    shield_splash_protection = 0
    helmet_splash_protection = 0
    chestplate_splash_protection = 0
    leggings_splash_protection = 0
    boots_splash_protection = 0

    for equipment_slot in [SHIELD, HELMET, CHESTPLATE, LEGGINGS, BOOTS]:
        equipment = sq_cursor.execute(
            f"""
                SELECT {ID_NAME_ITEM}
                FROM {TABLE_INVENTORY}
                WHERE {ID_NAME} = ? AND slot = ?
            """,
            (user_id, equipment_slot)
        ).fetchone()

        if equipment:
            equipment_id = equipment[0]
            equipment_info = items_dict[equipment_id]

            defense_boost = equipment_info["stats"]["defense_boost"]
            splash_protection = equipment_info["stats"]["slime_splash_protection"]

            if equipment_slot == SHIELD:
                shield_defense_boost = defense_boost
                shield_splash_protection = splash_protection

            elif equipment_slot == HELMET:
                helmet_defense_boost = defense_boost
                helmet_splash_protection = splash_protection

            elif equipment_slot == CHESTPLATE:
                chestplate_defense_boost = defense_boost
                chestplate_splash_protection = splash_protection

            elif equipment_slot == LEGGINGS:
                leggings_defense_boost = defense_boost
                leggings_splash_protection = splash_protection

            elif equipment_slot == BOOTS:
                boots_defense_boost = defense_boost
                boots_splash_protection = splash_protection
    
    # grab the player's weapon from the database, if they have one equipped.
    weapon = sq_cursor.execute(
        f"""
            SELECT {ID_NAME_ITEM}
            FROM {TABLE_INVENTORY}
            WHERE {ID_NAME} = ? AND slot = ?
        """,
        (user_id, WEAPON)
    ).fetchone()
    
    equipped_weapon = weapon[0] if weapon else None
    weapon_info = items_dict[equipped_weapon] if equipped_weapon else None
    weapon_damage_boost = weapon_info["stats"]["damage_boost"] if weapon_info else 0
    weapon_block_penetration = weapon_info["stats"]["block_penetration"] if weapon_info else 0
    
    combined_defense_boost = shield_defense_boost + helmet_defense_boost + chestplate_defense_boost + leggings_defense_boost + boots_defense_boost
    combined_splash_protection = shield_splash_protection + helmet_splash_protection + chestplate_splash_protection + leggings_splash_protection + boots_splash_protection

    # Grab some stuff from the database.
    player_base_damage, player_defense, player_health, player_speed, player_dexterity, crit_chance = DBGrab(
        user_id,
        TABLE_STATS,
        ["damage", "defense", "health", "speed", "dexterity", "critical_chance"],
        ID_NAME,
        sq_cursor
    )

    # Adjustions
    adjustions = {
        "player_damage": SQGetDamage(slime_defense, player_base_damage + weapon_damage_boost),
        "slime_damage":  SQGetDamage(player_defense + combined_defense_boost, slime_damage),
    }

    # Chances
    chances = {
        "escape":              SQAdjustToPercentage(player_speed, slime_speed, 100),
        "critical":            SQAdjustToPercentage(player_dexterity + crit_chance, slime_speed, 200),
        "parry":               SQAdjustToPercentage(player_dexterity, 0, 100),
        "splash_reduction":    SQAdjustToPercentage(combined_splash_protection, 0, 500),
        "block_penetration":   SQAdjustToPercentage(weapon_block_penetration, 0, 100),
        "slime_penetration":   SQAdjustToPercentage(slime_penetration, player_dexterity + shield_defense_boost, 200),
        "slime_intelligence":  SQAdjustToPercentage(slime_intelligence, 0, 100)
    }
    
    # embeds
    embed = discord.Embed(
        title=slime_name,
        description=slime_description,
        color=discord.Color.blue()
    )
    
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
            
            # TODO: add a message that shows the rewards the player got from defeating the slime.
            
            currency_rewards = slime_info["rewards"]["currency"]
            stats_rewards = slime_info["rewards"]["stats"]
            
            if currency_rewards:
                for key, coins in currency_rewards.items():
                    DBIncrement(user_id, TABLE_CURRENCY, key, coins, ID_NAME, sq_cursor, sq_connection)
            
            if stats_rewards:
                for key, value in stats_rewards.items():
                    DBIncrement(user_id, TABLE_STATS, key, value, ID_NAME, sq_cursor, sq_connection)
            
            # inventory rewards
            for item_id, quantity in guaranteed_loot.items():
                SQPutItemInInventory(user_id, item_id, quantity)
            
            for item_id, (max_quantity, chance) in randomized_loot.items():
                d1f = random.uniform(0, 1)
                
                if chance > d1f:
                    quantity = random.randint(1, max_quantity)
                    SQPutItemInInventory(user_id, item_id, quantity)
            
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

        slime_choice = NOTHING
        battle_view = SQAttackUI(slime_info, author, adjustions, slime_choice, battle_states, chances, player_health, slime_moveset)

        await fight_msg.edit(embed=embed, view=battle_view)
        await battle_view.wait()

    # Update the player's health in the database after the battle.
    DBUpdate(user_id, TABLE_STATS, {"health": player_health}, ID_NAME, sq_cursor, sq_connection)
    
# temporary test command to see if items are being added to the inventory correctly.
# delete this command later, it's just for testing purposes.
@slimequest.command(name="test_inventory", description="TEMP: Test command to see if items are being added to the inventory correctly.")
async def test_inventory(ctx: discord.ApplicationContext):
    await ctx.defer()
    
    if await SQUserExistsMessage(ctx):
        return

    user_id = ctx.author.id

    # view everything in the inventory for this user.
    sq_cursor.execute(
        f"""
            SELECT {ID_NAME_ITEM}, quantity, slot
            FROM {TABLE_INVENTORY}
            WHERE {ID_NAME} = ?
        """,
        (user_id,)
    )
    
    inventory_items = sq_cursor.fetchall()
    idx = 1
    
    if not inventory_items:
        await ctx.respond("Your inventory is empty.")
        return
    
    for item_id, quantity, slot in inventory_items:
        item_name = items_dict[item_id]["name"]
        await ctx.respond(f"{idx}: {item_name} (ID: {item_id}) - Quantity: {quantity} - Slot: {slot}")
        idx += 1