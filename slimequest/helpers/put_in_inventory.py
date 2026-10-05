from .items import *
from ..init.database.creation import *
from general_helpers.db_helpers import *

# returns the amount of items that could not be added to the inventory.
def _validate_custom_slot_item(slot: int, item_id: int) -> None:
    item_type = items_dict[item_id]["item_type"]

    if slot == WEAPON and item_type != WEAPON_ITEM:
        raise ValueError(f"Item {item_id} is not a weapon and cannot be placed in the weapon slot.")
    elif slot == SHIELD and item_type != SHIELD_ITEM:
        raise ValueError(f"Item {item_id} is not a shield and cannot be placed in the shield slot.")
    elif slot in [HELMET, CHESTPLATE, LEGGINGS, BOOTS] and item_type != ARMOR_ITEM:
        raise ValueError(f"Item {item_id} is not armor and cannot be placed in the armor slot.")


def SQPutItemInInventory(
    user_id: int,
    item_id: int,
    quantity: int = 1,
) -> int:
    """
    Adds an item to the player's inventory.

    Existing stacks are filled first.
    If those stacks are full, new stacks are created in the
    lowest available inventory slots.

    Returns:
        int: The amount of items that could NOT be added.
    """

    if quantity <= 0:
        return 0

    item = items_dict.get(item_id)

    if item is None:
        raise ValueError(f"Item {item_id} does not exist.")

    max_stack = item["max_stack"]
    
    # 1. fill existing stacks first

    sq_cursor.execute(
        f"""
            SELECT slot, quantity
            FROM {TABLE_INVENTORY}
            WHERE {ID_NAME} = ?
              AND {ID_NAME_ITEM} = ?
              AND {ID_NAME_INSTANCE} IS NULL
            ORDER BY slot ASC
        """,
        (user_id, item_id)
    )

    existing_stacks = sq_cursor.fetchall()

    for slot, current_quantity in existing_stacks:

        if quantity <= 0:
            break

        # How much space is left in this stack?
        space = max_stack - current_quantity

        if space <= 0:
            continue

        amount_to_add = min(quantity, space)

        sq_cursor.execute(
            f"""
                UPDATE {TABLE_INVENTORY}
                SET quantity = quantity + ?
                WHERE {ID_NAME} = ?
                  AND slot = ?
            """,
            (amount_to_add, user_id, slot)
        )

        quantity -= amount_to_add

    # 2. If everything was added, we're done.

    if quantity <= 0:
        sq_connection.commit()
        return 0

    # 3. Find the lowest available inventory slot.

    sq_cursor.execute(
        f"""
            SELECT slot
            FROM {TABLE_INVENTORY}
            WHERE {ID_NAME} = ?
            ORDER BY slot ASC
        """,
        (user_id,)
    )

    used_slots = {
        row[0]
        for row in sq_cursor.fetchall()
    }

    # 4. Create new stacks until either:
    # - all items have been added
    # - the inventory is full

    slot = 1

    while quantity > 0:

        # find the next available slot.
        while slot in used_slots:
            slot += 1

        amount_to_add = min(quantity, max_stack)

        sq_cursor.execute(
            f"""
                INSERT INTO {TABLE_INVENTORY}
                (
                    {ID_NAME},
                    {ID_NAME_ITEM},
                    quantity,
                    slot
                )
                VALUES (?, ?, ?, ?)
            """,
            (user_id, item_id, amount_to_add, slot)
        )

        used_slots.add(slot)

        quantity -= amount_to_add

        # move to the next slot for another stack.
        slot += 1

    sq_connection.commit()

    # Anything remaining couldn't be added.
    return quantity

def SQPutItemInCustomSlot(
    user_id: int,
    item_id: int,
    slot: int,
    quantity: int = 1,
) -> int:
    """
    Adds an item to the player's inventory in a specific slot.

    If the slot is already occupied, the function will not add the item.

    Returns:
        int: The amount of items that could NOT be added.
    """
    _validate_custom_slot_item(slot, item_id)
    

    if quantity <= 0:
        return 0

    item = items_dict.get(item_id)

    if item is None:
        raise ValueError(f"Item {item_id} does not exist.")

    max_stack = item["max_stack"]

    # Check if the slot is already occupied
    sq_cursor.execute(
        f"""
            SELECT quantity
            FROM {TABLE_INVENTORY}
            WHERE {ID_NAME} = ?
              AND slot = ?
        """,
        (user_id, slot)
    )

    existing_stack = sq_cursor.fetchone()

    if existing_stack is not None:
        # Slot is occupied, cannot add items
        return quantity

    amount_to_add = min(quantity, max_stack)

    sq_cursor.execute(
        f"""
            INSERT INTO {TABLE_INVENTORY}
            (
                {ID_NAME},
                {ID_NAME_ITEM},
                quantity,
                slot
            )
            VALUES (?, ?, ?, ?)
        """,
        (user_id, item_id, amount_to_add, slot)
    )

    sq_connection.commit()

    # Return any remaining items that couldn't be added
    return quantity - amount_to_add

def SQSwap(
    user_id: int,
    id_from: int,
    id_to: int,
    slot_from: int,
    slot_to: int,
):
    # detect the slot and item type of the items being swapped
    item_from = items_dict.get(id_from)
    item_to = items_dict.get(id_to)
    
    if not item_from and not item_to:
        raise ValueError("Both slots are empty. Cannot swap empty slots.")
    
    # check if the items can be swapped based on their types and slots
    type_from = item_from["item_type"]
    type_to = item_to["item_type"]

    # Validate the swap based on item types and slots
    if (slot_from == WEAPON and type_to != WEAPON_ITEM) or \
        (slot_from == SHIELD and type_to != SHIELD_ITEM) or \
        (slot_from in [HELMET, CHESTPLATE, LEGGINGS, BOOTS] and type_to != ARMOR_ITEM) or \
        (slot_to == WEAPON and type_from != WEAPON_ITEM) or \
        (slot_to == SHIELD and type_from != SHIELD_ITEM) or \
        (slot_to in [HELMET, CHESTPLATE, LEGGINGS, BOOTS] and type_from != ARMOR_ITEM):
        raise ValueError("Items cannot be swapped due to incompatible types and slots.")
        
    # Perform the swap in the database
    sq_cursor.execute(
        f"""
            UPDATE {TABLE_INVENTORY}
            SET {ID_NAME_ITEM} = CASE
                WHEN slot = ? THEN ?
                WHEN slot = ? THEN ?
                ELSE {ID_NAME_ITEM}
            END,
            quantity = CASE
                WHEN slot = ? THEN (SELECT quantity FROM {TABLE_INVENTORY} WHERE {ID_NAME} = ? AND slot = ?)
                WHEN slot = ? THEN (SELECT quantity FROM {TABLE_INVENTORY} WHERE {ID_NAME} = ? AND slot = ?)
                ELSE quantity
            END
            WHERE {ID_NAME} = ? AND (slot = ? OR slot = ?)
        """,
        (slot_from, id_to, slot_to, id_from,
         slot_from, user_id, slot_from,
         slot_to, user_id, slot_to,
         user_id, slot_from, slot_to)
    )
    
    # commit
    sq_connection.commit()