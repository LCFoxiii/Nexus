import sqlite3

sq_connection = sqlite3.connect("slimequest.db")

sq_cursor = sq_connection.cursor()

# just to make it easier to find tables and stuff.
TABLE_USERS     = "sq_users"
TABLE_CURRENCY  = "sq_currency"
TABLE_STATS     = "sq_stats"
TABLE_INVENTORY = "sq_inventory"
TABLE_ITEMS     = "sq_items"
TABLE_INSTANCE  = "sq_instance"

# no inventory for the time being.

ID_NAME = "id"
ID_NAME_INSTANCE = "instance_id"
ID_NAME_ITEM = "item_id"

# enable foreign keys
sq_cursor.execute("PRAGMA foreign_keys = ON")

# users
sq_cursor.execute(
    f"""
        CREATE TABLE IF NOT EXISTS {TABLE_USERS} (
            {ID_NAME} INTEGER PRIMARY KEY,
            name VARCHAR(32) NOT NULL,
            true_name TEXT NOT NULL,
            gender INTEGER DEFAULT NULL
        )
    """
)

# currency
sq_cursor.execute(
    f"""
        CREATE TABLE IF NOT EXISTS {TABLE_CURRENCY} (
            {ID_NAME} INTEGER PRIMARY KEY,
            copper_slime_coins INTEGER NOT NULL DEFAULT 0,
            silver_slime_coins INTEGER NOT NULL DEFAULT 0,
            gold_slime_coins INTEGER NOT NULL DEFAULT 0
        )
    """
)

# stats
sq_cursor.execute(
    f"""
        CREATE TABLE IF NOT EXISTS {TABLE_STATS} (
            {ID_NAME} INTEGER PRIMARY KEY,
            level INTEGER NOT NULL DEFAULT 0,
            xp INTEGER NOT NULL DEFAULT 0,
            health INTEGER NOT NULL DEFAULT 100,
            mana INTEGER NOT NULL DEFAULT 100,
            dexterity INTEGER NOT NULL DEFAULT 0,
            strength INTEGER NOT NULL DEFAULT 0,
            defense INTEGER NOT NULL DEFAULT 0,
            speed INTEGER NOT NULL DEFAULT 10,
            damage INTEGER NOT NULL DEFAULT 30
        )
    """
)


# instance
sq_cursor.execute(
    f"""
        CREATE TABLE IF NOT EXISTS {TABLE_INSTANCE} (
            {ID_NAME_INSTANCE} INTEGER PRIMARY KEY
        )
    """
)

# inventory
# this allows slot 0 and below, but i need this for equipment and other specialized slots.
sq_cursor.execute(
    f"""
        CREATE TABLE IF NOT EXISTS {TABLE_INVENTORY} (
            {ID_NAME} INTEGER PRIMARY KEY,
            {ID_NAME_ITEM} INTEGER NOT NULL,
            {ID_NAME_INSTANCE} INTEGER DEFAULT NULL,
            slot INTEGER NOT NULL CHECK (slot <= 32),
            quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
            FOREIGN KEY ({ID_NAME_INSTANCE}) REFERENCES {TABLE_INSTANCE}({ID_NAME_INSTANCE}),
            UNIQUE ({ID_NAME}, slot, {ID_NAME_INSTANCE})
        )
    """
)

# possible entries?

# table name: sq_users
# id (int primary key) (could use discord id)
# name (32 char primary key) (false name, inputted by user, so that they think this is their name.)
# true_name (32 char) (true name, could be automatically generated and picked randomly)
# gender (int) (0 = male, 1 = female, other / non-binary = 2) (default could be none.)

# table name: sq_currency
# id (int primary key) (could use discord id)
# copper_slime_coins (int)
# silver_slime_coins (int)
# gold_slime_coins   (int)

# table name: sq_stats
# id (int primary key) (could use discord id)
# level (int)
# xp (int)
# health (int)
# mana (int)
# strength (int)
# defense (int)
# speed (int)

# table name: sq_inventory
# id (int primary key) (could use discord id)
# item_id (int)
# instance_id (int)
# quantity (int)
# slot
# instance_id (reference to sq_instance table, nullable.)

# table name: sq_instance
# id (int primary key) (could use discord id)
# instance_id (int)
# etc.

# items and other shit plans:

# items:
# item id
# item name
# item description
# rarity (0 = common, 1 = uncommon, 2 = rare, 3 = epic, 4 = legendary, 5 = mythic)
# description
# max stack
# level requirement
# slot (inventory slot, not equipment slot)

# equipment:
# equipment id
# equipment name
# equipment description
# rarity (0 = common, 1 = uncommon, 2 = rare, 3 = epic, 4 = legendary, 5 = mythic)
# slot (0 = head, 1 = chest, 2 = legs, 3 = feet, 4 = weapon, 5 = accessory)
# base damage
# base defense
# base stats
# durability
# level requirement

# enchantments:
# enchantment id
# enchantment name
# enchantment description
# rarity (0 = common, 1 = uncommon, 2 = rare, 3 = epic, 4 = legendary, 5 = mythic)
# stat bonus
# level requirement