from enum import Enum, auto
import trueskill

A_WIN_RANK = [0, 1]
B_WIN_RANK = [1, 0]


class Result(Enum):
    ALPHA_WIN = auto()
    BETA_WIN = auto()


class Player:
    def __init__(self, environment: trueskill.TrueSkill, player_id: int, mu: float = None, sigma: float = None):
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
    def __init__(self, active_players: list, captain: Player = None):
        # We maintain active and inactive players/subs, along with the captain and how many games were played
        self.active_players = active_players
        self.inactive_players = []
        self.captain = captain
        self.play_time = {}

        for active_player in self.active_players:
            self.play_time[active_player.player_id] = 0

    def add_sub(self, new_player: Player, leaving_player: Player = None):
        # add sub player
        self.play_time[new_player.player_id] = 0
        self.active_players.append(new_player)

        # remove the person the sub replaced from the active lineup
        if leaving_player is not None and leaving_player in self.active_players:
            self.active_players.remove(leaving_player)
            self.inactive_players.append(leaving_player)

    def __str__(self):
        # Mildly complex string builder for a team, but is good for the hash function
        team_str = "Team "
        if len(self.active_players) is not 0:
            team_str += "with players:"
            for team_player in self.active_players:
                team_str += "\n" + str(team_player)

        if self.captain is not None:
            team_str += "\nCaptain is player {}".format(self.captain.player_id)

        if len(self.inactive_players) is not 0:
            team_str += "\nWith subs:"
            for inactive in self.inactive_players:
                team_str += "\n" + str(inactive)
        return team_str

    def __hash__(self):
        return hash(str(self))

    def to_database(self):
        # returns what is needed for the database
        return self.active_players, self.inactive_players, self.captain, self.play_time


def calc_new_rating(environment: trueskill.TrueSkill, team_alpha: Team, team_beta: Team, result: Result):
    """ Calculates new rating for team members after a match """
    team_a_players = tuple([player_a.rating for player_a in team_alpha.active_players])
    team_b_players = tuple([player_b.rating for player_b in team_beta.active_players])

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
        team_alpha.active_players[i].rating = new_team_a_scores[i]
    for i in range(len(new_team_b_scores)):
        team_beta.active_players[i].rating = new_team_b_scores[i]

    # Update play time
    for alpha_player in team_alpha.active_players:
        team_alpha.play_time[alpha_player.player_id] += 1

    for beta_player in team_beta.active_players:
        team_beta.play_time[beta_player.player_id] += 1


# For testing purposes
'''env = trueskill.TrueSkill(draw_probability=0)
team_a = Team(active_players=[Player(env, 0), Player(env, 1), Player(env, 2), Player(env, 3)])
team_b = Team(active_players=[Player(env, 4), Player(env, 5), Player(env, 6), Player(env, 7)], captain=Player(env, 7))
calc_new_rating(env, team_a, team_b, Result.BETA_WIN)

team_a.add_sub(Player(env, 8))
team_b.inactive_players.append(Player(env, 9))

print(team_a)
print(hash(team_a))

print(team_b)
print(hash(team_b))'''
