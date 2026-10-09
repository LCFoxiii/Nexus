from .items import *
from core.init_discord import *
from ..init.database.creation import *

# I gave up trying to split these into separate files.
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


def SQResolveInventoryCursorIndex(category, cat_slot):
    category = category.strip().lower()

    if category in ["armor", "armors", ARMOR_ITEM]:
        armor_slots = [HELMET, CHESTPLATE, LEGGINGS, BOOTS]
        if 1 <= cat_slot <= len(armor_slots):
            return next(
                index
                for index, (_, slot, _) in enumerate(INVENTORY_SLOT_LAYOUT)
                if slot == armor_slots[cat_slot - 1]
            )
    elif category in ["weapons", "weapon", WEAPON_ITEM, SHIELD_ITEM]:
        weapon_slots = [WEAPON, SHIELD]
        if 1 <= cat_slot <= len(weapon_slots):
            return next(
                index
                for index, (_, slot, _) in enumerate(INVENTORY_SLOT_LAYOUT)
                if slot == weapon_slots[cat_slot - 1]
            )
    elif category in ["items", "item", REGULAR_ITEM]:
        if INVENTORY_SLOT_START <= cat_slot <= INVENTORY_SLOT_END:
            return next(
                index
                for index, (_, slot, _) in enumerate(INVENTORY_SLOT_LAYOUT)
                if slot == cat_slot
            )

    return None


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


def SQBuildInventoryEmbed(author_name, sections):
    embed = discord.Embed(title=f"{author_name}'s Inventory", color=discord.Color.blue())
    embed.add_field(name="Armor", value="\n".join(sections["Armor"]) if sections["Armor"] else "None", inline=False)
    embed.add_field(name="Weapons", value="\n".join(sections["Weapons"]) if sections["Weapons"] else "None", inline=False)
    embed.add_field(name="Items", value="\n".join(sections["Items"]) if sections["Items"] else "Your inventory is empty.", inline=False)
    return embed


def SQBuildInventoryState(author_name, inventory_items, cursor_position):
    sections, slot_entries = build_inventory_sections(inventory_items, cursor_position)
    return SQBuildInventoryEmbed(author_name, sections), sections, slot_entries

def SQStatToString(stat_string):
    return str(stat_string).replace('_', ' ').title()