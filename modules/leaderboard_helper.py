import discord
from modules.power_level import MATCH_THRESHOLD
import datetime
import config

MAIN_LEADERBOARD_LIM = 10  # Max amount of players in global leaderboard and in each page for pagination
LEADERBOARD_SIZE = 50  # Total number of players for pagination


async def finalize_leaderboard(msg_id: int, curr_season: int, leaderboard: list, ctx):
    if msg_id is 0:
        return

    msg = await ctx.guild.get_channel(config.launchpoint_leaderboard_id).fetch_message(msg_id)

    title = "Final Season " + str(curr_season) + " Leaderboard -- Positions " + "1 to 10"
    members = await ctx.guild.fetch_members(limit=1000)
    member_ids = [user.id for user in members]
    current_leaderboard = parse_leaderboard(leaderboard, 0, member_ids)
    players_str, games_str, rank_str = gen_embed_str(0, current_leaderboard)

    embed = discord.Embed(title=title, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text="\u200b", icon_url="https://cdn.discordapp.com/emojis/791152168429813800.png")

    # We want to print something, so if there's an error print that no one's reached the leader board yet.
    embed.add_field(name="Player", value=players_str)
    embed.add_field(name="Rank", value=games_str)
    embed.add_field(name="Total Games", value=rank_str)

    await msg.edit(embed=embed)


def gen_embed_str(offset: int, current_leaderboard: list):
    players_str = ""
    games_str = ""
    rank_str = ""

    # offset_print is used for printing into the embed
    offset_print = offset
    for player in current_leaderboard:

        players_str += str(offset_print + 1) + ". " + player[0] + "\n"
        games_str += str(player[1]) + "\n"
        rank_str += str(player[2]) + "\n"
        offset_print += 1

    # Fills in any missing positions, should any exist
    for i in range(len(current_leaderboard), MAIN_LEADERBOARD_LIM, 1):
        players_str += str(offset_print + 1) + ". None" + "\n"
        games_str += "** **\n"  # Tricks discord.py into sending an "empty" embed field value
        rank_str += "** **\n"
        offset_print += 1

    return players_str, games_str, rank_str


def parse_leaderboard(leaderboard, offset, players):
    # this parses the leaderboard dict and removes non-eligible players
    total_skipped = 0  # to keep track of how much more we need to go through when players don't qualify
    current_leaderboard = []
    for i in range(offset, offset + MAIN_LEADERBOARD_LIM + total_skipped):
        # Exit loop if we've reached the end of the given leaderboard
        if len(leaderboard) <= i:
            break

        player = leaderboard[i]
        player_id = player[0]
        player_total_games = player[1]
        player_rank = round(player[2], 2)  # we wanna round the rank to 2 decimal places, a la profiles

        # Skip if the player hasn't played enough games or if the player isn't in the server anymore
        if player_total_games < MATCH_THRESHOLD or player_id not in players:
            total_skipped += 1
            continue

        pingable_player = "<@{}>".format(player_id)
        current_leaderboard.append([pingable_player, player_rank, player_total_games])
    return current_leaderboard


def gen_leaderboard_embed(leaderboard: list, offset: int, season_num: int, overwrite_empty: bool, members: list):
    position_str = str(offset + 1) + " to " + str(offset + MAIN_LEADERBOARD_LIM)  # Used for title
    title = "Season " + str(season_num) + " Leaderboard -- Positions " + position_str

    embed = discord.Embed(title=title, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text="\u200b", icon_url="https://cdn.discordapp.com/emojis/791152168429813800.png")

    current_leaderboard = parse_leaderboard(leaderboard, offset, members)  # Get leaderboard based off offset

    players_str, games_str, rank_str = gen_embed_str(offset, current_leaderboard)

    # We want to print something, so if there's an error print that no one's reached the leader board yet.
    if len(current_leaderboard) is not 0 or overwrite_empty:
        embed.add_field(name="Player", value=players_str)
        embed.add_field(name="Rank", value=games_str)
        embed.add_field(name="Total Games", value=rank_str)
    else:
        embed.add_field(name="No players yet", value="No players have reached the required {} total "
                                                     "games yet.".format(MATCH_THRESHOLD))

    return embed
