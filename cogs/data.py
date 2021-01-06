import asyncio

import discord
from discord.ext import commands
from db.src.data_db import DataDB, get_all_db_files

import csv

import config


class Data(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db

    @commands.group(case_insensitive=True, invoke_without_command=True, aliases=["gdpr", "ccpa", "data"])
    async def privacy(self, ctx):
        # sends out a good help embed
        embed = discord.Embed(title="Privacy Help", color=config.embed_color, description="Alias for command are "
                                                                                           "`gdpr`, `ccpa`, `data`, or "
                                                                                           "`privacy`.")
        embed.add_field(name="Purpose", value="Due to GDPR and CCPA, we are required to allow you to download and "
                                              "delete your data from our databases.\n"
                                              "Downloading your data will result in the bot DM-ing you a `.csv` file "
                                              "that contains all the data we have of you. This includes your profile, "
                                              "your player information, and any drafts you were in.\n"
                                              "Deleting your data irrevocably deletes all of our data of you.",
                        inline=False)
        embed.add_field(name="Download", value="The subcommand for downloading your data is `download`, `dl`, `d`, "
                                               "or `get`.")
        embed.add_field(name="Delete", value="The subcommand for deleting your data is `delete` or `purge`.")

        await ctx.send(embed=embed)

    @privacy.command(aliases=["dl", "d", "get"])
    async def download(self, ctx):
        # Generate embed explaining how the file works
        discord_id = ctx.author.id
        explain_embed = discord.Embed(title="About your Files", description="Information about your data.")
        explain_embed.add_field(name="File Names", value="The file name represents the season associated with it with "
                                                         "your Discord ID.\n"
                                                         "For example, Season 1's data is in "
                                                         "`{}-1.csv`.".format(str(discord_id)), inline=False)
        explain_embed.add_field(name="File Format", value="The first 2 rows are your profile information as saved in "
                                                      "the database. The next 2 rows are your player information, "
                                                      "if you were part of Launchpoint for that season. The rest "
                                                      "contains draft information, as saved in the database. Draft "
                                                      "information contains team id, scrim id, if you were a "
                                                      "sub/captain, and player ids of the people you played with.\n"
                                                      "Do note that the amount of players may change from scrim to "
                                                      "scrim.")
        # Get all db files
        db_files = get_all_db_files()

        uploaded_files = []  # array of discord Files

        for file in db_files:
            data_db = DataDB(file, None)  # None is fine b/c we're not gonna start a new season

            # Get all season info and csv it
            season_id, profile_info, player_info, team_info = data_db.get_player_info(ctx.author.id, ctx.guild.id)

            file_name = str(ctx.author.id) + "-" + str(season_id) + ".csv"
            with open(file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Player ID", "Friend Code"])  # Headers for each info
                writer.writerow(profile_info)
                writer.writerow(["Player ID", "Mu", "Sigma", "Num Game Wins", "Num Game Losses", "Num Set Wins",
                                 "Num Set Losses"])
                writer.writerow(player_info)

                writer.writerow(["Team Id", "Scrim Id", "Is Sub", "Is Captain", "*Played With"])
                for scrim in team_info:
                    row = [scrim[x] for x in range(4)]  # team id, scrim id, is_sub, is_captain
                    for player in scrim[1]:
                        row.append(player)

            uploaded_files.append(discord.File(file_name))

        await ctx.author.send(embed=explain_embed)
        await ctx.author.send(files=uploaded_files)
        await ctx.send(":white_check_mark: DM-ed you everything we have of you.")

    @privacy.command(aliases=["purge"])
    async def delete(self, ctx):
        # sends warning message
        temp_message = await ctx.send(":warning: Are you sure you want to delete your data? "
                                      "You cannot recover your data after deletion. We recommend downloading your data "
                                      "via `l?data download`. Do note that we can not recover your data under any "
                                      "circumstance.\n\n"
                                      "To confirm your decision to **irreversibly** delete your data, "
                                      "react `👍` to this message within the next 15 seconds.")
        await temp_message.add_reaction("👍")

        def check(reaction, user):
            # check used to make sure reaction is from the original author and with the correct reaction
            return user == ctx.author and str(reaction.emoji) == "👍"

        try:
            await self.bot.wait_for('reaction_add', timeout=15.0, check=check)  # wait for response

        except asyncio.TimeoutError:
            # If no response, cancel and exit
            await temp_message.edit(content="Operation canceled. Did not delete your data.")
            await temp_message.remove_reaction(emoji="👍", member=ctx.bot.user)
        else:
            # Otherwise start the purge
            db_files = get_all_db_files()

            for file in db_files:
                data_db = DataDB(file, None)
                data_db.purge_player_info(ctx.author.id)

            # send confirmation and a nice thank you
            await ctx.send(":white_check_mark: Successfully deleted your profile, player, and team/scrim information. "
                           "It may take up to 7 days from now to purge your everything from our backups. Regardless, "
                           "thank you for using LaunchBot!")


def setup(bot):
    bot.add_cog(Data(bot))
