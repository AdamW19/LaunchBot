from enum import Enum, auto
import trueskill

A_WIN_RANK = [0, 1]
B_WIN_RANK = [1, 0]


class Result(Enum):
    ALPHA_WIN = auto()
    BETA_WIN = auto()


class Player:
    def __init__(self, environment: trueskill.TrueSkill, player_id: str, mu: float = None, sigma: float = None):
        # Remember, mu is player's mean power level and sigma is std dev (sigma^2 is variance)
        self.player_id = player_id
        self.rating = environment.create_rating(mu, sigma)

    def __str__(self):
        return "Player {} with mu = {} and sigma = {}".format(self.player_id, self.rating.mu, self.rating.sigma)

    def __hash__(self):
        return hash(str(self))

    def to_database(self):
        # returns what is needed for the database
        return self.player_id, self.rating.mu, self.rating.sigma


class Team:
    def __init__(self, players: list, captain: Player = None):
        self.players = players
        self.captain = captain
        self.subs = []

    def __str__(self):
        # Mildly complex string builder for a team, but is good for the hash function
        team_str = "Team "
        if len(self.players) is not 0:
            team_str += "with players "
            for team_player in self.players:
                team_str += str(team_player.player_id) + " "

        if self.captain is not None:
            team_str += "with captain {} ".format(self.captain.player_id)

        if len(self.subs) is not 0:
            team_str += "with subs "
            for sub in self.subs:
                team_str += str(sub.player_id) + " "
        return team_str

    def __hash__(self):
        return hash(str(self))

    def to_database(self):
        # returns what is needed for the database
        return self.players, self.captain, self.subs


def calc_new_rating(environment: trueskill.TrueSkill, team_alpha: Team, team_beta: Team, result: Result):
    """ Calculates new rating for team members after a match """
    team_a_players = tuple([player_a.rating for player_a in team_alpha.players])
    team_b_players = tuple([player_b.rating for player_b in team_beta.players])
    team_pattern = [team_a_players, team_b_players]

    if result is Result.ALPHA_WIN:
        new_scores = environment.rate(team_pattern, A_WIN_RANK)
    else:
        new_scores = environment.rate(team_pattern, B_WIN_RANK)

    new_team_a_scores = new_scores[0]
    new_team_b_scores = new_scores[1]

    for i in range(len(new_team_a_scores)):
        team_alpha.players[i].rating = new_team_a_scores[i]

    for i in range(len(new_team_b_scores)):
        team_beta.players[i].rating = new_team_b_scores[i]


# For testing purposes
'''env = trueskill.TrueSkill(draw_probability=0)
team_a = Team(players=(Player(env, 0), Player(env, 1), Player(env, 2), Player(env, 3)))
team_b = Team(players=(Player(env, 4), Player(env, 5), Player(env, 6), Player(env, 7)))
calc_new_rating(env, team_a, team_b, Result.BETA_WIN)

print(team_a)
print(hash(team_a))
for player in team_a.players:
    print(player)
    print(hash(player))

print(team_b)
print(hash(team_b))
for player in team_b.players:
    print(player)
    print(hash(player))'''
