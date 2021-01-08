import asyncio
import datetime
from datetime import datetime
from enum import Enum, auto
import pytz

import config
import discord
from discord.ext import commands
from discord.ext.commands import Cog

# from discord import Guild

LAUNCHPOINT_ROLE = 795214612576469022
LOBBY_SIZE = 1

REMAINING_STR = "Needs {} more player(s)"
TIME_REMAINING = "{} more minutes before draft closes."


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
        # msg = '{}'.format(LaunchPoint.mention)
        # await ctx.send('<@&795214612576469022>')

        captains = []
        players = []
        lobby_curation_time = datetime.now(pytz.utc)

        # Embed for players to join draft
        embed = discord.Embed(title="Draft")
        embed.add_field(name="Captains", value=ctx.author.mention, inline=False)
        embed.add_field(name="Players", value="Empty", inline=False)
        embed.add_field(name="Status", value=REMAINING_STR.format(LOBBY_SIZE - 1) + " to start draft.", inline=False)
        embed.set_footer(text="Scrim ID: " + str(int(lobby_curation_time.timestamp())))
        message = await ctx.send(embed=embed)

        # LaunchPoint (react to join draft) and Stop (react to exit draft)
        launchEmoji = '<:LaunchPoint:791152168429813800>'
        stopEmoji = '🛑'
        await message.add_reaction(launchEmoji)
        await message.add_reaction(stopEmoji)

        captains.append(ctx.author)

        # async def on_reaction_add(self, reaction, user):
        # Open Embed until 8 players join or 30 minutes pass
        while len(players) + len(captains) is not LOBBY_SIZE:
            try:
                def player_check(reaction, user):
                    # checks to make sure reaction isn't a self reaction, to make sure user has launchpoint role,
                    # and user isn't already in the lobby
                    if user.id is not ctx.me.id:
                        role = discord.utils.find(lambda r: r.name == "LaunchPoint", ctx.guild.roles)
                        return role in user.roles
                    return False

                current_time = datetime.now(pytz.utc)
                delta = current_time - lobby_curation_time
                sec_left = (60 * 30) - delta.seconds

                if delta.days < 0:
                    sec_left = 0

                reaction, user = await self.bot.wait_for('reaction_add', timeout=sec_left, check=player_check)

                player_str = ""
                captain_str = ""
                status_str = ""
                num_players_required = 0

                # role = discord.utils.find(lambda r: r.name == 'Member', ctx.message.server.roles)
                if str(reaction) == launchEmoji:
                    if len(captains) is 0 or len(players) is LOBBY_SIZE:
                        captains.append(user)
                    elif user not in players and user not in captains:
                        players.append(user)
                elif str(reaction) == stopEmoji:
                    if user in players and user not in captains:
                        players.remove(user)
                    if user in captains:
                        captains.remove(user)
                        if len(players) > 0:
                            captains.append(players[0])
                            status_str = "Made " + players[0].mention + " captain.\n"
                            players.remove(players[0])
                    await reaction.remove(user)

                if len(captains) is 0:
                    player_str = "Empty"
                    captain_str = "Empty"
                    status_str = "First one to react becomes the captain.\n"
                    num_players_required = LOBBY_SIZE
                elif len(players) is 0:
                    player_str = "Empty"
                    captain_str = self.gen_player_str(captains)
                    num_players_required = self.player_remaining(captains, LOBBY_SIZE)
                else:
                    player_str = self.gen_player_str(players)
                    captain_str = self.gen_player_str(captains)
                    num_players_required = self.player_remaining(players, LOBBY_SIZE) - len(captains)

                status_str += REMAINING_STR.format(num_players_required) + " to start draft.\n"
                status_str += TIME_REMAINING.format(round(sec_left / 60, 0)) + "\n"

                embed.set_field_at(index=0, name="Captains", value=captain_str, inline=False)
                embed.set_field_at(index=1, name="Players", value=player_str, inline=False)
                embed.set_field_at(index=2, name="Status", value=status_str, inline=False)

                await message.edit(embed=embed)

            except asyncio.TimeoutError:
                await message.edit(content="Draft Closed - Not enough players", embed=None)
                await message.clear_reactions()
                return

        # === Starting captain confirmation ===
        await message.clear_reactions()

        for i in range(3, 0, -1):  # so we only change captains at most 3 times
            embed.clear_fields()
            embed.add_field(name="Captains", value=self.gen_player_str(captains), inline=False)
            embed.add_field(name="Captain Verification", value="Captains, react with `⛔️` within the next 15 "
                                                               "seconds if you do not want to be the captain.\n"
                                                               "You can switch captains {} more time(s).".format(i),
                            inline=False)
            await message.add_reaction("⛔")
            await message.edit(embed=embed)

            try:
                def captain_check(reaction_c, user_c):  # has to be a captain, not the bot, and reacted properly
                    if type(reaction_c.emoji) is str and str(reaction_c) == '⛔':
                        return user_c in captains and user_c.id is not ctx.me.id
                    return False

                reaction, orig_captain = await self.bot.wait_for('reaction_add', timeout=15.0, check=captain_check)
                embed.set_field_at(index=0, name="Captains", value=self.gen_player_str(captains), inline=False)
                embed.set_field_at(index=1, name="Captain?", value="Would anyone like to be the captain? React with "
                                                                   "`🖐` to be the captain within the next 15 "
                                                                   "seconds.")
                await message.clear_reactions()
                await message.add_reaction("🖐")
                await message.edit(embed=embed)

                try:
                    def player_check(reaction_p, user_p):  # has to be a player, not already a captain, not the bot,
                                                           # and raised their hand
                        return user_p in players and user_p not in captains and user_p.id is not ctx.me.id \
                               and str(reaction_p) is "🖐"

                    reaction, new_captain = await self.bot.wait_for('reaction_add', timeout=15.0, check=player_check)

                    # remove old captain and add them as a player, vice verse for new captain
                    captains.remove(orig_captain)
                    players.append(orig_captain)
                    captains.append(new_captain)
                    players.remove(new_captain)
                    embed.set_field_at(index=0, name="Captains", value=self.gen_player_str(captains), inline=False)
                    embed.set_field_at(index=1, name="Captain?", value=new_captain.mention + ", you are the new " +
                                                                       "captain. Restarting captain confirmation...")
                    await message.clear_reactions()
                    await message.edit(embed=embed)

                    with ctx.channel.typing():  # adds a pretty "typing" thing as a loading screen
                        await asyncio.sleep(5)

                except asyncio.TimeoutError:
                    # if no one volunteers, send error that they will still be the captain
                    embed.set_field_at(index=0, name="Captains", value=self.gen_player_str(captains), inline=False)
                    embed.set_field_at(index=1, name="Failed to find new captain", value=orig_captain.mention + ", "
                                                                                         "we could not find your " +
                                                                                         "replacement, so you will "
                                                                                         "continue to be the captain.\n"
                                                                                         "Restarting captain "
                                                                                         "confirmation...")
                    await message.clear_reactions()
                    await message.edit(embed=embed)

                    with ctx.channel.typing():
                        await asyncio.sleep(5)

            except asyncio.TimeoutError:
                break  # if no captain rejects, continue on

        # === Choosing how to choose teams ===
        await message.clear_reactions()
        await ctx.send("successful")

    @staticmethod
    def gen_player_str(players: list):
        player_str = ""
        for player in players:
            player_str += player.mention + "\n"
        return player_str

    @staticmethod
    def player_remaining(players: list, cutoff: int):
        num_players = len(players)
        return cutoff - num_players


def setup(bot):
    bot.add_cog(Draft(bot))
