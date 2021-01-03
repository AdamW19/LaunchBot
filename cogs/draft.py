from enum import Enum, auto

import config
import discord
from discord.ext import commands
from discord.ext.commands import Cog


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
        # Ping Launchpoint members
        await ctx.send("@LaunchPoint")

        # Embed for players to join draft
        embed=discord.Embed(title="Draft")
        embed.add_field(name="Captains", value=ctx.author, inline=False)
        embed.add_field(name="Players", value="Waiting on more players.", inline=False)
        embed.set_footer(text="Scrim ID: " + ctx.message.created_at)
        await ctx.send(embed=embed)

        # LaunchPoint (react to join draft) and Stop (react to exit draft)
        message.react('\:LaunchPoint').then(r => {
                            message.react('\:stop_sign');
                    });

        # Open Embed until 8 players join or 30 minutes pass
        list_captains = []
        list_players = []
        list_all_players = []
        list_captains.append(ctx.author)
        list_all_players.append(ctx.author)
        isEight = False
        while not isEight:
            try:
                reaction, user = await client.wait_for('reaction_add', timeout=1800.0, check=check)
                role = discord.utils.find(lambda r: r.name == 'LaunchPoint', ctx.message.server.roles)
                if reaction == '\:LaunchPoint' and role in user.roles:
                    list_all_players.append(user)
                    if len(list_players) == 8:
                        list_captains.append(user)
                        isEight = True
                        embed.set_field_at(0, *, "Captains", list_captains)
                    else:
                        list_players.append(user)
                        embed.set_field_at(1, *, "Players", list_players)
                elif reaction == '\:stop_sign' and role in user.roles:
                    list_all_players.remove(user)
                    if user in list_players:
                        embed.set_field_at(1, *, "Players", list_players)
                    elif user in list_captains:
                        embed.set_field_at(0, *, "Captains", list_captains)
                    await reaction.remove(user)

            except asyncio.TimeoutError:
                await ctx.send("Draft Closed - Not enough players")
                isEight = True
