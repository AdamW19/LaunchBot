# From Splatbot: https://github.com/ktraw2/SplatBot/blob/master/modules/splatoon_rotation.py

from enum import Enum, auto
from modules.splatnet import Splatnet
from datetime import datetime
from modules.linked_list import LinkedList
from modules.salmon_emotes import gen_emote_id, SR_TERM_CHAR

IMAGE_BASE = "https://splatoon2.ink/assets/splatnet"


class ModeTypes(Enum):
    SPLATFEST = auto()
    REGULAR = auto()
    RANKED = auto()
    LEAGUE = auto()
    SALMON = auto()
    PRIVATE = auto()


class Splatfest:
    # Just a container to hold Splatfest info
    splatfest_stage = None
    splatfest_image = None


class SplatoonRotation:
    def __init__(self, target_time: datetime, mode_type: ModeTypes, splatnet: Splatnet):
        self.target_time = target_time
        self.mode_type = mode_type
        self.splatnet = splatnet

        self.mode = None
        self.stages = []
        self.stage_images = []
        self.start_time = None
        self.end_time = None
        self.next_rotation = None
        if mode_type is not ModeTypes.SALMON:
            self.splatfest = None  # For splatfest information
        if mode_type is ModeTypes.SALMON:
            self.weapons_array = None  # For salmon run only

    async def populate_data(self):
        timestamp = self.target_time.timestamp()
        data = None
        splatfest_info = (await self.splatnet.get_na_splatfest())["festivals"][0]

        # Checking to see if splatfest is happening, the 0th elm is going to be the most recent one
        if self.mode_type is not ModeTypes.SALMON and splatfest_info["times"]["start"] <= timestamp < \
                splatfest_info["times"]["end"]:
            data = await self.splatnet.get_turf()
            self.mode_type = ModeTypes.SPLATFEST  # gotta remember to update the mode
            self.splatfest = Splatfest()
            self.splatfest.splatfest_stage = splatfest_info["special_stage"]["name"]
            self.splatfest.splatfest_image = IMAGE_BASE + splatfest_info["special_stage"]["image"]
        else:
            if self.mode_type is ModeTypes.REGULAR:
                data = await self.splatnet.get_turf()
            elif self.mode_type is ModeTypes.RANKED:
                data = await self.splatnet.get_ranked()
            elif self.mode_type is ModeTypes.LEAGUE:
                data = await self.splatnet.get_league()
            elif self.mode_type is ModeTypes.SALMON:
                data = await self.splatnet.get_salmon_detail()

        # find a regular/ranked/league session given the target time
        for rotation in data:
            if rotation["start_time"] <= timestamp < rotation["end_time"]:
                self.start_time = datetime.fromtimestamp(rotation["start_time"], self.target_time.tzname())
                self.end_time = datetime.fromtimestamp(rotation["end_time"], self.target_time.tzname())
                self.next_rotation = datetime.fromtimestamp(data[1]["start_time"], self.target_time.tzname())
                if self.mode_type is not ModeTypes.SALMON:
                    self.stages.append(rotation["stage_a"]["name"])
                    self.stage_images.append(IMAGE_BASE + rotation["stage_a"]["image"])
                    self.mode = rotation["rule"]["name"]
                    self.stages.append(rotation["stage_b"]["name"])
                    self.stage_images.append(IMAGE_BASE + rotation["stage_b"]["image"])
                    return True
                else:
                    # salmon run is a special exception, requires special processing
                    self.mode = "Salmon Run"
                    self.weapons_array = LinkedList()
                    self.stages.append(rotation["stage"]["name"])
                    self.stage_images.append(IMAGE_BASE + rotation["stage"]["image"])

                    # getting weapons, using SR_TERM_CHAR to separate b/t weapon name and weapon id
                    for weapon in rotation["weapons"]:
                        # weapon id of -1 indicates a random weapon
                        if weapon["id"] == '-1':
                            self.weapons_array.add(weapon["coop_special_weapon"]["name"] + " Weapon" + SR_TERM_CHAR +
                                                   "r1")
                        # weapon id of -2 indicates a random grizzco weapon
                        elif weapon["id"] == '-2':
                            self.weapons_array.add(weapon["coop_special_weapon"]["name"] + " Grizzco Weapon" +
                                                   SR_TERM_CHAR + "r2")
                        else:
                            self.weapons_array.add(weapon["weapon"]["name"] + SR_TERM_CHAR + weapon["id"])
                    return True
        return False

    @staticmethod
    def format_time(time: datetime):
        # returns <hour>:<time> <am/pm>
        return time.strftime("%I:%M %p")

    @staticmethod
    def format_time_sr(time: datetime):
        # returns <abbr. weekday> <abbr. month> <date> <hour>:<time> <am/pm>
        return time.strftime("%a %b %d %I:%M %p")

    @staticmethod
    def format_time_sch(time: datetime):
        # returns <hour> <am/pm>
        return time.strftime("%-I %p")

    @staticmethod
    def print_stages(stages: list):
        stage_str = ""
        for stage in stages:
            stage_str += stage + "\n"
        return stage_str

    @staticmethod
    def print_sr_weapons(weapons_array: LinkedList):
        # Used to print out salmon run weapons
        weapon_list_str = ""
        for weapon in weapons_array:
            # we split based off SR_TERM_CHAR: <weapon name>SR_TERM_CHAR<weapon id>
            weapon_name = weapon.split(SR_TERM_CHAR)[0]
            weapon_id = weapon.split(SR_TERM_CHAR)[1]
            weapon_list_str += gen_emote_id(weapon_id) + " " + weapon_name + "\n"
        return weapon_list_str
