import asyncio
import time

from db.src import db_strings
from db.src.database import Database
from modules.leaderboard_helper import finalize_leaderboard
from modules.power_level import Team, Result


class SplatoonDB(Database):

    def __init__(self, file_name: str, file_format: str):
        super(SplatoonDB, self).__init__(db_filename=file_name, file_format=file_format)
        self.init_season()

    def init_season(self):
        self.execute_query_no_arg(db_strings.INIT_PROFILE_TABLE)
        self.execute_query_no_arg(db_strings.INIT_PLAYER_TABLE)
        self.execute_query_no_arg(db_strings.INIT_TEAM_TABLE)
        self.execute_query_no_arg(db_strings.INIT_SCRIM_TABLE)
        self.execute_query_no_arg(db_strings.INIT_SETTING_TABLE)

        if self.execute_query(db_strings.GET_PROFILE, 98101114116111) is None:
            self.execute_commit_query(db_strings.INSERT_PROFILE, (98101114116111, "BERTO-WAS-HERE"))  # easter egg 🥚

        self.conn.commit()

    async def init_new_season(self, server_id: int, ctx):
        # Get stuff from old season for final update
        current_settings = self.execute_query(db_strings.GET_SETTINGS, server_id)
        leaderboard_msg_id = current_settings[0][3]
        current_season = current_settings[0][4]
        current_start_time = current_settings[0][5]
        leaderboard = self.execute_query_no_arg(db_strings.GET_LEADERBOARD)
        new_season_num = current_season + 1
        current_time = int(time.time())

        # last update of old season table, so we have end_time correct
        self.execute_commit_query(db_strings.UPDATE_SEASON, (current_season, leaderboard_msg_id, current_start_time,
                                                             current_time, server_id))

        # Finalize the global leaderboard, lock is needed to prevent double edits to the leaderboard
        async with asyncio.Lock():
            await finalize_leaderboard(leaderboard_msg_id, current_season, leaderboard, ctx)

        # starting new table
        super(SplatoonDB, self).start_new_season(new_season_num)
        self.execute_query_no_arg(db_strings.DROP_PLAYER_TABLE)  # Drops all tables other than settings & players
        self.execute_query_no_arg(db_strings.DROP_TEAM_TABLE)
        self.execute_query_no_arg(db_strings.DROP_SCRIM_TABLE)

        # Updating seasons table
        self.execute_commit_query(db_strings.UPDATE_SEASON, (new_season_num, 0, current_time, 0, server_id))

        # Inits any dropped tables
        self.init_season()

    def purge_players(self, server_members: list):
        # Get rid of all players in the Profiles db but not in the server
        removed_players = []
        player_ids = self.execute_query_no_arg(db_strings.GET_ALL_PROFILES_PLAYER_ID)
        for player in player_ids:
            if player.id not in server_members:
                self.execute_commit_query(db_strings.DELETE_PROFILE, player)
                removed_players.append(player)
            self.conn.commit()
        return removed_players  # return what players we removed

    def update_season_end(self, server_id: int):
        # Disables or enables the season
        season_end_status = self.execute_query(db_strings.GET_SETTINGS, server_id)
        season_end_status = season_end_status[0][6]

        if season_end_status is 0:
            end_time = int(time.time())
        else:
            end_time = 0
        self.execute_commit_query(db_strings.UPDATE_SEASON_END, (end_time, server_id))
        self.conn.commit()

    def get_next_team_id(self, server_id: int):
        # returns the next scrim_id in the db
        last_team_id = self.execute_query(db_strings.GET_SETTINGS, server_id)
        last_team_id = last_team_id[0][2]
        next_team_id = last_team_id + 1
        self.execute_commit_query(db_strings.UPDATE_LAST_SCRIM, (next_team_id, server_id))

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
                self.execute_commit_query(db_strings.UPDATE_PLAYER_SET_STAT, (player_game_wins, player_game_loses,
                                                                              player_id))

        for player in beta_team.players:
            if not player.active_sub:
                player_id = player.player_id

                player_row = self.execute_query(db_strings.GET_PLAYER, player_id)
                player_game_wins = player_row[5] + beta_win
                player_game_loses = player_row[6] + beta_loss
                self.execute_commit_query(db_strings.UPDATE_PLAYER_SET_STAT, (player_game_wins, player_game_loses,
                                                                              player_id))
        self.conn.commit()

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

            self.execute_commit_query(db_strings.UPDATE_PLAYER_RANK, (player_rank_mu, player_rank_sigma, player_id))

            player_row = self.execute_query(db_strings.GET_PLAYER, player_id)
            player_game_wins = player_row[3] + alpha_win
            player_game_loses = player_row[4] + alpha_loss
            self.execute_commit_query(db_strings.UPDATE_PLAYER_GAME_STAT,
                                      (player_game_wins, player_game_loses, player_id))

        for player in beta_team.players:
            player_id = player.player_id
            player_rank_mu = player.rating.mu
            player_rank_sigma = player.rating.sigma

            self.execute_commit_query(db_strings.UPDATE_PLAYER_RANK, (player_rank_mu, player_rank_sigma, player_id))

            player_row = self.execute_query(db_strings.GET_PLAYER, player_id)
            player_game_wins = player_row[3] + beta_win
            player_game_loses = player_row[4] + beta_loss
            self.execute_commit_query(db_strings.UPDATE_PLAYER_GAME_STAT,
                                      (player_game_wins, player_game_loses, player_id))

        scrim_row = self.execute_query(db_strings.GET_SCRIM, scrim_id)
        alpha_score = scrim_row[3]
        beta_score = scrim_row[4]

        if result is Result.ALPHA_WIN:
            alpha_score += 1
        else:
            beta_score += 1

        self.execute_query(db_strings.UPDATE_SCRIM_SCORE, (alpha_score, beta_score, scrim_id))

        self.conn.commit()
