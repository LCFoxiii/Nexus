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


def SQMoveItemToEmptySlot(user_id, slot_from, slot_to):
    sq_cursor.execute(
        f"""
            UPDATE {TABLE_INVENTORY}
            SET slot = ?
            WHERE {ID_NAME} = ?
              AND slot = ?
        """,
        (slot_to, user_id, slot_from)
    )
    sq_connection.commit()


def SQGetInventoryItems(user_id):
    return sq_cursor.execute(
        f"SELECT item_id, quantity, slot FROM {TABLE_INVENTORY} WHERE {ID_NAME} = ? ORDER BY slot ASC",
        (user_id,)
    ).fetchall()


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

class SQInventorySwapItemsConfirmation(discord.ui.View):
    def __init__(self, author):
        super().__init__()
        self.author = author
        self.result = None
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm_swap(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.result = True
        await interaction.response.defer()
        self.stop()
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.result = False
        await interaction.response.defer()
        self.stop()

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
    def __init__(self, author, exit_main_loop, main_msg, slot_entries, cursor_position, move_entries):
        super().__init__()
        self.author = author
        self.exit_main_loop = exit_main_loop
        self.main_msg = main_msg
        self.slot_entries = slot_entries
        self.cursor_position = cursor_position
        self.move_entries = move_entries
        
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
    
    @discord.ui.button(label="Move", style=discord.ButtonStyle.secondary)
    async def move_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        
        # 1. Get the selected slot and item id.
        selected_slot = self.slot_entries[self.cursor_position]
        
        # 2. counter stuff
        if (self.move_entries["move_counter"] == 0):
            if SQInventorySlotHasNoItems(selected_slot):
                await interaction.response.send_message("Select a slot with an item first.", delete_after=MESSAGE_DELETE_DELAY)
                self.stop()
                return

            # first move, store the "from" slot and item id.
            self.move_entries["move_list"][0] = selected_slot
            self.move_entries["move_counter"] = 1
            await interaction.response.send_message("Please select the destination slot to move the item to.", delete_after=MESSAGE_DELETE_DELAY)
        elif (self.move_entries["move_counter"] == 1):
            # second move, store the "to" slot and item id.
            self.move_entries["move_list"][1] = selected_slot
            self.move_entries["move_counter"] = 0
            
            from_slot = self.move_entries["move_list"][0]
            to_slot = self.move_entries["move_list"][1]
            
            if (from_slot["slot"] == to_slot["slot"]):
                await interaction.response.send_message("Cannot move to the same slot.", delete_after=MESSAGE_DELETE_DELAY)
                self.stop()
                return
            
            # 3. Move directly into empty slots; confirm swaps for occupied slots.
            if SQInventorySlotHasNoItems(from_slot) and SQInventorySlotHasNoItems(to_slot):
                await interaction.response.send_message("Both slots are empty. Cannot move.", delete_after=MESSAGE_DELETE_DELAY)

            elif SQInventorySlotHasNoItems(from_slot) or SQInventorySlotHasNoItems(to_slot):
                source_slot = from_slot if not SQInventorySlotHasNoItems(from_slot) else to_slot
                target_slot = to_slot if source_slot is from_slot else from_slot

                SQMoveItemToEmptySlot(self.author.id, source_slot["slot"], target_slot["slot"])
                await interaction.response.send_message("Item moved successfully.", delete_after=MESSAGE_DELETE_DELAY)

            else:
                confirm_view = SQInventorySwapItemsConfirmation(self.author)
                await interaction.response.send_message(
                    (
                        f"Swap {from_slot['display_name']} with {to_slot['display_name']}?"
                    ),
                    view=confirm_view,
                    ephemeral=True,
                )
                await confirm_view.wait()

                if confirm_view.result:
                    result_swap, reason = SQSwap(
                        self.author.id,
                        from_slot["item_id"],
                        to_slot["item_id"],
                        from_slot["slot"],
                        to_slot["slot"],
                    )

                    await interaction.followup.send(
                        reason if not result_swap else "Items swapped successfully.",
                        delete_after=MESSAGE_DELETE_DELAY,
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send("Item swap canceled.", delete_after=MESSAGE_DELETE_DELAY, ephemeral=True)
                
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
        
    # TODO: A button that allows you to type in a category and slot number.
    # this could probably replace the up and down buttons.
    # layout: "category:slot_number"
    # example:
    # "armor:1" would select the first armor slot (helmet)
    # "weapons:2" would select the second weapon slot (shield)
    # "items:5" would select the fifth item slot (slot 5)
        
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
    inventory_items = SQGetInventoryItems(user_id)

    # 2. categorize inventory entries into weapons, armor, and regular items
    sections, slot_entries = build_inventory_sections(inventory_items, cursor_position)
    if slot_entries:
        cursor_position %= len(slot_entries)

    # build initial embed with separate fields
    embed = discord.Embed(title=f"{ctx.author.name}'s Inventory", color=discord.Color.blue())
    embed.add_field(name="Armor", value="\n".join(sections["Armor"]) if sections["Armor"] else "None", inline=False)
    embed.add_field(name="Weapons", value="\n".join(sections["Weapons"]) if sections["Weapons"] else "None", inline=False)
    embed.add_field(name="Items", value="\n".join(sections["Items"]) if sections["Items"] else "Your inventory is empty.", inline=False)
    
    # initialize move entries
    move_list = [None, None]  # [from_slot, to_slot]
    move_counter = 0
    move_entries = {
        "move_list": move_list,
        "move_counter": move_counter
    }
    
    # main loop for the inventory UI
    while True:
        
        if exit_main_loop:
            break
        
        await asyncio.sleep(ASYNCIO_SLEEP_DELAY)

        inventory_items = SQGetInventoryItems(user_id)

        sections, slot_entries = build_inventory_sections(inventory_items, cursor_position)
        if slot_entries:
            cursor_position %= len(slot_entries)
        
        # create view with current cursor position
        inventory_view = SQInventoryMainUI(ctx.author, exit_main_loop, main_msg, slot_entries, cursor_position, move_entries)

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