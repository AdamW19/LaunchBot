from db import db_strings
from db.database import Database
from modules.power_level import Team, Result
import time


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

        # Updating seasons table
        self.execute_query_nr(db_strings.UPDATE_SEASON, (new_season_num, current_time, None, server_id))

        # Inits any dropped tables
        self.init_season()

    def purge_players(self, server_members: list):
        # Get rid of all players in the Profiles db but not in the server
        removed_players = []
        player_ids = self.execute_query_no_arg(db_strings.GET_ALL_PROFILES_PLAYER_ID)
        for player in player_ids:
            if player not in server_members:
                self.execute_query_nr(db_strings.DELETE_PROFILE, player)
                removed_players.append(player)
        return removed_players  # return what players we removed

    def update_season_end(self, server_id: int):
        # Disables or enables the season
        season_end_status = self.execute_query(db_strings.GET_SETTINGS, ("season_end", server_id))

        if season_end_status is None:
            end_time = int(time.time())
        else:
            end_time = None
        self.execute_query_nr(db_strings.UPDATE_SEASON_END, (end_time, server_id))

    def get_next_team_id(self, server_id: int):
        # returns the next scrim_id in the db
        last_team_id = self.execute_query(db_strings.GET_SETTINGS, ("prev_team_id", server_id))
        next_team_id = last_team_id + 1
        self.execute_query_nr(db_strings.UPDATE_LAST_SCRIM, (next_team_id, server_id))

        return next_team_id

    def set_finish(self, alpha_team: Team, beta_team: Team, set_result: Result):
        # Updates a player's set win/loss rate after a set
        alpha_win = alpha_loss = beta_win = beta_loss = 0
        if set_result is Result.ALPHA_WIN:
            alpha_win = 1
            beta_loss = 1
        else:
            alpha_loss = 1
            beta_win = 1

        # We only update the players that have played for the entire set
        for player in alpha_team.players:
            if not player.active_sub:
                player_id = player.player_id

                player_row = self.execute_query(db_strings.GET_PLAYER, player_id)
                player_game_wins = player_row[5] + alpha_win
                player_game_loses = player_row[6] + alpha_loss
                self.execute_query_nr(db_strings.UPDATE_PLAYER_SET_STAT, (player_game_wins, player_game_loses,
                                                                          player_id))

        for player in beta_team.players:
            if not player.active_sub:
                player_id = player.player_id

                player_row = self.execute_query(db_strings.GET_PLAYER, player_id)
                player_game_wins = player_row[5] + beta_win
                player_game_loses = player_row[6] + beta_loss
                self.execute_query_nr(db_strings.UPDATE_PLAYER_SET_STAT, (player_game_wins, player_game_loses,
                                                                          player_id))

    def match_finish(self, alpha_team: Team, beta_team: Team, scrim_id: int, result: Result):
        alpha_win = alpha_loss = beta_win = beta_loss = 0
        if result is Result.ALPHA_WIN:
            alpha_win = 1
            beta_loss = 1
        else:
            alpha_loss = 1
            beta_win = 1

        for player in alpha_team.players:
            player_id = player.player_id
            player_rank_mu = player.rating.mu
            player_rank_sigma = player.rating.sigma

            self.execute_query_nr(db_strings.UPDATE_PLAYER_RANK, (player_rank_mu, player_rank_sigma, player_id))

            player_row = self.execute_query(db_strings.GET_PLAYER, player_id)
            player_game_wins = player_row[3] + alpha_win
            player_game_loses = player_row[4] + alpha_loss
            self.execute_query_nr(db_strings.UPDATE_PLAYER_GAME_STAT, (player_game_wins, player_game_loses, player_id))

        for player in beta_team.players:
            player_id = player.player_id
            player_rank_mu = player.rating.mu
            player_rank_sigma = player.rating.sigma

            self.execute_query_nr(db_strings.UPDATE_PLAYER_RANK, (player_rank_mu, player_rank_sigma, player_id))

            player_row = self.execute_query(db_strings.GET_PLAYER, player_id)
            player_game_wins = player_row[3] + beta_win
            player_game_loses = player_row[4] + beta_loss
            self.execute_query_nr(db_strings.UPDATE_PLAYER_GAME_STAT, (player_game_wins, player_game_loses, player_id))

        scrim_row = self.execute_query(db_strings.GET_SCRIM, scrim_id)
        alpha_score = scrim_row[3]
        beta_score = scrim_row[4]

        if result is Result.ALPHA_WIN:
            alpha_score += 1
        else:
            beta_score += 1

        self.execute_query(db_strings.UPDATE_SCRIM_SCORE, (alpha_score, beta_score, scrim_id))
