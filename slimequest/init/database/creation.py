import sqlite3

sq_connection = sqlite3.connect("slimequest.db")

sq_cursor = sq_connection.cursor()

# just to make it easier to find tables and stuff.
TABLE_USERS    = "sq_users"
TABLE_CURRENCY = "sq_currency"
TABLE_STATS    = "sq_stats"

# no inventory for the time being.

ID_NAME = "id"

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
            strength INTEGER NOT NULL DEFAULT 10,
            defense INTEGER NOT NULL DEFAULT 10,
            speed INTEGER NOT NULL DEFAULT 10
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
# TODO: figure this shit out

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