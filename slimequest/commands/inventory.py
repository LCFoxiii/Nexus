from ..helpers.delays import *
from ..helpers.user_exists import *
from ..helpers.put_in_inventory import *
from ..helpers.inventory_helpers import *

import re
import asyncio

class SQThrowItemConfirmation(discord.ui.View):
    def __init__(self, author, confirmation):
        super().__init__()
        self.author = author
        self.confirmation = confirmation
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="Throw", style=discord.ButtonStyle.danger)
    async def confirm_swap(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.confirmation = True
        await interaction.response.defer()
        self.stop()
            
    @discord.ui.button(label="Keep", style=discord.ButtonStyle.success)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.confirmation = False
        await interaction.response.defer()
        self.stop()

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
    def __init__(self, author, exit_loop, slot_entries, cursor_position):
        super().__init__()
        self.author = author
        self.exit_loop = exit_loop
        self.slot_entries = slot_entries
        self.cursor_position = cursor_position
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="Use", style=discord.ButtonStyle.primary)
    async def use(self, button: discord.ui.Button, interaction: discord.Interaction):
        # TODO: Implement check if this item is usable.
        # TODO: If item is equip / unequippable, change the button to "Equip" or "Unequip" depending on the state of the item.
        
        await interaction.response.send_message("TODO: Implement USE functionality.", ephemeral=True)
        self.stop()
    
    @discord.ui.button(label="Throw", style=discord.ButtonStyle.danger)
    async def throw(self, button: discord.ui.Button, interaction: discord.Interaction):
        # I guess for now i could just remove the item from the inventory,
        # but I also want to make it so that other players can pick it up randomly.
        # But that's for later.
        
        await interaction.response.send_message("Please type in how much of the item you want to throw away:", ephemeral=True)
        
        try:
            encoded = await bot.wait_for(
                "message",
                check=lambda message: message.author == self.author and message.channel == interaction.channel,
                timeout=60,
            )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Throw timed out.",
                ephemeral=True,
            )
            self.stop()
            return
        
        match = re.fullmatch(r"([1-9]\d*)", encoded.content.strip())
        if not match:
            await interaction.followup.send(
                "Invalid format. Please enter a positive integer.",
                ephemeral=True,
            )
            self.stop()
            return
        
        amount = int(match.group(1))
        confirmation = SQThrowItemConfirmation(self.author, None)
        await interaction.followup.send(f"Are you sure you want to throw away {amount} of this item?", view=confirmation, ephemeral=True)
        await confirmation.wait()

        if not hasattr(self, "slot_entries") or not self.slot_entries:
            await interaction.followup.send("This item is no longer available to throw away.", ephemeral=True)
            self.stop()
            return

        if confirmation.confirmation:
            selected_slot = self.slot_entries[self.cursor_position]
            SQDeleteItem(self.author.id, selected_slot["slot"], amount)
            await interaction.followup.send(f"Successfully threw away {amount} of the item.", ephemeral=True)
        else:
            await interaction.followup.send("Item throw canceled.", ephemeral=True)
        
        self.stop()
        
    @discord.ui.button(label="Quick Sell", style=discord.ButtonStyle.success)
    async def quick_sell(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("TODO: Implement QUICK SELL functionality.", ephemeral=True)
        self.stop()
        
    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def exit_loop(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Exiting item inspection.", ephemeral=True)
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
            await interaction.response.send_message("This is not your inventory!", ephemeral=True)
            return False
        return True

    async def refresh_inventory_message(self, inventory_items):
        embed, sections, slot_entries = SQBuildInventoryState(self.author.name, inventory_items, self.cursor_position)
        self.slot_entries = slot_entries
        await self.main_msg.edit(embed=embed, view=self)
        return embed, sections, slot_entries
    
    @discord.ui.button(label="Goto", style=discord.ButtonStyle.success)
    async def goto_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Please enter the category and slot number ('category:slot_number'):",
            ephemeral=True,
        )

        try:
            encoded = await bot.wait_for(
                "message",
                check=lambda message: message.author == self.author and message.channel == interaction.channel,
                timeout=60,
            )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Goto timed out.",
                ephemeral=True,
            )
            self.stop()
            return
        
        match = re.fullmatch(r"([a-z]+):([1-9]\d*)", encoded.content.strip().lower())
        if not match:
            await interaction.followup.send(
                "Invalid format. Use 'category:slot_number'.",
                ephemeral=True,
            )
            self.stop()
            return

        category = match.group(1)
        cat_slot = int(match.group(2))
        cursor_index = SQResolveInventoryCursorIndex(category, cat_slot)

        if cursor_index is None:
            await interaction.followup.send(
                "That category or slot does not exist.",
                ephemeral=True,
            )
            self.stop()
            return

        self.cursor_position = cursor_index
        inventory_items = SQGetInventoryItems(self.author.id)
        await self.refresh_inventory_message(inventory_items)
        await interaction.followup.send(f"Moved cursor to {category}:{cat_slot}.", ephemeral=True)
    
    @discord.ui.button(label="Move", style=discord.ButtonStyle.secondary)
    async def move_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        
        # 1. Get the selected slot and item id.
        selected_slot = self.slot_entries[self.cursor_position]
        
        # 2. counter stuff
        if (self.move_entries["move_counter"] == 0):
            if SQInventorySlotHasNoItems(selected_slot):
                await interaction.response.send_message("Select a slot with an item first.", ephemeral=True)
                self.stop()
                return

            # first move, store the "from" slot and item id.
            self.move_entries["move_list"][0] = selected_slot
            self.move_entries["move_counter"] = 1
            await interaction.response.send_message("Please select the destination slot to move the item to.", ephemeral=True)

        elif (self.move_entries["move_counter"] == 1):
            # second move, store the "to" slot and item id.
            self.move_entries["move_list"][1] = selected_slot
            self.move_entries["move_counter"] = 0
            
            from_slot = self.move_entries["move_list"][0]
            to_slot = self.move_entries["move_list"][1]
            
            if (from_slot["slot"] == to_slot["slot"]):
                await interaction.response.send_message("Cannot move to the same slot.", ephemeral=True)
                self.stop()
                return
            
            # 3. Move directly into empty slots; confirm swaps for occupied slots.
            if SQInventorySlotHasNoItems(from_slot) and SQInventorySlotHasNoItems(to_slot):
                await interaction.response.send_message("Both slots are empty. Cannot move.", ephemeral=True)

            elif SQInventorySlotHasNoItems(from_slot) or SQInventorySlotHasNoItems(to_slot):
                source_slot = from_slot if not SQInventorySlotHasNoItems(from_slot) else to_slot
                target_slot = to_slot if source_slot is from_slot else from_slot

                SQMoveItemToEmptySlot(self.author.id, source_slot["slot"], target_slot["slot"])
                await interaction.response.send_message("Item moved successfully.", ephemeral=True)
                inventory_items = SQGetInventoryItems(self.author.id)
                await self.refresh_inventory_message(inventory_items)

            else:
                confirm_view = SQInventorySwapItemsConfirmation(self.author)
                await interaction.response.send_message(f"Swap {from_slot['display_name']} with {to_slot['display_name']}?", view=confirm_view, ephemeral=True)
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
                        ephemeral=True,
                    )
                    inventory_items = SQGetInventoryItems(self.author.id)
                    await self.refresh_inventory_message(inventory_items)
                else:
                    await interaction.followup.send("Item swap canceled.", ephemeral=True)
                
        self.stop()
    
    @discord.ui.button(label="Inspect", style=discord.ButtonStyle.secondary)
    async def inspect_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        exit_loop = False
        
        # determine selected item id from cursor
        if not self.slot_entries:
            await interaction.response.send_message("No item selected.", ephemeral=True)
            self.stop()
            return

        selected_slot = self.slot_entries[self.cursor_position]
        selected_item_id = selected_slot["item_id"]

        if SQInventorySlotHasNoItems(selected_slot):
            await interaction.response.send_message("That slot is empty.", ephemeral=True)
            self.stop()
            return

        embed = discord.Embed(
            title=f"{items_dict[selected_item_id]['name']} - Inspection",
            description=f"{items_dict[selected_item_id]['description']}",
            color=discord.Color.green()
        )
        
        # TODO: Add more detailed inspection info
        # only asset image left, i guess i'll ask someone to make a few assets for the items.
        
        item = items_dict[selected_item_id]
        quantity = selected_slot["quantity"]
        
        values    = item["values"]
        rarity    = SQStatToString(item["rarity"])
        max_stack = item["max_stack"]
        stats     = item["stats"]
        
        stack_string = f"{quantity}/{max_stack}" if max_stack > 1 else "Not stackable"
        
        value_strings = []
        for value_type, value_amount in values.items():
            if value_amount is not None:
                value_strings.append(f"{SQStatToString(value_type)}: {value_amount}")
            
        stats_strings = []
        for stat_type, stat_amount in stats.items():
            if stat_amount is not None:
                stats_strings.append(f"{SQStatToString(stat_type)}: {stat_amount}")
        
        embed.add_field(name="Rarity", value=rarity, inline=True)
        embed.add_field(name="Price", value="\n".join(value_strings), inline=True)
        embed.add_field(name="Stack Size", value=stack_string, inline=True)
        embed.add_field(name="Stats", value="\n".join(stats_strings) if stats_strings else "No useful stats available.", inline=True)

        while not exit_loop:
            await asyncio.sleep(ASYNCIO_SLEEP_DELAY)
            
            inspect_view = SQInventoryInspectEntries(
                self.author,
                exit_loop,
                self.slot_entries,
                self.cursor_position,
            )
            await self.main_msg.edit(embed=embed, view=inspect_view)
            await inspect_view.wait()
            
            exit_loop = inspect_view.exit_loop
        
        self.stop()
        
    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def exit_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Exiting inventory.", ephemeral=True)
        self.exit_main_loop = True
        self.stop()

@slimequest.command(name="inventory", description="View your inventory.")
async def inventory(ctx: discord.ApplicationContext):
    if await SQUserExistsMessage(ctx):
        return

    user_id = ctx.author.id
    exit_main_loop = False
    main_msg = await ctx.respond("Please wait.")
    cursor_position = 0

    # 1. get the inventory items from the database
    inventory_items = SQGetInventoryItems(user_id)

    # 2. categorize inventory entries into weapons, armor, and regular items
    embed, sections, slot_entries = SQBuildInventoryState(ctx.author.name, inventory_items, cursor_position)
    if slot_entries:
        cursor_position %= len(slot_entries)

    # initialize move entries
    move_entries = {
        "move_list": [None, None],  # [from_slot, to_slot]
        "move_counter": 0
    }

    # main loop for the inventory UI
    while True:
        if exit_main_loop:
            break

        await asyncio.sleep(ASYNCIO_SLEEP_DELAY)

        inventory_items = SQGetInventoryItems(user_id)

        embed, sections, slot_entries = SQBuildInventoryState(ctx.author.name, inventory_items, cursor_position)
        if slot_entries:
            cursor_position %= len(slot_entries)

        # create view with current cursor position
        inventory_view = SQInventoryMainUI(ctx.author, exit_main_loop, main_msg, slot_entries, cursor_position, move_entries)

        await main_msg.edit(embed=embed, view=inventory_view)
        await inventory_view.wait()

        # pull updated cursor and exit flag from view
        cursor_position = inventory_view.cursor_position
        exit_main_loop = inventory_view.exit_main_loop

    await main_msg.edit(content="Exited inventory.", embed=None, view=None)