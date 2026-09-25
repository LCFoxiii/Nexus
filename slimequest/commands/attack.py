from core.init_discord import *
from ..helpers.user_exists import *
from ..helpers.slime_damage import *
from ..helpers.slimes import *
from ..helpers.adjust_to_percentage import *

from general_helpers.db_helpers import *

from ..init.database.creation import *

import random
import asyncio

MESSAGE_DELETE_DELAY = 1.0 # seconds
ASYNCIO_SLEEP_DELAY  = 0.5 # seconds

# possible slime actions
ATTACK  = "attack"
BLOCK   = "block"
PARRY   = "parry"
NOTHING = "nothing"

# NOTE: d1f <= chance means success, d1f > chance means failure. (d1f = random.uniform(0, 1))

class SQAttackUI(discord.ui.View):
    
    def __init__(self, slime_info, author, adjusted_player_damage, slime_choice, battle_state, escape_chance, player_dexterity, player_health):
        super().__init__()
        self.author = author
        
        self.slime_info   = slime_info
        self.slime_choice = slime_choice
        
        self.escape_chance = escape_chance
        self.battle_state  = battle_state
        
        self.player_dexterity       = player_dexterity
        self.player_health          = player_health
        self.adjusted_player_damage = adjusted_player_damage
        
        # a bit redundant, but i just wanna mess around.
        self.escape_messages = ["failed to escape", "successfully escaped"] 
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your battle!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Attack", row=0, style=discord.ButtonStyle.red)
    async def attack_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.slime_choice == ATTACK:
            await interaction.response.send_message("TEMP: both attacked, clashed, no damage dealt, -1 for both.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["slime_turn_count"] = -1
            self.battle_state["player_turn_count"] = -1
        elif self.slime_choice == BLOCK:
            #TODO: Implement a chance for the player to break through the slime's block and deal damage, based on the player's sword PEN stat.
            await interaction.response.send_message("TEMP: you attack, the slime blocks. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["player_turn_count"] = -1
        elif self.slime_choice == PARRY:
            await interaction.response.send_message("TEMP: you attack, the slime parries. -2 turns.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["player_turn_count"] = -2
        elif (self.slime_choice == NOTHING):
            
            #TODO: also add a crit chance stat to the player (0-200)
            critical_chance = SQAdjustToPercentage(self.player_dexterity, 0, 100)
            
            d1f = random.uniform(0, 1)
            
            is_critical = d1f <= critical_chance
            self.slime_info["health"] -= self.adjusted_player_damage * (1 + is_critical)
            
            if d1f <= critical_chance:
                await interaction.response.send_message(f"CRITICAL HIT! You dealt {self.adjusted_player_damage * 2} damage to the slime!", delete_after=MESSAGE_DELETE_DELAY)
            else:
                await interaction.response.send_message(f"+{self.adjusted_player_damage} damage to the slime!", delete_after=MESSAGE_DELETE_DELAY)

        self.stop()
    
    @discord.ui.button(label="Defend", row=0, style=discord.ButtonStyle.green)
    async def defend_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        #TODO: Add defense success & failure chance mechanic based on player's DEX stat. and also the shield's base block percentage stat.
        #TODO: Add slime's attack penetration mechanic based on slime's PEN stat. (0-100)
        #for now, 100% success rate of blocking the slime's attack. and no penetration damage.
        
        if (self.slime_choice == ATTACK):
            await interaction.response.send_message("TEMP: you defend, slime attacked, no damage dealt. -1 turn for slime.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["slime_turn_count"] = -1
        elif (self.slime_choice == BLOCK):
            await interaction.response.send_message("TEMP: both defended, no damage dealt, -1 for both.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["slime_turn_count"] = -1
            self.battle_state["player_turn_count"] = -1
        elif (self.slime_choice == PARRY):
            await interaction.response.send_message("TEMP: you defend, slime parries, no damage dealt. -1 for both.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["slime_turn_count"] = -1
            self.battle_state["player_turn_count"] = -1
        else:
            await interaction.response.send_message("TEMP: You defend, slime did nothing. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["player_turn_count"] = -1
        
        self.stop()
        
    @discord.ui.button(label="Parry", row=0, style=discord.ButtonStyle.blurple)
    async def parry_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        d1f = random.uniform(0, 1)
        parry_chance = SQAdjustToPercentage(self.player_dexterity, 0, 100)
        
        if (d1f >= parry_chance):
            await interaction.response.send_message(f"TEMP: you failed, -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["player_turn_count"] = -1
            
            self.stop()
            return
            
        if (self.slime_choice == ATTACK):
            await interaction.response.send_message("TEMP: you parry, slime attacked, no damage dealt. -2 turns for slime.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["slime_turn_count"] = -2
        elif (self.slime_choice == BLOCK):
            await interaction.response.send_message("TEMP: you parry, slime blocked, no damage dealt. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["player_turn_count"] = -1
        elif (self.slime_choice == PARRY):
            await interaction.response.send_message("TEMP: both parried, no damage dealt. -1 for both.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["slime_turn_count"] = -1
            self.battle_state["player_turn_count"] = -1
        else:
            await interaction.response.send_message("TEMP: You parry, slime did nothing. -1 turn.", delete_after=MESSAGE_DELETE_DELAY)
            self.battle_state["player_turn_count"] = -1
            
        self.stop()
        
    @discord.ui.button(label="Run", row=0, style=discord.ButtonStyle.blurple)
    async def run_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        d1f = random.uniform(0, 1)
        escaped = d1f <= self.escape_chance
        
        await interaction.response.send_message(f"You've {self.escape_messages[escaped]} from the slime! ({self.escape_chance}/{d1f})", ephemeral=True, delete_after=MESSAGE_DELETE_DELAY)
        self.battle_state["is_running"] = escaped
        self.battle_state["player_turn_count"] = -1 if not self.battle_state["is_running"] else 0
        self.stop()

@slimequest.command(name="attack", description="TEMP: Creates a slime and put you in a simulated battle with it.")
async def attack(ctx: discord.ApplicationContext):
    if await SQUserExistsMessage(ctx):
        return
    
    random_slime = random.choice(list(slime_entries.keys()))
    
    # Battle initializations
    author = ctx.author
    
    slime_info = slime_entries[random_slime]
    battle_states = {
        "player_turn_count": 0,
        "slime_turn_count": 0,
        "is_running": False
    }
    
    slime_name        = slime_info['name']
    slime_description = slime_info['description']
    slime_damage      = slime_info['damage']
    slime_defense     = slime_info['defense']
    slime_speed       = slime_info['speed']
    
    embed = discord.Embed(
        title=slime_name,
        description=slime_description,
        color=discord.Color.blue()
    )
    
    user_id = author.id
    
    # grab some stuff from the database.
    player_base_damage, player_defense, player_health, player_speed, player_dexterity = DBGrab(user_id, TABLE_STATS, ["damage", "defense", "health", "speed", "dexterity"], ID_NAME, sq_cursor)
    
    # adjustions
    adjusted_slime_damage   = SQGetDamage(player_defense, slime_damage)
    adjusted_player_damage  = SQGetDamage(slime_defense, player_base_damage) # reused because why not.
    escape_chance           = SQAdjustToPercentage(player_speed, slime_speed, 200)
    
    fight_msg = await ctx.respond(f"You encountered a {slime_name}!")
    
    while True:
        slime_health = slime_info['health']
        
        await asyncio.sleep(ASYNCIO_SLEEP_DELAY)
        
        embed.clear_fields()
        embed.add_field(name="Slime Health",  value=f"{slime_health}", inline=True)
        embed.add_field(name="Your Health",   value=f"{player_health}", inline=True)
        embed.add_field(name="Your turn(s)",  value=f"{battle_states['player_turn_count']}", inline=True)
        embed.add_field(name="Slime turn(s)", value=f"{battle_states['slime_turn_count']}", inline=True)
        
        if slime_health <= 0:
            await ctx.send(f"You defeated the {slime_name}!")
            #TODO: get the rewards.
            
            break
        
        if player_health <= 0:
            await ctx.send(f"You were defeated by the {slime_name}!")
            player_health = 0 # just in case, to avoid negative health values.
            break
        
        if battle_states['is_running']:
            await ctx.send(f"You ran away from the {slime_name}!")
            break
        
        # This should make the slime attack the player until the player have turns again.
        if battle_states['player_turn_count'] < 0 and battle_states['slime_turn_count'] >= 0:
            player_health -= adjusted_slime_damage
            battle_states['player_turn_count'] += 1
            
            await ctx.send(f"The {slime_name} attacked you for {adjusted_slime_damage} damage! Your health is now {player_health}.", delete_after=MESSAGE_DELETE_DELAY)
            continue
        
        # TODO: Implement something that makes the slime's choice more intelligent, based on the slime's INT stat.
        
        # this has a chance of beating your ass, so i hope you are lucky.
        slime_choice = random.choice([ATTACK, BLOCK, PARRY, NOTHING]) if battle_states['slime_turn_count'] >= 0 else NOTHING
        battle_states['slime_turn_count'] += battle_states['slime_turn_count'] < 0
        
        battle_view = SQAttackUI(slime_info, author, adjusted_player_damage, slime_choice, battle_states, escape_chance, player_dexterity, player_health)
        
        await fight_msg.edit(embed=embed, view=battle_view)
        await battle_view.wait()
    
    # update the player's health in the database after the battle.
    DBUpdate(user_id, TABLE_STATS, {"health": player_health}, ID_NAME, sq_cursor, sq_connection)