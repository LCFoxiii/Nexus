print("this is from items.py")

# rariries
COMMON      = "common"
UNCOMMON    = "uncommon"
RARE        = "rare"
EPIC        = "epic"
LEGENDARY   = "legendary"
MYTHIC      = "mythic"
DEV_GRANTED = "dev_granted"

# types of items
REGULAR_ITEM = "regular_item"
WEAPON_ITEM = "weapon_item"
SHIELD_ITEM = "shield_item"
ARMOR_ITEM = "armor_item"

# special slots
WEAPON = -1
SHIELD = -2
HELMET = -3
CHESTPLATE = -4
LEGGINGS = -5
BOOTS = -6

items_dict = {}

def CreateItemEntry(
    index:                   int,
    name:                    str,
    description:             str,
    copper_value:            int,
    silver_value:            int,
    gold_value:              int,
    rarity:                  str,
    max_stack:               int,
    damage_boost:            int,
    defense_boost:           int,
    health_boost:            int,
    penetration_boost:       int,
    item_type:               str,
    slime_splash_protection: int,
    block_penetration:       int,
):
    items_dict.update({
        index: {
            "name": name,
            "description": description,
            "values": { # if all of these are none, then the item is not sellable.
                "copper_slime_coins": copper_value,
                "silver_slime_coins": silver_value,
                "gold_slime_coins": gold_value,
            },
            "rarity": rarity,
            "max_stack": max_stack,
            "stats": {
                "damage_boost": damage_boost,
                "defense_boost": defense_boost,
                "health_boost": health_boost,
                "penetration_boost": penetration_boost, # 0 - 100.
                "slime_splash_protection": slime_splash_protection, # 0 - 100.
                "block_penetration": block_penetration, # 0 - 100.
            },
            "item_type": item_type
        }
    })

DEV_ITEM = 0
CreateItemEntry(
    index=DEV_ITEM,
    name="dev item",
    description="this is a dev item, it does nothing.",
    copper_value=100,
    silver_value=10,
    gold_value=1,
    rarity=DEV_GRANTED,
    max_stack=99,
    damage_boost=None,
    defense_boost=None,
    health_boost=None,
    penetration_boost=None,
    slime_splash_protection=None,
    item_type=REGULAR_ITEM,
    block_penetration=None
)

WOODEN_SWORD = 1
CreateItemEntry(
    index=WOODEN_SWORD,
    name="wooden sword",
    description="The first weapon you will ever use. And for some, it will be the last.",
    copper_value=10,
    silver_value=0,
    gold_value=0,
    rarity=COMMON,
    max_stack=1,
    damage_boost=10,
    defense_boost=None,
    health_boost=None,
    penetration_boost=5,
    slime_splash_protection=3,
    item_type=WEAPON_ITEM,
    block_penetration=5
)

WOODEN_SHIELD = 2
CreateItemEntry(
    index=WOODEN_SHIELD,
    name="wooden shield",
    description="A basic wooden shield. It won't protect you from much, but it's better than nothing.",
    copper_value=20,
    silver_value=0,
    gold_value=0,
    rarity=COMMON,
    max_stack=1,
    damage_boost=None,
    defense_boost=10,
    health_boost=None,
    penetration_boost=None,
    slime_splash_protection=5,
    item_type=SHIELD_ITEM,
    block_penetration=None
)

LEATHER_HELMET = 3
CreateItemEntry(
    index=LEATHER_HELMET,
    name="leather helmet",
    description="A basic leather helmet. It won't protect you from much, but it's better than nothing.",
    copper_value=10,
    silver_value=0,
    gold_value=0,
    rarity=COMMON,
    max_stack=1,
    damage_boost=None,
    defense_boost=5,
    health_boost=None,
    penetration_boost=None,
    slime_splash_protection=7,
    item_type=ARMOR_ITEM,
    block_penetration=None
)

LEATHER_CHESTPLATE = 4
CreateItemEntry(
    index=LEATHER_CHESTPLATE,
    name="leather chestplate",
    description="A basic leather chestplate. It won't protect you from much, but it's better than nothing.",
    copper_value=20,
    silver_value=0,
    gold_value=0,
    rarity=COMMON,
    max_stack=1,
    damage_boost=None,
    defense_boost=10,
    health_boost=None,
    penetration_boost=None,
    slime_splash_protection=10,
    item_type=ARMOR_ITEM,
    block_penetration=None
)

LEATHER_LEGGINGS = 5
CreateItemEntry(
    index=LEATHER_LEGGINGS,
    name="leather leggings",
    description="A basic pair of leather leggings. It won't protect you from much, but it's better than nothing.",
    copper_value=15,
    silver_value=0,
    gold_value=0,
    rarity=COMMON,
    max_stack=1,
    damage_boost=None,
    defense_boost=7,
    health_boost=None,
    penetration_boost=None,
    slime_splash_protection=8,
    item_type=ARMOR_ITEM,
    block_penetration=None
)

LEATHER_BOOTS = 6
CreateItemEntry(
    index=LEATHER_BOOTS,
    name="leather boots",
    description="A basic pair of leather boots. It won't protect you from much, but it's better than nothing.",
    copper_value=10,
    silver_value=0,
    gold_value=0,
    rarity=COMMON,
    max_stack=1,
    damage_boost=None,
    defense_boost=5,
    health_boost=None,
    penetration_boost=None,
    slime_splash_protection=5,
    item_type=ARMOR_ITEM,
    block_penetration=None
)