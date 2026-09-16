from core.init_discord import *
from ..helpers.user_exists import *
from ..helpers.slime_damage import *
from ..helpers.slimes import *

from ..init.database.creation import *

import random
import asyncio

MESSAGE_DELETE_DELAY = 1.0 # seconds
ASYNCIO_SLEEP_DELAY  = 0.5 # seconds

class SQAttackUI(discord.ui.View):
    
    def __init__(self, slime_info, author, adjusted_user_damage, slime_choice, battle_state):
        super().__init__()
        self.slime_info = slime_info
        self.author = author
        self.adjusted_user_damage = adjusted_user_damage
        self.slime_choice = slime_choice # could either be attack, block, parry, nothing.
        self.battle_state = battle_state
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your battle!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Attack", row=0, style=discord.ButtonStyle.red)
    async def attack_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        
        #TODO: Implement critical hits.
        # attacking should be a high risk, high reward option.
        # on one hand, you can deal a lot of damage to the slime,
        # but on the other hand, you can also take a lot of damage from the slime. (from parrying and losing your turn)
        
        if (self.battle_state["slime_turn_count"] >= 0):
            if self.slime_choice == "attack":
                await interaction.response.send_message("TEMP: both attacked, clashed, no damage dealt, -1 for both.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["slime_turn_count"] = -1
                self.battle_state["player_turn_count"] = -1
            elif self.slime_choice == "block":
                #TODO: Implement a chance for the player to break through the slime's block and deal damage, based on the player's sword PEN stat.
                await interaction.response.send_message("TEMP: you attack, the slime blocks. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["player_turn_count"] = -1
            elif self.slime_choice == "parry":
                await interaction.response.send_message("TEMP: you attack, the slime parries. -2 turns.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["player_turn_count"] = -2
            
            else:
                await interaction.response.send_message(f"+{self.adjusted_user_damage} damage to the slime!", delete_after=MESSAGE_DELETE_DELAY)
                self.slime_info["health"] -= self.adjusted_user_damage
        else:
            await interaction.response.send_message(f"+{self.adjusted_user_damage} damage to the slime!", delete_after=MESSAGE_DELETE_DELAY)
            self.slime_info["health"] -= self.adjusted_user_damage

        self.stop()
    
    @discord.ui.button(label="Defend", row=0, style=discord.ButtonStyle.green)
    async def defend_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        #TODO: Add defense success & failure chance mechanic based on player's DEX stat.
        #TODO: Add slime's attack penetration mechanic based on slime's PEN stat. (1.0 = 100% penetration, 0.0 = 0% penetration chance)
        #for now, 100% success rate of blocking the slime's attack. and no penetration damage.
        
        if (self.battle_state["slime_turn_count"] >= 0):
            if (self.slime_choice == "attack"):
                await interaction.response.send_message("TEMP: you defend, slime attacked, no damage dealt. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["slime_turn_count"] = -1
            elif (self.slime_choice == "block"):
                await interaction.response.send_message("TEMP: both defended, no damage dealt, -1 for both.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["slime_turn_count"] = -1
                self.battle_state["player_turn_count"] = -1
            elif (self.slime_choice == "parry"):
                await interaction.response.send_message("TEMP: you defend, slime parries, no damage dealt. -1 for both.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["slime_turn_count"] = -1
                self.battle_state["player_turn_count"] = -1
            else:
                await interaction.response.send_message("TEMP: You defend, slime did nothing. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["player_turn_count"] = -1
        else:
            await interaction.response.send_message("TEMP: You defend, slime did nothing. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["player_turn_count"] = -1
        
        self.stop()
        
    @discord.ui.button(label="Parry", row=0, style=discord.ButtonStyle.blurple)
    async def parry_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        #TODO: Add parry success & failure chance mechanic based on player's DEX stat.
        
        if (self.battle_state["slime_turn_count"] >= 0):
            if (self.slime_choice == "attack"):
                await interaction.response.send_message("TEMP: you parry, slime attacked, no damage dealt. -2 turns for slime.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["slime_turn_count"] = -2
            elif (self.slime_choice == "block"):
                await interaction.response.send_message("TEMP: you parry, slime blocked, no damage dealt. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["player_turn_count"] = -1
            elif (self.slime_choice == "parry"):
                await interaction.response.send_message("TEMP: both parried, no damage dealt. -1 for both.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["slime_turn_count"] = -1
                self.battle_state["player_turn_count"] = -1
            else:
                await interaction.response.send_message("TEMP: You parry, slime did nothing. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
                self.battle_state["player_turn_count"] = -1
        else:
            await interaction.response.send_message("TEMP: You parry, slime did nothing. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["player_turn_count"] = -1
        self.stop()
        
    @discord.ui.button(label="Run", row=0, style=discord.ButtonStyle.blurple)
    async def run_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        #TODO: Implement a chance for the player to successfully run away from the slime, based on the player's speed stat and the slime's speed stat.
        # for now, 100% success rate of running away from the slime.
        
        await interaction.response.send_message("You ran away from the slime!", ephemeral=True, delete_after=MESSAGE_DELETE_DELAY)
        self.battle_state["is_running"] = True
        self.stop()

@slimequest.command(name="attack", description="TEMP: Creates a slime and put you in a simulated battle with it.")
async def attack(ctx: discord.ApplicationContext):
    if await SQUserExistsMessage(ctx):
        return
    
    random_slime = random.choice(list(slime_entries.keys()))
    
    # Battle initializations
    slime_info = slime_entries[random_slime]
    author = ctx.author
    slime_choice = "nothing" # default is nothing, should (hopefully) be changed during the battle loop.
    battle_state = {
        "player_turn_count": 0,
        "slime_turn_count": 0,
        "is_running": False
    }
    
    user_id = author.id
    
    # grab base damage, defense, and health from the database for the player.
    
    sq_cursor.execute(
        f"SELECT damage, defense, health FROM {TABLE_STATS} WHERE {ID_NAME} = ?",
        (user_id,)
    )
    
    player_base_damage, player_base_defense, player_base_health = sq_cursor.fetchone()
    
    # adjusting
    adjusted_slime_damage = SQGetSlimeDamage(player_base_defense, slime_info["damage"])
    adjusted_user_damage = SQGetSlimeDamage(slime_info["defense"], player_base_damage) # reused because why not.
    
    fight_msg = await ctx.respond(f"You encountered a {slime_info['name']}!")
    
    embed = discord.Embed(
        title=slime_info['name'],
        description=slime_info['description'],
        color=discord.Color.blue()
    )
    
    while True:
        
        await asyncio.sleep(ASYNCIO_SLEEP_DELAY)
        
        embed.clear_fields()
        embed.add_field(name="Slime Health", value=f"{slime_info['health']}", inline=True)
        embed.add_field(name="Your Health", value=f"{player_base_health}", inline=True)
        embed.add_field(name="Your turn(s)", value=f"{battle_state['player_turn_count']}", inline=True)
        embed.add_field(name="Slime turn(s)", value=f"{battle_state['slime_turn_count']}", inline=True)
        
        if slime_info["health"] <= 0:
            await ctx.send(f"You defeated the {slime_info['name']}!")
            #TODO: get the rewards.
            
            break
        
        if player_base_health <= 0:
            await ctx.send(f"You were defeated by the {slime_info['name']}!")
            player_base_health = 0 # just in case, to avoid negative health values.
            break
        
        if battle_state['is_running']:
            await ctx.send(f"You ran away from the {slime_info['name']}!")
            break
        
        # just in case.
        if battle_state['player_turn_count'] >= 10 or battle_state['slime_turn_count'] >= 10:
            battle_state['player_turn_count'] = 0
            battle_state['slime_turn_count'] = 0
        
        if battle_state['player_turn_count'] < 0:
            
            # I think the slime should automatically attack the player if the player has no turns left.
            # In my eyes, this is probably fair.
            player_base_health -= adjusted_slime_damage
            battle_state['player_turn_count'] += 1
            
            await ctx.send(f"The {slime_info['name']} attacked you for {adjusted_slime_damage} damage! Your health is now {player_base_health}.", delete_after=MESSAGE_DELETE_DELAY)
            
            continue
            
        if battle_state['slime_turn_count'] < 0:
            slime_choice = "nothing"
            battle_state['slime_turn_count'] += 1
        else:
            slime_choice = random.choice(["attack", "block", "parry", "nothing"])
        
        battle_view = SQAttackUI(slime_info, author, adjusted_user_damage, slime_choice, battle_state)
        
        await fight_msg.edit(embed=embed, view=battle_view)
        await battle_view.wait()
    
    # update the player's health in the database after the battle.
    sq_cursor.execute(
        "UPDATE players SET health = ? WHERE user_id = ?",
        (player_base_health, user_id)
    )
    
    sq_connection.commit()
    