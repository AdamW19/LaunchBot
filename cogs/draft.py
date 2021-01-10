import asyncio
import datetime
from datetime import datetime
import pytz
import random

import trueskill

import discord
from discord.ext import commands
from discord.ext.commands import Cog
from modules import code_parser, power_level
from db.src import db_strings


# TODO this whole thing needs more testing and general refactoring

SERVER_ID = 1234567890
LAUNCHPOINT_ROLE = 795214612576469022
LOBBY_SIZE = 2  # TODO change back to 8
LOBBY_THRESHOLD = int(LOBBY_SIZE / 2) + 1
EMOTE_NUM = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
NUM_CAPTAINS = 2
REDO_MAP_MODE_THRESHOLD = int(LOBBY_SIZE / 2)
BEST_OF = 1  # TODO change back to 7
BEST_OF_THRESHOLD = int(BEST_OF / 2) + 1

EMOTE_TO_INT = {
    "1️⃣": 1,
    "2️⃣": 2,
    "3️⃣": 3,
    "4️⃣": 4,
    "5️⃣": 5,
    "6️⃣": 6
}

REMAINING_STR = "Needs {} more player(s)"
TIME_REMAINING = "{} more minutes before draft closes."
GAME_STATUS = "Currently on game {}. You need to wait 180 seconds after the last change to report scores."  # TODO
SCORE_STR = "{}-{}"


class Draft(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self.trueskill_env = trueskill.TrueSkill(draw_probability=0)

    @commands.command(case_insensitive=True)
    @commands.has_role("LaunchPoint")
    async def draft(self, ctx):

        # Checks to make sure the server has an entry in the settings table and that the maplist is valid
        settings_db = self.db.execute_query(db_strings.GET_SETTINGS, ctx.guild.id)
        if len(settings_db) == 0:
            await ctx.send(":x: No maplist found. Please ask the developers or the staff for help.")
            return
        else:
            maplist = settings_db[0][1]
            parsed_maplist = code_parser.parse_code_dict(maplist)
            if "error" in parsed_maplist:
                await ctx.send(":x: Invalid maplist found. Please ask the developers or the staff for help.")
                return

            season_start = datetime.fromtimestamp(settings_db[0][5], tz=pytz.utc)
            season_end = datetime.fromtimestamp(settings_db[0][6], tz=pytz.utc)
            # checks to make sure the season hasn't ended
            if season_start > datetime.now(pytz.utc) and (
                    season_end <= datetime.now(pytz.utc) or settings_db[0][7] == 0):
                await ctx.send(":x: The current season has ended or is on pause.")
                return

        # Ping LaunchPoint members
        # msg = '{}'.format(LaunchPoint.mention)
        # await ctx.send('<@&795214612576469022>')

        captains = []
        players = []
        lobby_curation_time = datetime.now(pytz.utc)
        lobby_id = ctx.message.id

        # Embed for players to join draft
        embed = discord.Embed(title="Draft")
        embed.add_field(name="Captains", value=ctx.author.mention, inline=False)
        embed.add_field(name="Players", value="Empty", inline=False)
        embed.add_field(name="Status", value=REMAINING_STR.format(LOBBY_SIZE - 1) + " to start draft.", inline=False)
        embed.set_footer(text="Scrim ID: " + str(ctx.message.id))
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
                    if user not in captains and user not in players and \
                            (len(captains) is 0 or len(players) + len(captains) + 1 == LOBBY_SIZE):
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
                                                                            # TODO change value back to 15
                reaction, orig_captain = await self.bot.wait_for('reaction_add', timeout=5.0, check=captain_check)
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
                               and str(reaction_p) == "🖐"

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

        # Commence draft sequence, pick way to select players
        embed.set_field_at(index=0, name="Format 1: Alternate", value="Captain A Picks\n"
                                                                        "Captain B Picks\n"
                                                                        "Captain A Picks\n"
                                                                        "Captain B Picks, etc.")
        embed.set_field_at(index=1, name="Format 2: Snake", value="Captain A Picks\n"
                                                                        "Captain B Picks\n"
                                                                        "Captain B Picks\n"
                                                                        "Captain A Picks, etc.")

        embed.add_field(inline=False, name="Note", value="Both captains must react to the same draft format to proceed.\n"
                                                            "Failure to agree will reset reactions. After 60 seconds, "
                                                            "the bot will select a random draft format.")

        # Clear old reactions, add 1 and 2 reaction for draft style selection
        await message.clear_reactions()
        await message.edit(embed=embed)
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")

        # Move all players to a dictionary with corresponding emote
        players_remaining = {}
        for i in range(len(players)):
            players_remaining[EMOTE_NUM[i]] = players[i]

        # Lists for each team
        alpha = []
        bravo = []

        # Captains have 1 minute to agree, otherwise random
        reactions_not_match = True
        draft_mode_curation = datetime.now(pytz.utc)

        while reactions_not_match:
            async def start_draft_embed(captA, captB):
                alpha.append(captA)
                bravo.append(captB)

                embed.set_field_at(index=0, name="Alpha Team", value=captA.mention)
                embed.set_field_at(index=1, name="Bravo Team", value=captB.mention)
                embed.set_field_at(inline=False, index=2, name="Remaining Players",
                                   value=self.gen_players_remaining_str(players_remaining))
                embed.add_field(inline=False, name="Current Pick", value=captA.mention)
                await message.edit(embed=embed)
                await message.clear_reactions()
                await message.add_reaction("1️⃣")
                await message.add_reaction("2️⃣")
                await message.add_reaction("3️⃣")
                await message.add_reaction("4️⃣")
                await message.add_reaction("5️⃣")
                await message.add_reaction("6️⃣")

            #curr_captA = True

            def curr_captain_check(reaction_c, user_c, curr_captA):
                keys = players_remaining.keys()
                if type(reaction_c.emoji) is str and str(reaction_c) in keys:
                    if curr_captA:
                        return user_c.id == captA.id and user_c.id is not ctx.me.id
                    else:
                        return user_c.id == captB.id and user_c.id is not ctx.me.id
                return False

            # 2 functions for 2 different draft styles
            async def alternate_draft(captA, captB):
                await start_draft_embed(captA, captB)
                curr_captA = True
                for i in range(len(players)):
                    try:
                        reaction, capt = await self.bot.wait_for('reaction_add', timeout=20.0, check=lambda x, y: curr_captain_check(x, y, curr_captA))

                    except asyncio.TimeoutError:
                        num = random.randint(0, len(players_remaining))
                        keys = players_remaining.keys()
                        reaction = keys[num]

                    choosen_player = players_remaining.pop(str(reaction))
                    if curr_captA:
                        alpha.append(choosen_player)
                        embed.set_field_at(index=0, name="Alpha Team", value=self.gen_player_str(alpha))
                    else:
                        bravo.append(choosen_player)
                        embed.set_field_at(index=1, name="Bravo Team", value=self.gen_player_str(bravo))

                    curr_captA = not curr_captA

                    embed.set_field_at(inline=False, index=2, name="Remaining Players",
                                            value=self.gen_players_remaining_str(players_remaining))
                    embed.set_field_at(inline=False, index=3, name="Current Pick",
                                           value=captA.mention if curr_captA else captB.mention)

                    await message.edit(embed=embed)
                    await reaction.clear()

            async def snake_draft(captA, captB):
                await start_draft_embed(captA, captB)
                curr_captA = True
                for i in range(len(players)):
                    try:
                        reaction, capt = await self.bot.wait_for('reaction_add', timeout=20.0,
                                                                 check=lambda x, y: curr_captain_check(x, y,
                                                                                                       curr_captA))

                    except asyncio.TimeoutError:
                        num = random.randint(0, len(players_remaining))
                        keys = players_remaining.keys()
                        reaction = keys[num]

                    choosen_player = players_remaining.pop(str(reaction))
                    if curr_captA:
                        alpha.append(choosen_player)
                        embed.set_field_at(index=0, name="Alpha Team", value=self.gen_player_str(alpha))
                    else:
                        bravo.append(choosen_player)
                        embed.set_field_at(index=1, name="Bravo Team", value=self.gen_player_str(bravo))

                    if i == 0 or i == 2 or i == 4:
                        curr_captA = not curr_captA

                    embed.set_field_at(inline=False, index=2, name="Remaining Players",
                                       value=self.gen_players_remaining_str(players_remaining))
                    embed.set_field_at(inline=False, index=3, name="Current Pick",
                                       value=captA if curr_captA else captB)

                    await message.edit(embed=embed)
                    await reaction.clear()

            # Ask captains to agree on draft format
            try:
                def captain_check(reaction_c, user_c):  # has to be a captain, not the bot, and reacted properly
                    if type(reaction_c.emoji) is str and (str(reaction_c) == '1️⃣' or str(reaction_c) == '2️⃣'):
                        return user_c in captains and user_c.id is not ctx.me.id
                    return False

                # Time remaining calculations
                current_time = datetime.now(pytz.utc)
                delta = current_time - draft_mode_curation
                sec_left = 15.0 - delta.seconds

                reaction1, captA = await self.bot.wait_for('reaction_add', timeout=sec_left, check=captain_check)
                reaction2, captB = await self.bot.wait_for('reaction_add', timeout=sec_left, check=captain_check)

                if str(reaction1) == str(reaction2) and captA != captB:
                    if str(reaction1) == "1️⃣":
                        await alternate_draft(captA, captB)
                    elif str(reaction1) == "2️⃣":
                        await snake_draft(captA, captB)
                    reactions_not_match = False
                else:
                    if str(reaction1) == "1️⃣" and str(reaction2) == "2️⃣":
                        await reaction1.remove(captA)
                        await reaction2.remove(captB)
                    elif str(reaction2) == "1️⃣" and str(reaction1) == "2️⃣":
                        await reaction1.remove(captB)
                        await reaction2.remove(captA)
                    continue

            except asyncio.TimeoutError:
                random_mode = random.randint(1, 3)
                random_capt = random.randint(0, 2)
                if random_capt == 0: # Randomize Capt A and B
                    captA = captains[0]
                    captB = captains[1]
                else:
                    captA = captains[1]
                    captB = captains[0]
                if random_mode == 1: # Randomize Draft Format
                    await alternate_draft(captA, captB)
                else:
                    await snake_draft(captA, captB)
                reactions_not_match = False

            else:

                db_settings = self.db.execute_query(db_strings.GET_SETTINGS, ctx.guild.id)[0]

                alpha_team_id = int(db_settings[2])
                bravo_team_id = alpha_team_id + 1

                self.db.execute_commit_query(db_strings.UPDATE_LAST_SCRIM, ((bravo_team_id + 1), ctx.guild.id))

                for player in alpha:
                    self.db.execute_commit_query(db_strings.INSERT_TEAM, (alpha_team_id, player.id, 0, 0))
                for player in bravo:
                    self.db.execute_commit_query(db_strings.INSERT_TEAM, (bravo_team_id, player.id, 0, 0))

                # add captains into the team, set is_captain to true
                self.db.execute_commit_query(db_strings.INSERT_TEAM, (alpha_team_id, captA.id, 0, 1))
                self.db.execute_commit_query(db_strings.INSERT_TEAM, (alpha_team_id, captB.id, 0, 1))

                self.db.execute_commit_query(db_strings.INSERT_SCRIM, (ctx.message.id, alpha_team_id, bravo_team_id, 0, 0))

                # === Match start ===
                await message.clear_reactions()
                await self.match(ctx, alpha, bravo, captains, message, [alpha_team_id, bravo_team_id], lobby_id)

    async def match(self, ctx, alpha: list, bravo: list, captains: list, message, team_ids, lobby_id: int):
        maplist_str = self.db.execute_query(db_strings.GET_SETTINGS, ctx.guild.id)[0][1]
        mean_power_level = 0.0
        combined_team = alpha + bravo
        for player in combined_team:
            player_db = self.db.execute_query(db_strings.GET_PLAYER, player.id)
            if len(player_db) == 0:
                self.db.execute_commit_query(db_strings.INSERT_PLAYER, (player.id, None, None, 0, 0, 0, 0))
                player_power = 25.0  # default starting power level
            else:
                player_power = float(player_db[0][1])
            mean_power_level += player_power
        mean_power_level = round(mean_power_level / 8.0, 0)

        num_players_redo = 0
        total_num_games_played = 0
        total_map_refreshes = 0

        alpha_wins = 0
        bravo_wins = 0

        alpha_subs = []
        bravo_subs = []

        map_list = code_parser.parse_code_format(maplist_str)
        map_mode = map_list.pop(random.randint(0, len(map_list)))  # get random map-mode

        embed = self.gen_match_embed(alpha, bravo, map_mode, mean_power_level, alpha_wins, bravo_wins,
                                     GAME_STATUS.format(total_num_games_played + 1), lobby_id)

        await message.edit(embed=embed)

        await message.add_reaction('⛔')  # stop sign
        await message.add_reaction('\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}')  # redo icon

        while alpha_wins != BEST_OF_THRESHOLD and bravo_wins != BEST_OF_THRESHOLD:
            update_embed = False
            try:
                def set_check(reaction_s, user_s):  # has to be a player/captain and not the bot
                    return (user_s in alpha or user_s in bravo or user_s in captains) and user_s.id is not ctx.me.id
                                                                    # TODO CHANGE THIS NUMBER
                reaction, player = await self.bot.wait_for('reaction_add', timeout=10.0, check=set_check)

                if str(reaction) == "⛔":
                    await message.clear_reactions()
                    embed.set_field_at(index=4, name="Status", value="Need a sub, feel free to ping again.. "
                                                                     "If you want to sub, react with `🖐`.\n"
                                                         "Lobby will auto-close in 10 minutes if a sub could not "
                                                         "be found.")
                    await message.add_reaction("🖐")
                    await message.edit(embed=embed)

                    try:
                        def sub_check(reaction_sub, user_sub):  # has to be a player not in the lobby, not the bot,
                                                                # and reacted
                            return user_sub not in alpha and user_sub not in bravo and \
                                   user_sub.id is not ctx.me.id and str(reaction_sub) == "🖐"

                        # wait for a sub to react
                        reaction, sub = await self.bot.wait_for('reaction_add', timeout=(60.0 * 10), check=sub_check)

                        # clear fields and reactions
                        embed.clear_fields()
                        await message.clear_reactions()

                        # remove old player
                        if player in alpha:
                            if player in captains:  # remove captain status in the db
                                captains.remove(player)
                                self.db.execute_commit_query(db_strings.UPDATE_TEAM_CAPTAIN, (0, team_ids[0], player.id))
                            alpha.remove(player)
                            alpha_subs.append(player)
                            alpha.append(sub)
                            alpha_subs.append(sub)
                            self.db.execute_commit_query(db_strings.UPDATE_TEAM_SUB, (1, team_ids[0], player.id))
                            self.db.execute_commit_query(db_strings.INSERT_TEAM, (team_ids[0], sub.id, 1, 0))

                            if len(captains) != NUM_CAPTAINS:
                                if len(alpha) > 1:
                                    captains.append(alpha[random.randint(0, len(alpha) - 1)])
                                else:
                                    captains.append(sub)
                        elif player in bravo:
                            if player in captains:
                                captains.remove(player)
                                self.db.execute_commit_query(db_strings.UPDATE_TEAM_CAPTAIN, (0, team_ids[1], player.id))
                            bravo.remove(player)
                            bravo_subs.append(player)
                            bravo.append(sub)
                            bravo_subs.append(sub)
                            self.db.execute_commit_query(db_strings.UPDATE_TEAM_SUB, (1, team_ids[1], player.id))
                            self.db.execute_commit_query(db_strings.INSERT_TEAM, (team_ids[1], sub.id, 1, 0))

                            if len(captains) != NUM_CAPTAINS:
                                if len(bravo) > 1:
                                    captains.append(bravo[random.randint(0, len(bravo) - 1)])
                                else:
                                    captains.append(sub)

                        mean_power_level = 0.0
                        for player in combined_team:
                            player_power = self.db.execute_query(db_strings.GET_PLAYER, player.id)[0][1]
                            mean_power_level += player_power
                        mean_power_level = round(mean_power_level / 8.0, 0)

                        embed.add_field(name="Status", value="Thank you for subbing {}! If the captain left, "
                                                             "I randomly choose someone in the team to be the "
                                                             "captain.\n"
                                                             "Returning to the set...".format(sub.mention),
                                           inline=False)
                        await message.clear_reactions()
                        await message.edit(embed=embed)

                        with ctx.channel.typing():
                            await asyncio.sleep(5)

                        update_embed = True

                    except asyncio.TimeoutError:
                        embed.clear_fields()
                        await message.edit(content="Could not find a sub in time. Closing lobby.", embed=None)

                        if total_num_games_played > 0:
                            await message.clear_reactions()
                            final_embed = self.send_final_score(alpha, bravo, alpha_subs, bravo_subs,
                                                                [alpha_wins, bravo_wins], None, ctx.message.id)
                            await message.edit(embed=final_embed)
                            return

                elif str(reaction) == "🔄" and total_map_refreshes < 2:
                    num_players_redo += 1
                    status_str = GAME_STATUS.format(total_num_games_played + 1) + " We need {} more people to reroll the " \
                                                                              "stage-mode.".format(str(
                                                                            REDO_MAP_MODE_THRESHOLD - num_players_redo))
                    embed.set_field_at(index=4, name="Status", value=status_str, inline=False)

                    if REDO_MAP_MODE_THRESHOLD - num_players_redo == 0:  # if we met the threshold do a reset
                        num_players_redo = 0
                        total_map_refreshes += 1
                        status_str = GAME_STATUS.format(total_num_games_played + 1) + \
                                     " Rerolled map-mode. You have {} more rerolls.".format(2 - total_map_refreshes)

                        await message.clear_reactions()
                        await message.add_reaction('⛔')  # stop sign
                        await message.add_reaction('\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}')

                        map_mode = map_list.pop(random.randint(0, len(map_list)))  # get random map-mode
                        # map_mode_list = map_mode.split("-")
                        # map_file = FILE_PREFIX + map_mode_list[1].replace(" ", "-") + ".png"
                        embed.set_field_at(index=2, name="Mode + Stage", value=map_mode, inline=False)
                        embed.set_field_at(index=4, name="Status", value=status_str, inline=False)

                        # file = discord.File(map_file, filename="map.png")
                        # embed.set_image(url="attachment://map.png")

                        await message.edit(embed=embed)
                        continue
            except asyncio.TimeoutError:
                embed = discord.Embed(title="Draft")
                embed.set_footer(text="Scrim ID: " + str(ctx.message.id))

                embed.add_field(name="Alpha Team", value=self.gen_player_str(alpha))
                embed.add_field(name="Beta Team", value=self.gen_player_str(bravo))

                embed.add_field(name="Mode + Stage", value=map_mode, inline=False)

                await message.clear_reactions()

                num_captains_agree = [0, 0]  # index 0 is alpha, index 1 is bravo
                num_players_agree = [0, 0]

                embed.add_field(name="Winner?", value="Who won the {} game?".format(map_mode) +
                                                      "\n\n `🇦` for Alpha team, `🇧` for Beta team.")
                embed.add_field(name="Status", value="Both captains must agree, or a majority of the lobby must agree.")

                await message.edit(file=None, embed=embed)

                await message.add_reaction("🇦")
                await message.add_reaction("🇧")

                try:
                    def match_check(reaction_match, user_match):  # has to be a player in the lobby and not the bot
                        return (user_match in alpha or user_match in bravo or user_match in captains) and \
                               user_match.id is not ctx.me.id

                    while num_players_agree[0] < LOBBY_THRESHOLD and num_players_agree[1] < LOBBY_THRESHOLD and \
                        num_captains_agree[0] < len(captains) and num_captains_agree[1] < len(captains):
                        reaction, lobby_player = await self.bot.wait_for('reaction_add', timeout=(60.0 * 60 * 10),
                                                                         check=match_check)

                        if str(reaction) == "🇦":
                            if lobby_player in captains:
                                num_captains_agree[0] += 1
                            num_players_agree[0] += 1
                        elif str(reaction) == "🇧":
                            if lobby_player in captains:
                                num_captains_agree[1] += 1
                            num_players_agree[1] += 1

                    if num_captains_agree[0] == len(captains) or num_players_agree[0] >= LOBBY_THRESHOLD:
                        alpha_wins += 1
                        result = power_level.Result.ALPHA_WIN
                    elif num_captains_agree[1] == len(captains) or num_players_agree[1] >= LOBBY_THRESHOLD:
                        bravo_wins += 1
                        result = power_level.Result.BETA_WIN
                    else:
                        result = None

                    self.db.execute_commit_query(db_strings.UPDATE_SCRIM_SCORE, (alpha_wins, bravo_wins,
                                                                                 ctx.message.id))
                    total_num_games_played += 1
                    # arrays of player objects for new power ratings
                    alpha_team_pow = []
                    bravo_team_pow = []

                    for player in combined_team:
                        # generates Player object for power calculations
                        player_db = self.db.execute_query(db_strings.GET_PLAYER, player.id)[0]
                        pow_player = power_level.Player(self.trueskill_env, player.id, player_db[1], player_db[2])

                        # Saves result of the game into the db
                        game_wins = player_db[3]
                        game_losses = player_db[4]

                        if player in alpha:

                            alpha_team_pow.append(pow_player)
                            if result is power_level.Result.ALPHA_WIN:
                                game_wins += 1
                            else:
                                game_losses += 1
                            self.db.execute_commit_query(db_strings.UPDATE_PLAYER_GAME_STAT,
                                                         (game_wins, game_losses, player.id))

                        else:
                            bravo_team_pow.append(pow_player)

                            if result is power_level.Result.BETA_WIN:
                                game_wins += 1
                            else:
                                game_losses += 1
                            self.db.execute_commit_query(db_strings.UPDATE_PLAYER_GAME_STAT,
                                                         (game_wins, game_losses, player.id))

                    alpha_team = power_level.Team(alpha_team_pow, None)
                    bravo_team = power_level.Team(bravo_team_pow, None)

                    power_level.calc_new_rating(self.trueskill_env, alpha_team, bravo_team, result)

                    # saves new power level for each player
                    for player in (alpha_team_pow + bravo_team_pow):
                        player_id = player.player_id
                        self.db.execute_commit_query(db_strings.UPDATE_PLAYER_RANK,
                                                     (player.rating.mu, player.rating.sigma, player_id))

                    if alpha_wins != BEST_OF_THRESHOLD and bravo_wins != BEST_OF_THRESHOLD:
                        update_embed = True

                except asyncio.TimeoutError:
                    return  # TODO some error about not choosing a team on time, this shouldn't happen but

            if update_embed:
                map_mode = map_list.pop(random.randint(0, len(map_list)))  # get random map-mode
                embed = self.gen_match_embed(alpha, bravo, map_mode, mean_power_level, alpha_wins, bravo_wins,
                                             GAME_STATUS.format(total_num_games_played + 1), lobby_id)
                await message.clear_reactions()
                await message.add_reaction('⛔')  # stop sign
                await message.add_reaction('\N{ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS}')

            await message.edit(embed=embed)

        if alpha_wins == BEST_OF_THRESHOLD:
            set_endresult = power_level.Result.ALPHA_WIN
        else:
            set_endresult = power_level.Result.BETA_WIN

        for player in combined_team:
            player_db = self.db.execute_query(db_strings.GET_PLAYER, player.id)[0]

            set_wins = player_db[5]
            set_losses = player_db[6]
            if player in alpha:
                team_player_db = self.db.execute_query(db_strings.GET_TEAM_PLAYER, (team_ids[0], player.id))[0]
                if not bool(team_player_db[2]):
                    if set_endresult is power_level.Result.ALPHA_WIN:
                        set_wins += 1
                    else:
                        set_losses += 1
                    self.db.execute_commit_query(db_strings.UPDATE_PLAYER_SET_STAT,
                                                 (set_wins, set_losses, player.id))
            else:
                team_player_db = self.db.execute_query(db_strings.GET_TEAM_PLAYER, (team_ids[1], player.id))[0]
                if not bool(team_player_db[2]):
                    if set_endresult is power_level.Result.BETA_WIN:
                        set_wins += 1
                    else:
                        set_losses += 1
                    self.db.execute_commit_query(db_strings.UPDATE_PLAYER_SET_STAT,
                                                 (set_wins, set_losses, player.id))

        await message.clear_reactions()
        final_embed = self.send_final_score(alpha, bravo, alpha_subs, bravo_subs, [alpha_wins, bravo_wins],
                                            set_endresult, ctx.message.id)
        await message.edit(embed=final_embed)

    def send_final_score(self, alpha: list, bravo: list, alpha_subs: list, bravo_subs: list, result: list,
                         winner: power_level.Result, scrim_id: int):
        alpha_str = self.gen_player_str(alpha)
        if len(alpha_subs) == 0:
            alpha_str += "\n *No Subs*"
        else:
            alpha_str += "\nSubs:\n"
            alpha_str += self.gen_player_str(alpha_subs)

        bravo_str = self.gen_player_str(bravo)
        if len(bravo_subs) == 0:
            bravo_str += "\n *No Subs*"
        else:
            bravo_str += "\nSubs:\n"
            bravo_str += self.gen_player_str(bravo_subs)

        embed = discord.Embed(title="Draft result")
        embed.add_field(name="Alpha Team", value=alpha_str)
        embed.add_field(name="Bravo Team", value=bravo_str)

        if winner is power_level.Result.ALPHA_WIN:
            winner_str = "Alpha team won!"
        elif winner is power_level.Result.BETA_WIN:
            winner_str = "Beta team won!"
        else:
            winner_str = "Did not finish."

        embed.add_field(name="Result", value=SCORE_STR.format(result[0], result[1]) + "\n" + winner_str, inline=False)
        embed.set_footer(text="Scrim ID: " + str(scrim_id))

        return embed

    def gen_match_embed(self, alpha: list, bravo: list, map_mode: str, mean_power_level: float, alpha_wins: int,
                        bravo_wins: int, status_str: str, lobby_id: int):
        embed = discord.Embed(title="Draft")
        embed.add_field(name="Alpha Team", value=self.gen_player_str(alpha))
        embed.add_field(name="Beta Team", value=self.gen_player_str(bravo))

        embed.add_field(name="Mode + Stage", value=map_mode, inline=False)
        embed.add_field(name="Average Power Level", value=str(mean_power_level), inline=False)

        embed.add_field(name="Status", value=status_str)
        embed.add_field(name="Score", value=SCORE_STR.format(alpha_wins, bravo_wins))
        embed.set_footer(text="Scrim ID: " + str(lobby_id))

        return embed

    @staticmethod
    def gen_player_str(players: list):
        player_str = ""
        for player in players:
            player_str += player.mention + "\n"
        return player_str

    @staticmethod
    def gen_players_remaining_str(players_remaining: dict):
        player_str = ""
        if len(players_remaining) == 0:
            return "None"
        for emote, player in players_remaining.items():
            player_str += player.mention + " " + emote + "\n"
        return player_str

    @staticmethod
    def player_remaining(players: list, cutoff: int):
        num_players = len(players)
        return cutoff - num_players


def setup(bot):
    bot.add_cog(Draft(bot))
