from enum import Enum, auto

from db import db_strings
from db.database import Database


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

    def get_rows(self, arguments: tuple, which_table: Tables):
        if which_table is Tables.PROFILE:
            return self.execute_query(db_strings.GET_PROFILE, arguments)
        elif which_table is Tables.PLAYER:
            return self.execute_query(db_strings.GET_PLAYER, arguments)
        elif which_table is Tables.TEAM:
            return self.execute_query(db_strings.GET_TEAM, arguments)
        elif which_table is Tables.SCRIM:
            return self.execute_query(db_strings.GET_SCRIM, arguments)
        elif which_table is Tables.SETTINGS:
            return self.execute_query(db_strings.GET_SCRIM, arguments)
        else:
            raise AttributeError("Invalid table")

    def set_rows(self, arguments: tuple, which_table: Tables):
        if which_table is Tables.PROFILE:
            return self.execute_query(db_strings.INSERT_PROFILE, arguments)
        elif which_table is Tables.PLAYER:
            return self.execute_query(db_strings.INSERT_PLAYER, arguments)
        elif which_table is Tables.TEAM:
            return self.execute_query(db_strings.INSERT_TEAM, arguments)
        elif which_table is Tables.SCRIM:
            return self.execute_query(db_strings.INSERT_SCRIM, arguments)
        elif which_table is Tables.SETTINGS:
            return self.execute_query(db_strings.INSERT_SCRIM, arguments)
        else:
            raise AttributeError("Invalid table")
