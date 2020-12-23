from collections import defaultdict

PARSE_LEN = 4  # length of map-mode combo

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


def def_val():
    # For the defaultdict
    return None


def parse_code_format(code: str):
    # Goes from code to a list of printable strings
    formatted_code = []
    code_array = [code[i:i + PARSE_LEN] for i in range(0, len(code), PARSE_LEN)]
    for val in code_array:
        mode = val[:2]
        stage = val[2:4]
        # Basic error checking
        if mode not in MODE_TO_LONG_MODE or stage not in MAP_TO_LONG_MAP:
            formatted_code = {"error": "Invalid input"}
            break

        mode_map = MODE_TO_LONG_MODE[mode] + " - " + MAP_TO_LONG_MAP[stage]
        formatted_code.append(mode_map)

    return formatted_code


def parse_code_dict(code: str):
    # Goes from code to a more machine readable dict of lists
    code_dict = defaultdict(def_val)
    code_array = [code[i:i + PARSE_LEN] for i in range(0, len(code), PARSE_LEN)]

    for val in code_array:
        mode = val[:2]
        stage = val[2:4]
        # Basic error checking
        if mode not in MODE_TO_LONG_MODE or stage not in MAP_TO_LONG_MAP:
            code_dict = {"error": "Invalid input"}
            break

        mode = MODE_TO_LONG_MODE[val[:2]]
        stage = MAP_TO_LONG_MAP[val[2:4]]
        stage_list = code_dict[stage]
        if stage_list is not None:
            code_dict[stage].append(mode)
        else:
            code_dict[stage] = []
            code_dict[stage].append(mode)
    return code_dict
