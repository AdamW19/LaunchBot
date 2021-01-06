from db.src import db_strings
from db.src.database import Database, DB_FILE_BASE


def get_all_db_files():
    import glob
    db_files = glob.glob(DB_FILE_BASE + "*.db")
    return db_files


class DataDB(Database):

    def __init__(self, file_name: str, file_format: str):
        super(DataDB, self).__init__(db_filename=file_name, file_format=file_format)

    def get_player_info(self, player_id: int, server_id: int):
        profile_info = ""  # format is discord_id, switch FC
        player_info = ""  # format is discord_id, mu, sigma, num_won_games, num_loss_games, num_win_sets, num_loss_sets
        team_info = []  # format is a list of team id, scrim id, players played with, if player was a sub or captain,
                        # results

        season_id = self.execute_query(db_strings.GET_SETTINGS, server_id)[0][4]

        profile = self.execute_query(db_strings.GET_PROFILE, player_id)
        if len(profile) is not 0:
            profile = profile[0]
            profile_info = [str(profile[0]), str(profile[1])]
        else:
            profile_info = ["None"] * 2

        player = self.execute_query(db_strings.GET_PLAYER, player_id)
        if len(player) is not 0:
            player = str(player[0])
            for info in player:
                player_info += str(info) + ","
        else:
            player_info = ["None"] * 7

        teams_list = self.execute_query(db_strings.GET_TEAM_VIA_PLAYER, player_id)
        if teams_list is not None:
            for team_listing in teams_list:
                team_id = team_listing[0]
                scrim_list = [team_id, str(bool(team_listing[2])), str(bool(team_listing[3]))]

                players = []

                played_with = self.execute_query(db_strings.GET_TEAM, player_id)

                scrim = self.execute_query(db_strings.GET_SCRIM, team_id)
                scrim = scrim[0]
                scrim_list.index(scrim, 1)  # add scrim id in the 2nd row
                if scrim[1] is team_id:
                    played_against = self.execute_query(db_strings.GET_TEAM, scrim[2])
                else:
                    played_against = self.execute_query(db_strings.GET_TEAM, scrim[1])

                for player in played_with, played_against:
                    players.append(player[1])

                scrim_list.append(players)

                team_info.append(scrim_list)
        else:
            team_info = ["None"] * 5

        return season_id, profile_info, player_info, team_info

    def purge_player_info(self, player_id: int):
        self.execute_commit_query(db_strings.DELETE_PLAYER, player_id)
        self.execute_commit_query(db_strings.DELETE_PROFILE, player_id)
        self.execute_commit_query(db_strings.DELETE_TEAM_PLAYER, player_id)
