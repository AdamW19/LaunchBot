import asyncio
from enum import Enum, auto

import config
import discord
from discord.ext import commands
from discord.ext.commands import Cog
# from discord import Guild


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
        self.list_captains = []
        self.list_players = []
        self.list_all_players = []

    @commands.command(case_insensitive=True)
    @commands.has_role("LaunchPoint")

    async def draft(self, ctx):
        # Ping LaunchPoint members
        #msg = '{}'.format(LaunchPoint.mention)
        #await ctx.send('<@&795214612576469022>')

        self.list_captains = []
        self.list_players = []
        self.list_all_players = []

        # Embed for players to join draft
        embed = discord.Embed(title="Draft")
        embed.add_field(name="Captains", value=ctx.author, inline=False)
        embed.add_field(name="Players", value="Waiting on more players.", inline=False)
        embed.set_footer(text="Scrim ID: " + str(ctx.message.created_at))
        message = await ctx.send(embed=embed)

        # LaunchPoint (react to join draft) and Stop (react to exit draft)
        launchEmoji = '<:LaunchPoint:791152168429813800>'
        stopEmoji = '🛑'
        await message.add_reaction(launchEmoji)
        await message.add_reaction(stopEmoji)

        self.list_captains.append(ctx.author)
        self.list_all_players.append(ctx.author)

    #async def on_reaction_add(self, reaction, user):
        # Open Embed until 8 players join or 30 minutes pass
        isEight = False
        while not isEight:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=1800.0) #check=check)
                role = 795214612576469022
                #role = discord.utils.find(lambda r: r.name == 'Member', ctx.message.server.roles)
                if reaction == launchEmoji: #role in user.roles and
                    await ctx.send('Here!')
                    self.list_all_players.append(user.name)
                    if len(self.list_players) == 8:
                        self.list_captains.append(user.name)
                        isEight = True
                        captains = ""
                        for i in range(len(self.list_captains)):
                            captains = self.list_captains[i] + "\n" + captains
                        embed.set_field_at(0, "Captains", captains)
                    else:
                        players = ""
                        for i in range(len(self.list_players)):
                            players = self.list_players[i] + "\n" + players
                        self.list_players.append(user.name)
                        embed.set_field_at(1, "Players", players)
                    await message.edit(embed=embed)
                elif reaction == stopEmoji: #and role in user.roles:
                    self.list_all_players.remove(user.name)
                    if user.name in self.list_players:
                        self.list_players.remove(user.name)
                        players = ""
                        for i in range(len(self.list_players)):
                            players = self.list_players[i] + "\n" + players
                        embed.set_field_at(1, "Players", players)
                    elif user.name in self.list_captains:
                        self.list_captains.remove(user.name)
                        captains = ""
                        for i in range(len(self.list_captains)):
                            captains = self.list_captains[i] + "\n" + captains
                        embed.set_field_at(0, "Captains", captains)
                    #await reaction.remove(user)

                    await message.edit(embed=embed)

            except asyncio.TimeoutError:
                await ctx.send("Draft Closed - Not enough players")
                isEight = True

def setup(bot):
    bot.add_cog(Draft(bot))