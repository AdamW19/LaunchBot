from collections import defaultdict
from tabulate import tabulate

PARSE_LEN = 4  # length of map-mode combo

YES_STR = "X"  # string printed when a map-mode is in the map pool
NO_STR = ""  # string printed when a map-mode is NOT in the map pool

MAP_HEADER = "Map"  # Header for the maps column

MODES = [
    "Turf War",
    "Splat Zones",
    "Tower Control",
    "Rainmaker",
    "Clam Blitz"
]

MODE_TO_LONG_MODE = {
    "tw": "Turf War",
    "sz": "Splat Zones",
    "tc": "Tower Control",
    "rm": "Rainmaker",
    "cb": "Clam Blitz"
}

MAP_TO_LONG_MAP = {
    "ag": "Ancho-V Games",
    "am": "Arowana Mall",
    "bs": "Blackbelly Skatepark",
    "ct": "Camp Triggerfish",
    "ga": "Goby Arena",
    "hp": "Humpback Pump Track",
    "ia": "Inkblot Art Academy",
    "kd": "Kelp Dome",
    "mk": "MakoMart",
    "mm": "Manta Maria",
    "mt": "Moray Towers",
    "mf": "Musselforge Fitness",
    "ah": "New Albacore Hotel",
    "pp": "Piranha Pit",
    "pm": "Port Mackerel",
    "si": "Shellendorf Institute",
    "sp": "Skipper Pavilion",
    "sc": "Snapper Canal",
    "sm": "Starfish Mainstage",
    "ss": "Sturgeon Shipyard",
    "tr": "The Reef",
    "wh": "Wahoo World",
    "ww": "Walleye Warehouse"
}


# For the defaultdict
def def_val():
    return None


def parse_code_format(code: str):
    """ Converts code to a printable list """
    if len(code) % 4 != 0:
        code_dict = {"error": "Invalid input -- len(code) not divisible by 4"}
        return code_dict

    # Goes from code to a list of printable strings
    formatted_code = []
    code_array = [code[i:i + PARSE_LEN] for i in range(0, len(code), PARSE_LEN)]  # Splits string into length 4 strings
    for val in code_array:
        # The code is 2 characters for the mode followed by 2 characters for the stage
        mode = val[:2]
        stage = val[2:4]
        # Basic error checking to make sure mode/stage are valid
        if mode not in MODE_TO_LONG_MODE or stage not in MAP_TO_LONG_MAP:
            formatted_code = {"error": "Invalid input -- mode/stage code unknown"}
            break

        # Making a basic "[Mode] - [Map]" for general printing
        mode_map = MODE_TO_LONG_MODE[mode] + " - " + MAP_TO_LONG_MAP[stage]
        formatted_code.append(mode_map)

    return formatted_code


def parse_code_dict(code: str):
    """ Converts code to a machine readable dictionary """
    if len(code) % 4 != 0:
        code_dict = {"error": "Invalid input -- len(code) not divisible by 4"}
        return code_dict

    # Goes from code to a more machine readable dict of lists
    code_dict = defaultdict(def_val)
    code_array = [code[i:i + PARSE_LEN] for i in range(0, len(code), PARSE_LEN)]  # Splits string into length 4 strings

    for val in code_array:
        # The code is 2 characters for the mode followed by 2 characters for the stage
        mode = val[:2]
        stage = val[2:4]
        # Basic error checking to make sure mode/stage are valid
        if mode not in MODE_TO_LONG_MODE or stage not in MAP_TO_LONG_MAP:
            code_dict = {"error": "Invalid input -- mode/stage code unknown"}
            break

        # Convert to their full name
        mode = MODE_TO_LONG_MODE[val[:2]]
        stage = MAP_TO_LONG_MAP[val[2:4]]

        # Checking to see if the stage is already in the dictionary
        # If so, append to its list. Otherwise, make a new list and append to it.
        stage_list = code_dict[stage]
        if stage_list is not None:
            code_dict[stage].append(mode)
        else:
            code_dict[stage] = []
            code_dict[stage].append(mode)
    return code_dict


def gen_maplist_str(gen_dict: defaultdict):
    """ Converts from a defaultdict to a printable table """

    # gen_dict: key is stage, value is list of modes
    table = []
    all_modes = []
    all_modes_sorted = []

    # Checks to see what modes are in the dictionary
    for key, value in gen_dict.items():
        for mode in value:
            if mode not in all_modes:
                all_modes.append(mode)

    # Generates header and adds Map to the map column
    for mode in MODES:
        if mode in all_modes:
            all_modes_sorted.append(mode)
    all_modes_sorted.insert(0, MAP_HEADER)
    table.append(all_modes_sorted)

    # Generates table
    for key, value in gen_dict.items():
        flat_list = [key]
        mode_iter = iter(value)
        current_mode = next(mode_iter)

        # for each mode in the known modes, check if the mode is in the value
        # If so, append it to the list, otherwise continue.
        # If we've finished running the iterator, continue to the next key
        for mode in all_modes_sorted:
            if mode != MAP_HEADER:
                if mode == current_mode:
                    flat_list.append(YES_STR)
                    try:
                        current_mode = next(mode_iter)
                    except StopIteration:
                        continue
                else:
                    flat_list.append(NO_STR)
        table.append(flat_list)
    # Then we tabulate the table, 1st row is the header, center align, use simple formatting
    return tabulate(table, headers="firstrow", stralign="center", tablefmt="simple")
