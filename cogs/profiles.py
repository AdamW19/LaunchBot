import discord
from discord.ext import commands
import config
from db.cogs import db_strings
from modules import checks
from modules.power_level import MATCH_THRESHOLD
import re


class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db

    async def cog_check(self, ctx):
        # Checks to make sure we're not in a PM
        if not ctx.message.guild:
            return False
        return True

    @commands.group(case_insensitive=True, invoke_without_command=True, aliases=["p"])
    async def profile(self, ctx, *args):
        embed = None
        if len(args) == 0:  # If there's no arguments, we want
            embed = await self.gen_profile_embed(ctx.author)
        else:
            if len(args) == 1:  # if there's exactly 1 argument, maybe it's a mention or a user id
                mention = ctx.message.mentions
                user_id = args[0]

                if len(mention) == 0:  # If there's no mention, maybe it's a user id
                    user = self.bot.get_user(user_id)
                    if user is not None:  # if it is a user id, use that
                        embed = await self.gen_profile_embed(user)
                else:
                    embed = await self.gen_profile_embed(mention[0])  # if it is a mention, use that

        if embed is None:  # If parsing failed, return error message
            await ctx.send(":x: Profile not found. Please make your profile with `l?profile set [fc]`. If you tried "
                           "to get another user's profile, the user did not set up their profile yet.")
        else:  # otherwise send the embed
            await ctx.send(embed=embed)

    @profile.command()
    @commands.check(checks.user_is_developer)
    async def debug(self, ctx, *args):
        # TODO remove command once we're in production
        player_id = ctx.author.id
        switch = args[0]
        rank_mu = args[1]
        rank_sigma = args[2]
        num_game_win = args[3]
        num_game_loss = args[4]
        num_set_win = args[5]
        num_set_loss = args[6]

        if switch is "new":
            self.db.execute_commit_query(db_strings.INSERT_PLAYER, (player_id, rank_mu, rank_sigma, num_game_win,
                                                                    num_game_loss, num_set_win, num_set_loss))
        elif switch is "update":
            self.db.execute_commit_query("UPDATE Player SET rank_mu = ?, rank_sigma = ?, num_game_win = ?, "
                                         "num_game_loss = ?, num_set_win = ?, num_set_loss = ? WHERE player_id = ? ",
                                         (rank_mu, rank_sigma, num_game_win, num_game_loss, num_set_win,
                                          num_set_loss, player_id))
        else:
            self.db.execute_commit_query("DELETE FROM Player WHERE player_id = ?", player_id)

        await ctx.send("successful")

    @profile.command(name="set", aliases=["s"])
    async def set_profile(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(":x: You need to provide your Nintendo Switch Friend Code!")
        elif len(args) == 1:
            fc_check = re.search("^SW(?:-[0-9]{4}){3}$", args[0])  # Checking for "SW-0000-0000-0000"
            if not fc_check:
                fc_check = re.search("^(?:[0-9]{4}-){2}[0-9]{4}$", args[0])  # Checking for "0000-0000-0000"
                if not fc_check:  # If we couldn't find it, send error
                    await ctx.send(":x: Could not parse your Nintendo Switch Friend Code. Make sure it's formatted "
                                   "like `SW-0000-0000-0000` or `0000-0000-0000`.")
                    return
                else:
                    switch_fc = args[0]
            else:
                switch_fc = args[0][3:]  # we just want the numbers, not the prefix `SW-`

            # On success, insert the new profile, print success message and the profile
            self.db.execute_commit_query(db_strings.INSERT_PROFILE, (ctx.author.id, switch_fc))
            await ctx.send(":white_check_mark: Profile successfully made:")
            embed = await self.gen_profile_embed(ctx.author)
            await ctx.send(embed=embed)

    @profile.command(name="delete", aliases=["d"])
    async def remove_profile(self, ctx):
        profile = self.db.execute_query(db_strings.GET_PROFILE, ctx.author.id)  # Check if their profile exists
        if len(profile) > 0:
            self.db.execute_commit_query(db_strings.DELETE_PROFILE, ctx.author.id)  # If it does delete it
            await ctx.send(":white_check_mark: Profile successfully deleted.")
        else:
            await ctx.send(":x: Profile not found.")  # Otherwise send error

    async def gen_profile_embed(self, guild_user: discord.Member):
        profile = self.db.execute_query(db_strings.GET_PROFILE, guild_user.id)  # Get profile
        player = self.db.execute_query(db_strings.GET_PLAYER, guild_user.id)  # Get player

        if len(profile) == 0 and len(player) == 0:  # If both are None, return None
            return None

        title = "Profile -- " + guild_user.name
        thumbnail = guild_user.avatar_url
        embed = discord.Embed(title=title, color=config.embed_color)
        embed.set_thumbnail(url=thumbnail)

        embed.add_field(name="Friend Code", value=profile[0][1])

        if len(player) > 0:  # Checking to see if the user is in Launchpoint/in the Players table

            # Squash and parse, then add to the embed
            player = player[0]

            num_games_won = player[3]
            num_games_lost = player[4]
            num_sets_won = player[5]
            num_sets_lost = player[6]

            total_games = num_games_won + num_games_lost
            total_sets = num_sets_won + num_sets_lost

            if total_games > MATCH_THRESHOLD:  # Making sure the player has enough games played before showing rating
                player_rating = round(player[1], 2)  # round to 2 decimal places
            else:
                player_rating = "Play {} more game(s)\nto view rank.".format(MATCH_THRESHOLD - total_games)

            embed.add_field(name="Player Level", value=player_rating)
            embed.add_field(name=" \u200b", value="** **\n", inline=False)  # Spacer to make embed 2 columns
            embed.add_field(name="Game Stats", value="Games won: " + str(num_games_won) +
                                                     "\nGames lost: " + str(num_games_lost))
            embed.add_field(name="Total Games", value=str(total_games))
            embed.add_field(name=" \u200b", value="** **\n", inline=False)
            embed.add_field(name="Set Stats", value="Sets won: " + str(num_sets_won) +
                                                    "\nSets lost: " + str(num_sets_lost))
            embed.add_field(name="Total Sets", value=str(total_sets))
        return embed


def setup(bot):
    bot.add_cog(Profiles(bot))
