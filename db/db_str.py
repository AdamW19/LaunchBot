# Pycharm is complaining about the tables not existing but it's fine

INIT_PROFILE_TABLE = "CREATE TABLE IF NOT EXISTS Profile (" \
                     "player_id INTEGER PRIMARY KEY, " \
                     "fc TEXT" \
                     ");"

INIT_PLAYER_TABLE = "CREATE TABLE IF NOT EXISTS Player (" \
                    "player_id INTEGER PRIMARY KEY, " \
                    "rank_mu TEXT NOT NULL, " \
                    "rank_sigma TEXT NOT NULL, " \
                    "num_game_win INTEGER NOT NULL, " \
                    "num_game_loss INTEGER NOT NULL, " \
                    "num_set_win INTEGER NOT NULL, " \
                    "num_set_loss INTEGER NOT NULL," \
                    "FOREIGN KEY (player_id)" \
                    "REFERENCES Profile (player_id)" \
                    "ON DELETE CASCADE " \
                    "ON DELETE CASCADE " \
                    ");"

INIT_TEAM_TABLE = "CREATE TABLE IF NOT EXISTS Team ( " \
                  "team_id INTEGER PRIMARY KEY, " \
                  "player_id INTEGER NOT NULL, " \
                  "is_sub INTEGER NOT NULL, " \
                  "FOREIGN KEY (player_id)" \
                  "REFERENCES Player (player_id)" \
                  "ON DELETE NO ACTION " \
                  "ON UPDATE CASCADE " \
                  ");"

INIT_SCRIM_TABLE = "CREATE TABLE IF NOT EXISTS Scrim ( " \
                   "scrim_id INTEGER PRIMARY KEY, " \
                   "winning_team INTEGER, " \
                   "losing_team INTEGER, " \
                   "winner_score INTEGER, " \
                   "loser_score INTEGER," \
                   "is_final INTEGER," \
                   "FOREIGN KEY (winning_team) " \
                   "REFERENCES Team (team_id) " \
                   "ON DELETE NO ACTION " \
                   "ON UPDATE CASCADE, " \
                   "FOREIGN KEY (losing_team) " \
                   "REFERENCES Team (team_id) " \
                   "ON DELETE NO ACTION " \
                   "ON UPDATE CASCADE " \
                   ");"

INIT_SETTING_TABLE = "CREATE TABLE IF NOT EXISTS Settings ( " \
                     "server_id INTEGER PRIMARY KEY, " \
                     "map_list TEXT NOT NULL, " \
                     "season_start INTEGER NOT NULL, " \
                     "season_end INTEGER NOT NULL " \
                     ");"

INSERT_PROFILE = "INSERT INTO Profile(player_id, fc) " \
                 "VALUES (?, ?)"

INSERT_PLAYER = "INSERT INTO Player(player_id, rank_mu, rank_sigma, num_game_win, num_game_loss," \
                "num_set_win, num_set_loss)" \
                "VALUES (?, ?, ?, ?, ?, ?, ?)"

INSERT_TEAM = "INSERT INTO Team(team_id, player_id, is_sub, is_final)" \
              "VALUES (?, ?, ?, ?)"

INSERT_SCRIM = "INSERT INTO Scrim(scrim_id, winning_team, losing_team, winner_score, loser_score)" \
               "VALUES(?, ?, ?, ?, ?)"
