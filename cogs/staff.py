import config
import discord
from discord.ext import commands
from discord.ext.commands import Cog


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
                                                                                           "and `settings`.")
        embed.add_field(name="Map pool", value="The subcommand for mappool is `map-pool`, `map`, or `pool`. If you "
                                               "don't provide a valid [nkitten.net]("
                                               "http://nkitten.net/splatoon2/random/) code as an argument, "
                                               "the bot will print out the current map pool. Otherwise, it will update "
                                               "the current map pool according to the given code.", inline=False)
        embed.add_field(name="Season", value="The subcommand for season is `draft` and `launchpoint`.\n "
                                             "You can provide `stop`, `end`, or `close` as an argument to end the "
                                             "season.\n "
                                             "You can also provide `pause` or `timeout` as an argument to temporarily "
                                             "close or to reopen the season.\n "
                                             "You can also provide `start`. `init`, or `open` as an argument to start "
                                             "a season.", inline=False)
        embed.add_field(name="Eggs", value="Type `l?tenta` or `l?tent` for the best weapon", inline=False)

        embed.set_footer(text="Remember, you must have the Staff role to run these commands. ")

        await ctx.send(embed=embed)

    @settings.group(case_insensitive=True, invoke_without_command=True, aliases=["map-pool", "map", "pool"])
    async def mappool(self, ctx, *args):
        if len(args) == 0:
            await ctx.send("TBD")  # TODO print out map list
        elif len(args) == 1:
            await ctx.send("TBD")  # TODO update and print out new map list
        else:
            await ctx.send(":x: Too many arguments. Type `l?settings` for a list of commands and their use cases. ")

    @settings.group(case_insensitive=True, invoke_without_command=True, aliases=["draft", "laucnhpoint"])
    async def season(self, ctx):
        await ctx.send(":x: You must provide an argument to stop the season or to start the season:\n"
                       "To stop the season, provide `stop`, `end`, or `close` as an argument.\n"
                       "To pause the season, provide `pause` or `timeout` to pause/continue the season.\n"
                       "To start the season, provide `start`, `init`, or `open` as an argument.\n"
                       "Type `l?settings` for a list of commands and their use cases.")

    @season.group(case_insensitive=True, invoke_without_command=True, aliases=["stop", "end", "close"])
    async def stop_season(self, ctx):
        await ctx.send("TBD")  # TODO: Edit Settings table and put now in `season_end`

    @season.group(case_insensitive=True, invoke_without_command=True, aliases=["pause", "timeout"])
    async def pause_season(self, ctx):
        await ctx.send("TBD")  # TODO if `season_end` has something remove it, otherwise put now in `season_end`

    @season.group(case_insensitive=True, invoke_without_command=True, aliases=["start", "init", "open"])
    async def start_season(self, ctx):
        await ctx.send("TBD")
        # TODO: Make a new db, copy over Players table from other season and put now in `start_season`
        # TODO: Also may want to make an announcement in some channel? ping @/Launchpoint?

    @commands.command(name="tent", aliases=["tenta"])
    async def best_weapon(self, ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/743901312718209154/791250962798215198/video0.mov")


def setup(bot):
    bot.add_cog(Staff(bot))
