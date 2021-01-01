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

    @commands.command()
    async def draft(self, ctx):
        pass

