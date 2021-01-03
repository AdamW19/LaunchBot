import discord
from discord.ext import commands

import config
from modules import embeds


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(case_insensitive=True, invoke_without_command=True, aliases=["commands"])
    async def help(self, ctx, *args):
        if len(args) == 0:
            help_embed = embeds.generate_base_help_embed(self.bot)
            help_embed.add_field(name=":question: **Help Categories**",
                                 value="To get help for the various parts of " + self.bot.user.name + ", "
                                       "use `l?help [page]` to view any of the pages listed below:\n\n"
                                       "1. Rotation Commands\n"
                                       "2. Draft Commands\n"
                                       "3. Misc. Commands\n"
                                       "4. Command Syntax Help\n\n"
                                       "You can also type `l?help full` "
                                       "if you would like the view the full contents of the help in a DM.",
                                 inline=False)
            embeds.add_help_embed_footer_links(help_embed, self.bot)
            await ctx.send(embed=help_embed)
        else:
            await ctx.send(":x: Sorry, that is not a valid help page. Type `l?help` to view the valid help pages.")

    @help.command(name="1", aliases=["Rotation", "Schedule"])
    async def lobby_commands(self, ctx):
        help_embed = embeds.generate_base_help_embed(self.bot)
        embeds.add_help_embed_field(help_embed, "rotation_commands")
        await ctx.send(embed=help_embed)

    @help.command(name="2", aliases=["Draft"])
    async def draft_commands(self, ctx):
        help_embed = embeds.generate_base_help_embed(self.bot)
        embeds.add_help_embed_field(help_embed, "draft_commands")
        await ctx.send(embed=help_embed)

    @help.command(name="3", aliases=["Misc"])
    async def misc_commands(self, ctx):
        help_embed = embeds.generate_base_help_embed(self.bot)
        embeds.add_help_embed_field(help_embed, "misc_commands")
        await ctx.send(embed=help_embed)

    @help.command(name="4", aliases=["Command"])
    async def command_syntax(self, ctx):
        help_embed = embeds.generate_base_help_embed(self.bot)
        embeds.add_help_embed_field(help_embed, "command_syntax")
        await ctx.send(embed=help_embed)

    @help.command()
    async def full(self, ctx):
        help_embed = embeds.generate_base_help_embed(self.bot)
        for key, field in embeds.help_embed_fields.items():
            help_embed.add_field(name=field["title"], value=field["body"], inline=False)
        embeds.add_help_embed_footer_links(help_embed, self.bot)
        await ctx.author.send(embed=help_embed)
        await ctx.send(":white_check_mark: " + ctx.author.mention +
                       ", the full help for " + self.bot.user.name + " has been DMed to you.")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong! Took {0} ms'.format(round(self.bot.latency * 1000, 0)))

    @commands.command()
    async def special_thanks(self, ctx):
        embed = discord.Embed(title="Special Thanks", color=config.embed_color)
        embed.add_field(name="Notice", value="We would like to thank [splatoon2.ink](https://splatoon2.ink/) for the "
                                             "rotation API. " + self.bot.user.name + " is written in Python 3 with "
                                             "[discord.py](https://discordpy.readthedocs.io/en/latest/) and "
                                             "SQLite. Player power levels uses "
                                             "[Trueskill™](http://research.microsoft.com/en-us/projects/trueskill/). "
                                             "Trueskill™ is a registered trademark of the Microsoft Corporation.\n"
                                             "All rights reserved.", inline=False)
        embed.add_field(name="Github Repo",
                        value="Visit the code for " + self.bot.user.name + " [here.](https://github.com/AdamW19"
                                                                           "/LaunchBot)", inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    # remove the default help command so the better one can be used
    bot.remove_command("help")
    bot.add_cog(Help(bot))
