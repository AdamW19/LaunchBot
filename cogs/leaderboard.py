import asyncio
import datetime

import DiscordUtils
import discord
from discord.ext import commands
from discord.ext.commands import Cog

import config
from db.src import db_strings
from modules.power_level import MATCH_THRESHOLD

MAIN_LEADERBOARD_LIM = 10  # Max amount of players in global leaderboard and in each page for pagination
LEADERBOARD_SIZE = 50  # Total number of players for pagination


class Leaderboard(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self.global_lb_mes = None  # the message that contains the global leaderboard

        self.bot.loop.create_task(self.leaderboard_update())

    async def leaderboard_update(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)  # Sometimes the bot won't actually be ready, so an extra 5 sec helps
        while not self.bot.is_closed():
            print("[LPBot] Updating leaderboard...")

            db_settings = self.db.execute_query(db_strings.GET_SETTINGS, config.launchpoint_server_id)[0]
            db_curr_season = db_settings[4]
            db_leaderboard = db_settings[3]

            leaderboard = self.db.execute_query_no_arg(db_strings.GET_LEADERBOARD)
            embed = self.gen_leaderboard_embed(leaderboard, 0, db_curr_season)

            # embed is none iff there's no one on the leaderboard
            if embed is not None:
                # on first run or on reboot, get the db entry
                if self.global_lb_mes is None:
                    # if it doesn't exist, make a new one and safe that as the global leaderboard
                    if db_leaderboard is None or db_leaderboard is 0:
                        self.global_lb_mes = await self.bot.get_channel(config.launchpoint_leaderboard_id).send(
                                                                                                            embed=embed)
                        self.db.execute_commit_query(db_strings.UPDATE_LEADERBOARD, (self.global_lb_mes.id,
                                                                                     config.launchpoint_server_id))
                    else:  # otherwise use the existing one as the leaderboard
                        self.global_lb_mes = await self.bot.get_channel(config.launchpoint_leaderboard_id).\
                            fetch_message(db_leaderboard)
                else:  # if we have the message update the leaderboard
                    await self.global_lb_mes.edit(embed=embed)
            await asyncio.sleep(20)  # TODO change this to a better value

    @commands.command(case_insensitive=True, aliases=["l", "rank", "ranks"])
    async def leaderboard(self, ctx):
        embeds = []
        leaderboard = self.db.execute_query_no_arg(db_strings.GET_LEADERBOARD)

        db_settings = self.db.execute_query(db_strings.GET_SETTINGS, config.launchpoint_server_id)[0]
        db_curr_season = db_settings[4]

        # Makes embeds for pagination, we want 5 10-player sized embeds sorta like the global leaderboard
        for i in range(0, LEADERBOARD_SIZE, MAIN_LEADERBOARD_LIM):
            embeds.append(self.gen_leaderboard_embed(leaderboard, i, db_curr_season))  # TODO fix empty embeds

        # Sets up pagination, thank you libraries
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx=ctx, remove_reactions=True, auto_footer=True)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⏪', "back")
        paginator.add_reaction('🛑', "lock")
        paginator.add_reaction('⏩', "next")
        paginator.add_reaction('⏭️', "last")
        await paginator.run(embeds)

    def gen_leaderboard_embed(self, leaderboard: list, offset: int, season_num: int):
        position_str = str(offset + 1) + " to " + str(offset + MAIN_LEADERBOARD_LIM)  # Used for title
        title = "Season " + str(season_num) + " Leaderboard -- Positions " + position_str

        embed = discord.Embed(title=title, timestamp=datetime.datetime.utcnow())
        # FIXME this is kinda sketchy but it works... maybe we should host the icon locally? something to think about
        embed.set_footer(text="\u200b", icon_url="https://cdn.discordapp.com/emojis/791152168429813800.png")

        current_leaderboard = self.parse_leaderboard(leaderboard, offset)  # Get leaderboard based off offset

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

        # We want to print something, so if there's an error print that no one's reached the leader board yet.
        if len(players_str) > 0 or len(games_str) > 0 or len(rank_str) > 0:
            embed.add_field(name="Player", value=players_str)
            embed.add_field(name="Rank", value=games_str)
            embed.add_field(name="Total Games", value=rank_str)
        else:
            embed.add_field(name="No players yet", value="No players have reached the required {} total "
                                                         "games yet.".format(MATCH_THRESHOLD))

        return embed

    @staticmethod
    def parse_leaderboard(leaderboard, offset):  # this parses the leaderboard dict and removes non-eligible players
        total_skipped = 0  # to keep track of how much more we need to go through when players don't qualify
        current_leaderboard = []
        for i in range(offset, offset + MAIN_LEADERBOARD_LIM + total_skipped):
            # Exit loop if we've reached the end of the given leaderboard
            if len(leaderboard) <= i:
                break

            player = leaderboard[i]
            player_id = player[0]
            player_total_games = player[1]
            player_rank = round(float(player[2]), 2)  # we wanna round the rank to 2 decimal places, a la profiles

            # Skip if the player hasn't played enough games or if the player isn't in the server anymore
            if player_total_games < MATCH_THRESHOLD:  # or self.bot.get_user(player_id) is None: TODO remove comment
                total_skipped += 1
                continue

            pingable_player = "<@{}>".format(player_id)
            current_leaderboard.append([pingable_player, player_rank, player_total_games])
        return current_leaderboard


def setup(bot):
    bot.add_cog(Leaderboard(bot))
