print("this is from items.py")

# rariries
COMMON      = "common"
UNCOMMON    = "uncommon"
RARE        = "rare"
EPIC        = "epic"
LEGENDARY   = "legendary"
MYTHIC      = "mythic"
DEV_GRANTED = "dev_granted"

items_dict = {}

def CreateItemEntry(
    index:        int,
    name:         str,
    description:  str,
    copper_value: int,
    silver_value: int,
    gold_value:   int,
    rarity:       str,
    max_stack:    int
):
    items_dict.update({
        index: {
            "name": name,
            "description": description,
            "values": {
                "copper_slime_coins": copper_value,
                "silver_slime_coins": silver_value,
                "gold_slime_coins": gold_value,
            },
            "rarity": rarity,
            "max_stack": max_stack,
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
    max_stack=99
)