from core.init_discord import *
from ..helpers.delays import *
from ..helpers.user_exists import *
from ..helpers.items import *

import asyncio

# welcome to an over the top inventory system.
# I know this is overkill lmao.

SELECTED_ITEM = "->" # cursor's design.

class SQInventoryInspectEntries(discord.ui.View):
    def __init__(self, author, exit_loop):
        super().__init__()
        self.author = author
        self.exit_loop = exit_loop
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="Use", style=discord.ButtonStyle.primary)
    async def use(self, button: discord.ui.Button, interaction: discord.Interaction):
        # TODO: Implement check if this item is usable.
        # TODO: If item is equip / unequippable, change the button to "Equip" or "Unequip" depending on the state of the item.
        
        await interaction.response.send_message(f"TODO: Implement USE functionality.", delete_after=MESSAGE_DELETE_DELAY)
        self.stop()
    
    @discord.ui.button(label="Throw", style=discord.ButtonStyle.danger)
    async def throw(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(f"TODO: Implement THROW functionality.", delete_after=MESSAGE_DELETE_DELAY)
        self.stop()
        
    @discord.ui.button(label="Quick Sell", style=discord.ButtonStyle.success)
    async def quick_sell(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(f"TODO: Implement QUICK SELL functionality.", delete_after=MESSAGE_DELETE_DELAY)
        self.stop()
        
    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def exit_loop(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Exiting item inspection.", delete_after=MESSAGE_DELETE_DELAY)
        self.exit_loop = True
        self.stop()

class SQInventoryMainUI(discord.ui.View):
    def __init__(self, author, exit_main_loop, main_msg, item_ids, cursor_position=0):
        super().__init__()
        self.author = author
        self.exit_main_loop = exit_main_loop
        self.main_msg = main_msg
        # list of item ids in the inventory and current cursor position
        self.item_ids = item_ids
        self.cursor_position = cursor_position
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your inventory!", delete_after=MESSAGE_DELETE_DELAY)
            return False
        return True
    
    @discord.ui.button(label="Up", style=discord.ButtonStyle.primary)
    async def up_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # move cursor up (wrap around)
        if self.item_ids:
            self.cursor_position = (self.cursor_position - 1) % len(self.item_ids)
        await interaction.response.defer()
        self.stop()
    
    @discord.ui.button(label="Down", style=discord.ButtonStyle.primary)
    async def down_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # move cursor down (wrap around)
        if self.item_ids:
            self.cursor_position = (self.cursor_position + 1) % len(self.item_ids)
        await interaction.response.defer()
        self.stop()
        
    #TODO: Add a "Move" button to move items between slots.
    
    @discord.ui.button(label="Inspect", style=discord.ButtonStyle.secondary)
    async def inspect_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        exit_loop = False
        # determine selected item id from cursor
        if not self.item_ids:
            await interaction.response.send_message("No item selected.", delete_after=MESSAGE_DELETE_DELAY)
            self.stop()
            return

        selected_item_id = self.item_ids[self.cursor_position]
        embed = discord.Embed(
            title=f"{items_dict[selected_item_id]['name']} - Inspection",
            description=f"{items_dict[selected_item_id]['description']}",
            color=discord.Color.green()
        )
        
        # TODO: Add more detailed inspection info
        # this could include stats, sell value, rarity, etc. 
        # or something that is not null or none.
        
        while not exit_loop:
            await asyncio.sleep(ASYNCIO_SLEEP_DELAY)
            
            inspect_view = SQInventoryInspectEntries(self.author, exit_loop)
            await self.main_msg.edit(embed=embed, view=inspect_view)
            await inspect_view.wait()
            
            exit_loop = inspect_view.exit_loop
        
        self.stop()
        
    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def exit_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Exiting inventory.", delete_after=MESSAGE_DELETE_DELAY)
        self.exit_main_loop = True
        self.stop()

@slimequest.command(name="inventory", description="View your inventory.")
async def inventory(ctx: discord.ApplicationContext):
    await ctx.defer()
    
    if await SQUserExistsMessage(ctx):
        return
    
    user_id = ctx.author.id
    exit_main_loop = False
    main_msg = await ctx.respond("Please wait.")
    cursor_position = 0
    inventory_strings = []
    # cursor_position = 0 # for selecting items in the future.
    
    # 1. get the inventory items from the database
    inventory_items = sq_cursor.execute(
        f"SELECT item_id, quantity, slot FROM {TABLE_INVENTORY} WHERE {ID_NAME} = ? ORDER BY slot ASC",
        (user_id,)
    ).fetchall()
    
    item_ids = [item[0] for item in inventory_items]
    quantities = [item[1] for item in inventory_items]
    slots = [item[2] for item in inventory_items]
    
    # 2. categorize inventory entries into weapons, armor, and regular items
    weapons = []
    armor = []
    items_general = []

    for i in range(len(item_ids)):
        item_id = item_ids[i]
        quantity = quantities[i]
        slot = slots[i]
        item_name = items_dict[item_id]["name"]
        # prefix selected cursor marker when this entry is selected
        prefix = SELECTED_ITEM + " " if i == cursor_position and item_ids else ""

        if slot == WEAPON or slot == SHIELD:
            label = "Weapon" if slot == WEAPON else "Shield"
            weapons.append(f"{prefix}{label}: {item_name} x{quantity}")
        elif slot in (HELMET, CHESTPLATE, LEGGINGS, BOOTS):
            # map special armor slots to names
            slot_map = {HELMET: "Helmet", CHESTPLATE: "Chestplate", LEGGINGS: "Leggings", BOOTS: "Boots"}
            armor.append(f"{prefix}{slot_map.get(slot, f'Slot {slot}')}: {item_name} x{quantity}")
        else:
            # regular inventory slots (positive integers)
            items_general.append(f"{prefix}Slot {slot}: {item_name} x{quantity}")

    # build initial embed with separate fields
    embed = discord.Embed(title=f"{ctx.author.name}'s Inventory", color=discord.Color.blue())
    embed.add_field(name="Armor", value="\n".join(armor) if armor else "None", inline=False)
    embed.add_field(name="Weapons", value="\n".join(weapons) if weapons else "None", inline=False)
    embed.add_field(name="Items", value="\n".join(items_general) if items_general else "Your inventory is empty.", inline=False)
    
    # main loop for the inventory UI
    while True:
        
        if exit_main_loop:
            break
        
        await asyncio.sleep(ASYNCIO_SLEEP_DELAY)
        
        # create view with current cursor position
        inventory_view = SQInventoryMainUI(ctx.author, exit_main_loop, main_msg, item_ids, cursor_position)

        # TODO: Put below into a function.
        # rebuild categorized lists each loop in case of cursor changes
        weapons = []
        armor = []
        items_general = []
        for i in range(len(item_ids)):
            item_id = item_ids[i]
            quantity = quantities[i]
            slot = slots[i]
            item_name = items_dict[item_id]["name"]
            # prefix selected cursor marker when this entry is selected
            prefix = SELECTED_ITEM + " " if i == cursor_position and item_ids else ""

            if slot == WEAPON or slot == SHIELD:
                label = "Weapon" if slot == WEAPON else "Shield"
                weapons.append(f"{prefix}{label}: {item_name} x{quantity}")
            elif slot in (HELMET, CHESTPLATE, LEGGINGS, BOOTS):
                slot_map = {HELMET: "Helmet", CHESTPLATE: "Chestplate", LEGGINGS: "Leggings", BOOTS: "Boots"}
                armor.append(f"{prefix}{slot_map.get(slot, f'Slot {slot}')}: {item_name} x{quantity}")
            else:
                items_general.append(f"{prefix}Slot {slot}: {item_name} x{quantity}")

        embed = discord.Embed(title=f"{ctx.author.name}'s Inventory", color=discord.Color.blue())
        embed.add_field(name="Armor", value="\n".join(armor) if armor else "None", inline=False)
        embed.add_field(name="Weapons", value="\n".join(weapons) if weapons else "None", inline=False)
        embed.add_field(name="Items", value="\n".join(items_general) if items_general else "Your inventory is empty.", inline=False)

        await main_msg.edit(embed=embed, view=inventory_view)
        await inventory_view.wait()

        # pull updated cursor and exit flag from view
        cursor_position = inventory_view.cursor_position
        exit_main_loop = inventory_view.exit_main_loop
    await ctx.respond("Exited inventory.", delete_after=MESSAGE_DELETE_DELAY)