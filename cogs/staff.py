import asyncio

import config
import discord
from discord.ext import commands
from discord.ext.commands import Cog
from db.cogs import db_strings
from modules import code_parser


class Staff(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        # TODO make sure you edit this before launch, it disables staff/server675 checks
        # Checks to make sure we're not in a PM and we're not in another server
        if not ctx.message.guild:  # or ctx.message.guild.id != config.launchpoint_server_id:
            return False

        # Makes sure the person running this command is has the "Staff" role
        # staff_role = discord.utils.get(ctx.guild.roles, name="Staff")
        return True  # staff_role in ctx.author.roles

    @commands.group(case_insensitive=True, invoke_without_command=True, aliases=["change", "modify"])
    async def settings(self, ctx):
        embed = discord.Embed(title="Settings Help", color=config.embed_color, description="Alias for command are "
                                                                                           "`change`, `modify`, "
                                                                                           "`staff`, and `settings`.")
        embed.add_field(name="Map pool", value="The subcommand for mappool is `map-pool`, `map`, or `pool`. If you "
                                               "don't provide a valid [nkitten.net]("
                                               "http://nkitten.net/splatoon2/random/) code as an argument, "
                                               "the bot will print out the current map pool. Otherwise, it will update "
                                               "the current map pool according to the given code.", inline=False)
        embed.add_field(name="Season", value="The subcommand for season is `draft` and `launchpoint`.\n "
                                             "You can provide `pause`, `timeout`, `reopen`, or `open` as an argument "
                                             "to temporarily close or to reopen the season.\n "
                                             "You can also provide `start`. `init`, or `open` as an argument to start "
                                             "a season.", inline=False)
        embed.add_field(name="Eggs", value="Type `l?tenta` or `l?tent` for the best weapon", inline=False)

        embed.set_footer(text="Remember, you must have the Staff role to run these commands. ")

        await ctx.send(embed=embed)

    @settings.group(case_insensitive=True, invoke_without_command=True, aliases=["map-pool", "map", "pool"])
    async def mappool(self, ctx, *args):
        if len(args) == 0:
            map_list = self.bot.db.execute_query(db_strings.GET_SETTINGS, ctx.guild.id)
            map_list = map_list[0][1]
            map_dict = code_parser.parse_code_dict(map_list)
            map_str = code_parser.gen_maplist_str(map_dict)

            if len(map_list) is 0 or "error" in map_dict:
                await ctx.send(":x: No maplist set! Please set a maplist by providing one with this command.")
            else:
                await ctx.send("Current maplist:")
                await ctx.send("```" + map_str + "```")
        elif len(args) == 1:
            check = code_parser.parse_code_dict(args[0])
            if "error" in check:
                await ctx.send(":x: Invalid map list. Please try again.")
                return
            self.bot.db.execute_commit_query(db_strings.UPDATE_SETTING_MAPLIST, (args[0], ctx.guild.id))
            await ctx.send(":white_check_mark: Successfully updated the maplist:")
            await ctx.send("```" + code_parser.gen_maplist_str(check) + "```")
        else:
            await ctx.send(":x: Too many arguments. Type `l?settings` for a list of commands and their use cases. ")

    @settings.group(case_insensitive=True, invoke_without_command=True, aliases=["draft", "laucnhpoint"])
    async def season(self, ctx):
        await ctx.send(":x: You must provide an argument to stop the season or to start the season:\n"
                       "To pause the season, provide `pause`, `timeout`, `reopen`, or `open` to pause/continue the "
                       "season.\n "
                       "To start a new season, provide `start`, `init`, or `open` as an argument.\n"
                       "Type `l?settings` for a list of commands and their use cases.")

    @season.group(case_insensitive=True, invoke_without_command=True, aliases=["pause", "timeout", "reopen", "open"])
    async def toggle_season(self, ctx):
        self.bot.db.update_season_end(ctx.guild.id)
        season_status = self.bot.db.execute_query(db_strings.GET_SETTINGS, ctx.guild.id)
        season_status = season_status[0][5]  # if end time is 0, it reopened; otherwise it closed
        if season_status is 0:
            await ctx.send(":white_check_mark: Successfully reopened the season.")
        else:
            await ctx.send(":white_check_mark: Successfully paused the season.")

    @season.group(case_insensitive=True, invoke_without_command=True, aliases=["start", "init"])
    async def start_season(self, ctx):
        # sends warning message
        temp_message = await ctx.send(":warning: Are you sure you want to start the next season? "
                                      "You cannot go back to a previous season.\n\n"
                                      "To confirm your decision to **irreversibly** end the current season and start "
                                      "the next season, react `👍` to this message within the next 10 seconds.")
        await temp_message.add_reaction("👍")

        def check(reaction, user):
            # check used to make sure reaction is from the original author and with the correct reaction
            return user == ctx.author and str(reaction.emoji) == "👍"

        try:
            await self.bot.wait_for('reaction_add', timeout=10.0, check=check)  # wait for response

        except asyncio.TimeoutError:
            # If no response, cancel and exit
            await temp_message.edit(content="Operation canceled. Did not start a new season.")
            await temp_message.remove_reaction(emoji="👍", member=ctx.bot.user)
        else:
            # otherwise start new season
            self.bot.db.init_new_season(ctx.guild.id)

            # Sets confirmation/reminder for maplist, pings launchpoint about the new season
            await ctx.send(":white_check_mark: Successfully started new season. **Remember to update the maplist via "
                           "`s?settings maplist`!**")
            launchpoint_role = discord.utils.get(ctx.guild.roles, name="LaunchPoint")
            season_num = self.bot.db.execute_query(db_strings.GET_SETTINGS, ctx.guild.id)
            season_num = season_num[0][3]
            await ctx.guild.get_channel(config.launchpoint_announcement_id).send(launchpoint_role.mention + " Season " +
                                                                                 str(season_num) + " has started!")

    @commands.command()
    async def join(self, ctx):
        # TODO remove debug command
        guild_id = ctx.guild.id
        self.bot.db.execute_commit_query(db_strings.INSERT_SETTING, (guild_id, "", -1, 0, 0, 0))

    @commands.command(name="tent", aliases=["tenta"])
    async def best_weapon(self, ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/743901312718209154/791250962798215198/video0.mov")


def setup(bot):
    bot.add_cog(Staff(bot))
