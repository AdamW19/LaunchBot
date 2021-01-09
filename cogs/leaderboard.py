import asyncio

import DiscordUtils
from discord.ext import commands
from discord.ext.commands import Cog

import config
from db.src import db_strings
from modules.leaderboard_helper import gen_leaderboard_embed, MAIN_LEADERBOARD_LIM, LEADERBOARD_SIZE


class Leaderboard(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self.global_lb_mes = None  # the message that contains the global leaderboard

        # self.bot.loop.create_task(self.leaderboard_update())  # TODO remove comment

    async def leaderboard_update(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)  # Sometimes the bot won't actually be ready, so an extra 5 sec helps
        while not self.bot.is_closed():
            print("[LPBot] Updating global leaderboard...")

            db_settings = self.db.execute_query(db_strings.GET_SETTINGS, config.launchpoint_server_id)[0]
            db_curr_season = db_settings[4]
            db_leaderboard = db_settings[3]

            leaderboard = self.db.execute_query_no_arg(db_strings.GET_LEADERBOARD)
            embed = gen_leaderboard_embed(leaderboard, 0, db_curr_season)

            # embed is none iff there's no one on the leaderboard
            if embed is not None:
                # on first run or on reboot, get the db entry (also check if internal lb id ≠ db id at season change
                if self.global_lb_mes is None or self.global_lb_mes.id is not db_leaderboard:
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
            embeds.append(gen_leaderboard_embed(leaderboard, i, db_curr_season))  # TODO fix empty embeds

        # Sets up pagination, thank you libraries
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx=ctx, remove_reactions=True, auto_footer=True)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⏪', "back")
        paginator.add_reaction('🛑', "lock")
        paginator.add_reaction('⏩', "next")
        paginator.add_reaction('⏭️', "last")
        await paginator.run(embeds)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
