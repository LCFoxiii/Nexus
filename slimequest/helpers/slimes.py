# possible slime actions
ATTACK  = "attack"
BLOCK   = "block"
PARRY   = "parry"
NOTHING = "nothing"


movesets = {
    "all_attacks": [ATTACK],
    "all_blocks": [BLOCK],
    "all_parries": [PARRY],
    "all_nothings": [NOTHING],
    
    "normal": [ATTACK, BLOCK, PARRY, NOTHING],
    "aggressive": [ATTACK, ATTACK, BLOCK, PARRY],
    "defensive": [BLOCK, BLOCK, ATTACK, PARRY],
    "cowardly": [BLOCK, BLOCK, BLOCK, NOTHING],
    "duelist": [ATTACK, PARRY]
}



slime_entries = {}
def CreateSlimeEntry(
        name:               str,
        description:        str,
        level:              int,
        health:             int,
        defense:            int,
        damage:             int,
        speed:              int,
        xp:                 int,
        copper_slime_coins: int,
        silver_slime_coins: int,
        gold_slime_coins:   int,
        moveset:            list[str],
        slime_image:        str, # this is just paths
    ) -> None:
    slime_entries.update({
        name: {
            "name": name,
            "description": description,
            "level": level,
            "health": health,
            "defense": defense,
            "damage": damage,
            "speed": speed,
            "rewards": {
                
                "stats": {
                    "xp": xp,
                },
                
                "currency": {
                    "copper_slime_coins": copper_slime_coins,
                    "silver_slime_coins": silver_slime_coins,
                    "gold_slime_coins": gold_slime_coins
                },
            },
            
            "moveset": moveset,
            
            "slime_image": slime_image
        }
    })
    
# for testing purposes, this is a temporary slime.
CreateSlimeEntry(
    name                = "Dev Slime",
    description         = "test slime for battle test.",
    level               = 1, # could be scalable based on the player's level???
    health              = 100, # also scalable based on the slime's level
    defense             = 10,
    damage              = 10,
    speed               = 10,
    xp                  = 10,
    copper_slime_coins  = 10,
    silver_slime_coins  = 5,
    gold_slime_coins    = 1,
    moveset             = movesets["normal"],
    slime_image         = "temporary, do not use this, this is just a placeholder for now."
)

print(slime_entries)