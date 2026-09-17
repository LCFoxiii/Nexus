# https://gamedev.stackexchange.com/questions/129319/rpg-formula-attack-and-defense
def SQGetDamage(defense, enemy_damage):
    return round(enemy_damage * enemy_damage / (enemy_damage + defense))
        
