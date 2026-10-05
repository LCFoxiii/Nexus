from core.init_discord import *
from ..helpers.delays import *
from ..helpers.user_exists import *
from ..helpers.items import *
from ..helpers.put_in_inventory import *


import asyncio

# welcome to an over the top inventory system.
# I know this is overkill lmao.

SELECTED_ITEM = "->" # cursor's design.
INVENTORY_SLOT_START = 1
INVENTORY_SLOT_END = 32
INVENTORY_SLOT_LAYOUT = [
    ("Armor", HELMET, "Helmet"),
    ("Armor", CHESTPLATE, "Chestplate"),
    ("Armor", LEGGINGS, "Leggings"),
    ("Armor", BOOTS, "Boots"),
    ("Weapons", WEAPON, "Weapon"),
    ("Weapons", SHIELD, "Shield"),
] + [
    ("Items", slot, f"Slot {slot}")
    for slot in range(INVENTORY_SLOT_START, INVENTORY_SLOT_END + 1)
]


def SQInventorySlotHasNoItems(slot_entry):
    return slot_entry is None or slot_entry.get("item_id") is None


def build_inventory_sections(inventory_items, cursor_position):
    inventory_by_slot = {
        slot: {
            "item_id": item_id,
            "quantity": quantity,
        }
        for item_id, quantity, slot in inventory_items
    }

    sections = {
        "Armor": [],
        "Weapons": [],
        "Items": [],
    }

    slot_entries = []

    for index, (section_name, slot, display_name) in enumerate(INVENTORY_SLOT_LAYOUT):
        inventory_entry = inventory_by_slot.get(slot)

        if SQInventorySlotHasNoItems(inventory_entry):
            line = f"{display_name}: Empty"
            slot_entries.append({
                "slot": slot,
                "item_id": None,
                "quantity": None,
                "section": section_name,
                "display_name": display_name,
            })
        else:
            item_id = inventory_entry["item_id"]
            quantity = inventory_entry["quantity"]
            item_name = items_dict.get(item_id, {}).get("name", f"Item {item_id}")
            line = f"{display_name}: {item_name} x{quantity}"
            slot_entries.append({
                "slot": slot,
                "item_id": item_id,
                "quantity": quantity,
                "section": section_name,
                "display_name": display_name,
            })

        if index == cursor_position:
            line = f"{SELECTED_ITEM} {line}"

        sections[section_name].append(line)

    return sections, slot_entries

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
    def __init__(self, author, exit_main_loop, main_msg, slot_entries, cursor_position):
        super().__init__()
        self.author = author
        self.exit_main_loop = exit_main_loop
        self.main_msg = main_msg
        self.slot_entries = slot_entries
        self.cursor_position = cursor_position
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your inventory!", delete_after=MESSAGE_DELETE_DELAY)
            return False
        return True
    
    @discord.ui.button(label="Up", style=discord.ButtonStyle.primary)
    async def up_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # move cursor up (wrap around)
        if self.slot_entries:
            self.cursor_position = (self.cursor_position - 1) % len(self.slot_entries)
        await interaction.response.defer()
        self.stop()
    
    @discord.ui.button(label="Down", style=discord.ButtonStyle.primary)
    async def down_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # move cursor down (wrap around)
        if self.slot_entries:
            self.cursor_position = (self.cursor_position + 1) % len(self.slot_entries)
        await interaction.response.defer()
        self.stop()
        
    #TODO: Add a "Move" button to move items between slots.
    # if there is an item in that slot, it will give an option to swap or cancel.
    # and if there is no item in that slot, it will move the item to that slot.
    
    @discord.ui.button(label="Move", style=discord.ButtonStyle.secondary)
    async def move_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Plans:
        # 1. create a list with a size of two. (from, to)
        # 1,1. Slot 0 could be a slot where the item is temporarily stored for swapping.
        # 2. create a counter for the number of moves made for the counter list (0 -> 1)
        # 3. everytime this button is pressed, it will store the item id on the list, indexed by the counter.
        # 3,1. if there's nothing there, reset the whole move process and exit the move mode.
        # 4. If the counter is 1, first it will move the "from" spot to slot 0, then move the "to" spot to "from", and slot 0 to "to".
        # 4,1. If the "to" spot is empty, it will just move the item to that spot.
        
        self.stop()
    
    @discord.ui.button(label="Inspect", style=discord.ButtonStyle.secondary)
    async def inspect_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        exit_loop = False
        # determine selected item id from cursor
        if not self.slot_entries:
            await interaction.response.send_message("No item selected.", delete_after=MESSAGE_DELETE_DELAY)
            self.stop()
            return

        selected_slot = self.slot_entries[self.cursor_position]
        selected_item_id = selected_slot["item_id"]

        if SQInventorySlotHasNoItems(selected_slot):
            await interaction.response.send_message("That slot is empty.", delete_after=MESSAGE_DELETE_DELAY)
            self.stop()
            return

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
    
    # 1. get the inventory items from the database
    inventory_items = sq_cursor.execute(
        f"SELECT item_id, quantity, slot FROM {TABLE_INVENTORY} WHERE {ID_NAME} = ? ORDER BY slot ASC",
        (user_id,)
    ).fetchall()

    # 2. categorize inventory entries into weapons, armor, and regular items
    sections, slot_entries = build_inventory_sections(inventory_items, cursor_position)
    if slot_entries:
        cursor_position %= len(slot_entries)

    # build initial embed with separate fields
    embed = discord.Embed(title=f"{ctx.author.name}'s Inventory", color=discord.Color.blue())
    embed.add_field(name="Armor", value="\n".join(sections["Armor"]) if sections["Armor"] else "None", inline=False)
    embed.add_field(name="Weapons", value="\n".join(sections["Weapons"]) if sections["Weapons"] else "None", inline=False)
    embed.add_field(name="Items", value="\n".join(sections["Items"]) if sections["Items"] else "Your inventory is empty.", inline=False)
    
    # main loop for the inventory UI
    while True:
        
        if exit_main_loop:
            break
        
        await asyncio.sleep(ASYNCIO_SLEEP_DELAY)
        
        # create view with current cursor position
        inventory_view = SQInventoryMainUI(ctx.author, exit_main_loop, main_msg, slot_entries, cursor_position)

        sections, slot_entries = build_inventory_sections(inventory_items, cursor_position)
        if slot_entries:
            cursor_position %= len(slot_entries)

        embed = discord.Embed(title=f"{ctx.author.name}'s Inventory", color=discord.Color.blue())
        embed.add_field(name="Armor", value="\n".join(sections["Armor"]) if sections["Armor"] else "None", inline=False)
        embed.add_field(name="Weapons", value="\n".join(sections["Weapons"]) if sections["Weapons"] else "None", inline=False)
        embed.add_field(name="Items", value="\n".join(sections["Items"]) if sections["Items"] else "Your inventory is empty.", inline=False)

        await main_msg.edit(embed=embed, view=inventory_view)
        await inventory_view.wait()

        # pull updated cursor and exit flag from view
        cursor_position = inventory_view.cursor_position
        exit_main_loop = inventory_view.exit_main_loop
    await ctx.respond("Exited inventory.", delete_after=MESSAGE_DELETE_DELAY)