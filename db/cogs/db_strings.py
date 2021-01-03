# Pycharm is complaining about the tables not existing but it's fine

INIT_PROFILE_TABLE = """CREATE TABLE IF NOT EXISTS Profile (
                        player_id INTEGER PRIMARY KEY, 
                        fc TEXT
                        );"""

INIT_PLAYER_TABLE = """CREATE TABLE IF NOT EXISTS Player (
                       player_id INTEGER PRIMARY KEY, 
                       rank_mu TEXT NOT NULL, 
                       rank_sigma TEXT NOT NULL, 
                       num_game_win INTEGER NOT NULL, 
                       num_game_loss INTEGER NOT NULL, 
                       num_set_win INTEGER NOT NULL, 
                       num_set_loss INTEGER NOT NULL,
                       FOREIGN KEY (player_id)
                           REFERENCES Profile (player_id)
                           ON DELETE CASCADE 
                           ON UPDATE CASCADE 
                      );"""  # TODO make player table independent b/c a player may not have a profile

INIT_TEAM_TABLE = """CREATE TABLE IF NOT EXISTS Team ( 
                     team_id INTEGER PRIMARY KEY, 
                     player_id INTEGER NOT NULL, 
                     is_sub INTEGER NOT NULL, 
                     FOREIGN KEY (player_id)
                        REFERENCES Player (player_id)
                        ON DELETE NO ACTION
                        ON UPDATE CASCADE
                     );"""

INIT_SCRIM_TABLE = """CREATE TABLE IF NOT EXISTS Scrim (
                      scrim_id INTEGER PRIMARY KEY,
                      alpha_team INTEGER, 
                      beta_team INTEGER,
                      alpha_score INTEGER, 
                      beta_score INTEGER,
                      FOREIGN KEY (alpha_team) 
                        REFERENCES Team (team_id) 
                        ON DELETE NO ACTION 
                        ON UPDATE CASCADE, 
                      FOREIGN KEY (beta_team) 
                        REFERENCES Team (team_id) 
                        ON DELETE NO ACTION 
                        ON UPDATE CASCADE
                      );"""

INIT_SETTING_TABLE = """CREATE TABLE IF NOT EXISTS Settings (
                        server_id INTEGER PRIMARY KEY, 
                        map_list TEXT NOT NULL,
                        prev_team_id INTEGER,
                        season_num INTEGER NOT NULL,
                        season_start INTEGER NOT NULL,
                        season_end INTEGER NOT NULL
                        );"""

INSERT_PROFILE = """INSERT INTO Profile(player_id, fc)
                    VALUES (?, ?)"""

INSERT_PLAYER = """INSERT INTO Player(player_id, rank_mu, rank_sigma, num_game_win, num_game_loss,
                                      num_set_win, num_set_loss)
                   VALUES (?, ?, ?, ?, ?, ?, ?)"""

INSERT_TEAM = """INSERT INTO Team(team_id, player_id, is_sub)
                 VALUES (?, ?, ?)"""

INSERT_SCRIM = """INSERT INTO Scrim(scrim_id, alpha_team, beta_team, alpha_score, beta_score)
                  VALUES(?, ?, ?, ?, ?)"""

INSERT_SETTING = """INSERT INTO Settings(server_id, map_list, prev_team_id, season_num, season_start, season_end)
                    VALUES(?, ?, ?, ?, ?, ?)"""

GET_ALL_PROFILES_PLAYER_ID = """SELECT player_id FROM Profile"""

GET_PROFILE = """SELECT * FROM Profile 
                 WHERE player_id = ?"""

GET_PLAYER = """SELECT * FROM Player
                WHERE player_id = ?"""

GET_TEAM = """SELECT * FROM Team
               WHERE team_id = ?"""

GET_SCRIM = """SELECT * FROM Scrim
              WHERE scrim_id = ?"""

GET_SETTINGS = """SELECT ? FROM Settings
                  WHERE server_id = ?"""

UPDATE_PROFILE = """UPDATE Profile
                    SET fc = ?
                    WHERE player_id = ?"""

UPDATE_PLAYER_RANK = """UPDATE Player
                        SET rank_mu = ?,
                            rank_sigma = ?
                        WHERE player_id = ?"""

UPDATE_PLAYER_GAME_STAT = """UPDATE Player
                             SET num_game_win = ?, 
                                 num_game_loss = ?
                             WHERE player_id = ?"""

UPDATE_PLAYER_SET_STAT = """UPDATE Player
                            SET num_set_win = ?, 
                                num_set_loss = ?
                            WHERE player_id = ?"""

UPDATE_TEAM_SUB = """UPDATE Team
                     SET is_sub = ?
                     WHERE team_id = ? AND player_id = ?"""

UPDATE_SCRIM_SCORE = """UPDATE Scrim
                        SET alpha_score = ?,
                            loser_score = ?
                        WHERE scrim_id = ?"""

UPDATE_SETTING_MAPLIST = """UPDATE Settings
                            SET map_list = ?
                            WHERE server_id = ?"""

UPDATE_SEASON = """UPDATE Settings
                   SET season_num = ?,
                       season_start = ?,
                       season_end = ?
                   WHERE server_id = ?"""

UPDATE_SEASON_END = """UPDATE Settings
                       SET season_end = ?
                       WHERE server_id = ?"""

UPDATE_LAST_SCRIM = """UPDATE Settings
                       SET prev_team_id = ?
                       WHERE server_id = ?"""

DELETE_PROFILE = """DELETE FROM Profile
                    WHERE player_id = ?"""

DROP_PLAYER_TABLE = """DROP TABLE Player"""

DROP_TEAM_TABLE = """DROP TABLE Team"""

DROP_SCRIM_TABLE = """DROP TABLE Scrim"""
