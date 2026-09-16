# import math
# https://gamedev.stackexchange.com/questions/129319/rpg-formula-attack-and-defense
def SQGetSlimeDamage(player_defense, slime_damage):
    return round(slime_damage * slime_damage / (slime_damage + player_defense))
        
