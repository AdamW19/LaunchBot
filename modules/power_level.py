from enum import Enum, auto
import trueskill

A_WIN_RANK = [0, 1]
B_WIN_RANK = [1, 0]

MATCH_THRESHOLD = 15  # min number of matches to play before displaying player level


class Result(Enum):
    ALPHA_WIN = auto()
    BETA_WIN = auto()


class Player:
    def __init__(self, environment: trueskill.TrueSkill, player_id: int, mu: float = None, sigma: float = None):
        # Remember, mu is player's mean power level and sigma is std dev (sigma^2 is variance)
        self.player_id = player_id
        self.rating = environment.create_rating(mu, sigma)
        self.active_sub = False  # For players that finished a set but wasn't there at the beginning

    def __str__(self):
        return "Player {} with mu = {} and sigma = {}".format(self.player_id, self.rating.mu, self.rating.sigma)

    def to_database(self):
        # returns what is needed for the database
        return self.player_id, self.active_sub, self.rating.mu, self.rating.sigma


class Team:
    def __init__(self, players: list, captain: Player = None):
        # We maintain active and inactive players/subs, along with the captain and how many games were played
        self.players = players
        self.captain = captain

    def add_sub(self, new_player: Player, leaving_player: Player = None):
        # add sub player
        self.players.append(new_player)
        new_player.active_sub = True

        # remove the person the sub replaced from the active lineup
        if leaving_player is not None and leaving_player in self.players:
            self.players.remove(leaving_player)

    def __str__(self):
        # Mildly complex string builder for a team, but is good for the hash function
        team_str = "Team "
        if len(self.players) is not 0:
            team_str += "with players:"
            for team_player in self.players:
                team_str += "\n" + str(team_player)

        if self.captain is not None:
            team_str += "\nCaptain is player {}".format(self.captain.player_id)

        return team_str

    def to_database(self):
        # returns what is needed for the database
        return self.players, self.captain


def calc_new_rating(environment: trueskill.TrueSkill, team_alpha: Team, team_beta: Team, result: Result):
    """ Calculates new rating for team members after a match """
    team_a_players = tuple([player_a.rating for player_a in team_alpha.players])
    team_b_players = tuple([player_b.rating for player_b in team_beta.players])

    team_pattern = [team_a_players, team_b_players]

    # Generate new scores
    if result is Result.ALPHA_WIN:
        new_scores = environment.rate(team_pattern, A_WIN_RANK)
    else:
        new_scores = environment.rate(team_pattern, B_WIN_RANK)

    # Update team scores
    new_team_a_scores = new_scores[0]
    new_team_b_scores = new_scores[1]
    for i in range(len(new_team_a_scores)):
        team_alpha.players[i].rating = new_team_a_scores[i]
    for i in range(len(new_team_b_scores)):
        team_beta.players[i].rating = new_team_b_scores[i]


# For testing purposes
"""env = trueskill.TrueSkill(draw_probability=0)
team_a = Team(players=[Player(env, 0), Player(env, 1), Player(env, 2), Player(env, 3)])
team_b = Team(players=[Player(env, 4), Player(env, 5), Player(env, 6), Player(env, 7)], captain=Player(env, 7))
calc_new_rating(env, team_a, team_b, Result.BETA_WIN)
calc_new_rating(env, team_a, team_b, Result.ALPHA_WIN)
calc_new_rating(env, team_a, team_b, Result.BETA_WIN)
calc_new_rating(env, team_a, team_b, Result.ALPHA_WIN)
calc_new_rating(env, team_a, team_b, Result.BETA_WIN)
calc_new_rating(env, team_a, team_b, Result.ALPHA_WIN)
calc_new_rating(env, team_a, team_b, Result.BETA_WIN)

print(team_a)

print(team_b)"""

