from .items import *
from ..init.database.creation import *
from general_helpers.db_helpers import *

# returns the amount of items that could not be added to the inventory.
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