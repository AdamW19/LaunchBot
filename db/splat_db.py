from enum import Enum, auto

from db import db_strings
from db.database import Database
import time


class Tables(Enum):
    PROFILE = auto()
    PLAYER = auto()
    TEAM = auto()
    SCRIM = auto()
    SETTINGS = auto()


class SplatoonDB(Database):

    def __init__(self, file_name: str):
        super(SplatoonDB, self).__init__(db_filename=file_name)

    def init_season(self):
        self.execute_query_no_arg(db_strings.INIT_PROFILE_TABLE)
        self.execute_query_no_arg(db_strings.INIT_PLAYER_TABLE)
        self.execute_query_no_arg(db_strings.INIT_TEAM_TABLE)
        self.execute_query_no_arg(db_strings.INIT_SCRIM_TABLE)
        self.execute_query_no_arg(db_strings.INIT_SETTING_TABLE)

    def init_new_season(self, server_id: int):
        new_season_num = int(self.filename[7:8]) + 1  # Gets the current season and adds 1 to it
        current_time = int(time.time())

        super(SplatoonDB, self).start_new_season(new_season_num)
        self.execute_query_no_arg(db_strings.DROP_PLAYER_TABLE)  # Drops all tables other than settings & players
        self.execute_query_no_arg(db_strings.DROP_TEAM_TABLE)
        self.execute_query_no_arg(db_strings.DROP_SCRIM_TABLE)

        self.execute_query_nr(db_strings.UPDATE_SEASON, (new_season_num, current_time, None, server_id))

    def purge_players(self, server_members: list):
        player_ids = self.execute_query_no_arg(db_strings.GET_ALL_PROFILES_PLAYER_ID)
        for player in player_ids:
            if player not in server_members:
                self.execute_query_nr(db_strings.DELETE_PROFILE, player)

    def update_season_end(self, server_id: int):
        season_end_status = self.execute_query(db_strings.GET_SETTINGS, ("season_end", server_id))

        if season_end_status is None:
            end_time = int(time.time())
        else:
            end_time = None

        self.execute_query_nr(db_strings.UPDATE_SEASON_END, (end_time, server_id))
