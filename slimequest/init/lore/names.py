# Hello, code snoopers.
# This file is reserved for the names.
# so, spoiler alert, i guess.

import numpy as np 

male_first_name = [
    "Aldric",
    "Alaric",
    "Arlen",
    "Beren",
    "Caelan",
    "Cedric",
    "Darian",
    "Edric",
    "Elias",
    "Elric",
    "Emrys",
    "Eryndor",
    "Faelan",
    "Gareth",
    "Gavin",
    "Hadrian",
    "Kael",
    "Lorian",
    "Lucian",
    "Marek",
    "Roland",
    "Rowan",
    "Silas",
    "Theron",
    "Tristan",
    "Valen",
    "Varian",
    "Wystan",
]

female_first_name = [
    "Alina",
    "Aria",
    "Aveline",
    "Celeste",
    "Elara",
    "Elowen",
    "Elyra",
    "Evelyn",
    "Freya",
    "Isolde",
    "Liora",
    "Lyra",
    "Mira",
    "Nerissa",
    "Rhea",
    "Selene",
    "Seraphina",
    "Sylvia",
    "Talia",
    "Vera",
    "Yara",
]

last_name = [
    "Ashford",
    "Blackwood",
    "Brightwood",
    "Dawnmere",
    "Emberfall",
    "Everhart",
    "Fairwind",
    "Frostwood",
    "Goldmere",
    "Graves",
    "Hawthorne",
    "Ironwood",
    "Kingsley",
    "Mooncrest",
    "Nightvale",
    "Oakheart",
    "Ravencrest",
    "Ravenwood",
    "Redwyn",
    "Silverbrook",
    "Silverwood",
    "Starfall",
    "Stormwind",
    "Stoneheart",
    "Thornfield",
    "Thornwood",
    "Valewood",
    "Westfall",
    "Wintermere",
    "Winterwood",
    "Windermere",
    "Wolfhart",
    "Ambervale",
    "Brightmere",
    "Darkwater",
    "Duskwood",
    "Eagleton",
    "Evermere",
    "Flameheart",
    "Greystone",
    "Highwind",
    "Mistwood",
    "Moonbrook",
    "Oakridge",
    "Riversong",
    "Shadowmere",
    "Silvervale",
    "Stormvale",
    "Suncrest",
    "Wildheart",
]

def GetName(is_male: bool = True, non_binary_mode: bool = False) -> str:
    first = ""
    last = " " + np.random.choice(last_name)

    if not non_binary_mode:
        if is_male:
            first = np.random.choice(male_first_name)
        else:
            first = np.random.choice(female_first_name)
    else:
        first = np.random.choice(male_first_name + female_first_name)

    return first + last

# tests
print(GetName(False))
print(GetName(True))
# okay, fuck off now. :3