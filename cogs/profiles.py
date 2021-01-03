import discord
from discord.ext import commands
import config
from db import db_strings
from modules.power_level import MATCH_THRESHOLD
import re


class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db

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
                        embed = self.gen_profile_embed(user)
                else:
                    embed = self.gen_profile_embed(mention[0])  # if it is a mention, use that

        if embed is None:  # If parsing failed, return error message
            await ctx.send(":x: Profile not found. Please make your profile with `l?profile set [fc]`. If you gave a "
                           "user, the user did not set up their profile yet.")
        else:  # otherwise send the embed
            await ctx.send(embed=embed)

    @profile.command(name="set", aliases=["s"])
    async def set_profile(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(":x: You need to provide your Nintendo Switch Friend Code!")
        elif len(args) == 1:
            fc_check = re.search("^SW(?:-[0-9]{4}){3}$", args[0])  # Checking for "SW-0000-0000-0000"
            if not fc_check:
                fc_check = re.search("^(?:[0-9]{4}-){2}[0-9]{4}$", args[0])  # Checking for "0000-0000-0000"
                if not fc_check:  # If we couldn't find it, send error
                    await ctx.send(":x: Could not parse your Switch Friend Code. Make sure it's formatted like "
                                   "`SW-0000-0000-0000` or `0000-0000-0000`.")
                    return
                else:
                    switch_fc = args[0]
            else:
                switch_fc = args[0][3:]

            # On success, insert the new profile, print success message and the profile
            self.db.execute_query(db_strings.INSERT_PROFILE, (ctx.author.id, switch_fc))
            await ctx.send(":white_check_mark: Profile successfully made:")
            embed = self.gen_profile_embed(ctx.author.id)
            await ctx.send(embed=embed)

    @profile.command(name="delete", aliases=["d"])
    async def remove_profile(self, ctx):
        profile = self.db.execute_query(db_strings.GET_PROFILE, ctx.author.id)  # Check if their profile exists
        if len(profile) > 0:
            self.db.execute_query_nr(db_strings.DELETE_PROFILE, ctx.author.id)  # If it does delete it
            await ctx.send(":white_check_mark: Profile successfully deleted.")
        else:
            await ctx.send(":x: Profile not found.")  # Otherwise send error

    async def gen_profile_embed(self, guild_user: discord.Member):
        profile = self.db.execute_query(db_strings.GET_PROFILE, guild_user.id)  # Get profile
        player = self.db.execute_query(db_strings.GET_PLAYER, guild_user.id)  # Get player

        if profile and player is None:  # If both are None, return None
            return None

        title = "Profile -- " + guild_user.name
        thumbnail = guild_user.avatar_url
        embed = discord.Embed(title=title, color=config.embed_color)
        embed.set_thumbnail(url=thumbnail)

        embed.add_field(name="Friend Code", value=profile[1])

        if len(player) > 0:  # Checking to see if the user is in Launchpoint/in the Players table

            # Squash and parse, then add to the embed
            player = player[0]

            num_games_won = player[4]
            num_games_lost = player[5]
            num_sets_won = player[6]
            num_sets_lost = player[7]

            total_games = num_games_won + num_games_lost

            if total_games <= MATCH_THRESHOLD:  # Making sure the player has enough games played before showing rating
                player_rating = player[1]
            else:
                player_rating = "N/A -- You need to play {} more games!".format(MATCH_THRESHOLD - total_games)

            embed.add_field(name="Player Level", value=player_rating)
            embed.add_field(name="Game Stats", value="Number of games won: " + num_games_won +
                                                     "\nNumber of games lost: " + num_games_lost)
            embed.add_field(name="Set Stats", value="Number of sets won: " + num_sets_won +
                                                    "\nNumber of sets lost: " + num_sets_lost)
        return embed
