import asyncio
from enum import Enum, auto

import config
import discord
from discord.ext import commands
from discord.ext.commands import Cog
# from discord import Guild

LAUNCHPOINT_ROLE = 795214612576469022
LOBBY_SIZE = 8


class Status(Enum):
    RECRUIT = auto()
    CAPTAIN_CHOOSING = auto()
    TEAM_CHOOSING = auto()
    MATCH_PLAYING = auto()
    SET_RESULT = auto()


class Draft(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None

    @commands.command(case_insensitive=True)
    @commands.has_role("LaunchPoint")

    async def draft(self, ctx):
        # Ping LaunchPoint members
        #msg = '{}'.format(LaunchPoint.mention)
        #await ctx.send('<@&795214612576469022>')

        captains = []
        players = []

        # Embed for players to join draft
        embed = discord.Embed(title="Draft")
        embed.add_field(name="Captains", value=ctx.author.mention, inline=False)
        embed.add_field(name="Players", value="Waiting on more players.", inline=False)
        embed.set_footer(text="Scrim ID: " + str(ctx.message.created_at))
        message = await ctx.send(embed=embed)

        # LaunchPoint (react to join draft) and Stop (react to exit draft)
        launchEmoji = '<:LaunchPoint:791152168429813800>'
        stopEmoji = '🛑'
        await message.add_reaction(launchEmoji)
        await message.add_reaction(stopEmoji)

        captains.append(ctx.author)
        players.append(ctx.author)

    #async def on_reaction_add(self, reaction, user):
        # Open Embed until 8 players join or 30 minutes pass
        while len(players) is not LOBBY_SIZE:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=1800.0) #check=check)

                if user.id == ctx.me.id:  # skipping our own reactions
                    continue

                #role = discord.utils.find(lambda r: r.name == 'Member', ctx.message.server.roles)
                if str(reaction) == launchEmoji: #role in user.roles and
                    players.append(user.mention)
                    if len(players) is LOBBY_SIZE:
                        captains.append(user.mention)
                elif str(reaction) == stopEmoji: #and role in user.roles:
                    players.remove(user.mention)

                player_str = self.gen_player_str(players)
                captain_str = self.gen_player_str(captains)

                embed.set_field_at(index=0, name="Captains", value=captain_str)
                embed.set_field_at(index=1, name="Players", value=player_str)

                await message.edit(embed=embed)

            except asyncio.TimeoutError:
                await message.edit("Draft Closed - Not enough players")
                return

    @staticmethod
    def gen_player_str(players: list):
        player_str = ""
        for player in players:
            player_str += player + "\n"
        return player_str


def setup(bot):
    bot.add_cog(Draft(bot))