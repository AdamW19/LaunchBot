import discord
import aiohttp
import traceback
from discord.ext import commands
import os
import asyncio
import config
from modules import checks
import glob
from db.cogs.splat_db import SplatoonDB
from db.cogs.database import DB_FILE_BASE

print("[LPBot] Initializing...")

EXTENSIONS = ["cogs.logs", "cogs.rotation", "cogs.help"]


def get_db_file():
    # Gets the most recently used db file from the db folder
    list_of_files = glob.glob(DB_FILE_BASE + "*.db")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


class LPBot(commands.Bot):
    def __init__(self, extensions):
        checks.make_sure_file_exists("config.py", "config_public.py")

        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        intents.reactions = True

        super().__init__(command_prefix=config.prefix, description=config.description, case_insensitive=True,
                         intents=intents)
        self.session = None
        self.db = SplatoonDB(file_name=get_db_file())

        for e in extensions:
            self.load_extension(e)

        self.loop.create_task(self.garbage_collector())

    # Below 2 methods properly close the session once the bot's killed
    def __del__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.close())

    async def close(self):
        if self.session is not None:
            await self.session.close()

    async def garbage_collector(self):
        """Removes all .gif and .png files from gif generation for lobby/rotation info"""
        await self.wait_until_ready()
        while not self.is_closed():
            print("[LPBot] Deleting old files...")
            for f in os.listdir():
                if f.endswith(".gif") or f.endswith(".png"):
                    os.remove(f)
            print("[LPBot] Deleted all old files")
            await asyncio.sleep(300)  # removes every 5 min/300 sec

    async def on_ready(self):
        print("[LPBot] Connected")
        self.session = aiohttp.ClientSession(headers=config.header)
        await self.get_channel(config.online_logger_id).send("*Connected to Discord*")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                             name="wahoo zones | l?help"))

    async def on_command(self, ctx):
        if ctx.guild is None:
            await self.get_channel(config.online_logger_id).send( "Command received from `" + ctx.author.name + "`: " +
                                                                  ctx.message.content)
        else:
            await self.get_channel(config.online_logger_id).send("Command received from `" + ctx.author.name + "` on `"
                                                                 + ctx.guild.name + "`: " + ctx.message.content)

    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.Forbidden) or "missing permissions" in str(error).lower():
            await ctx.send(":x: I do not have permission to send embedded messages in this channel and/or server!  "
                           "Make sure I have the permission `Embed Links`, or I can't function!")
            await self.get_channel(config.online_logger_id).send(":information_source: A handled error occurred "
                                                                 "of type `" + type(error).__name__ + "` for message `"
                                                                 + ctx.message.content + "`: `" + str(error) + "`")
        elif (isinstance(error, discord.HTTPException) or isinstance(error, aiohttp.ClientOSError)) \
                and not hasattr("on_error", ctx.command):
            await self.send_unexpected_error(ctx, error)
        elif isinstance(error, discord.ext.commands.CommandNotFound):
            if config.send_invalid_command:
                await ctx.send(":x: Sorry, `" + ctx.invoked_with +
                               "` is not a valid command.  Type `l?help` for a list of commands.")
            if ctx.guild is None:
                await self.get_channel(config.online_logger_id).send("Invalid command received from `" + ctx.author.name
                                                                     + "`: " + ctx.message.content)
            else:
                await self.get_channel(config.online_logger_id).send("Invalid command received from `" + ctx.author.name
                                                                     + "` on `" + ctx.guild.name + "`: " +
                                                                     ctx.message.content)
        elif isinstance(error, discord.ext.commands.CheckFailure):
            if isinstance(error, discord.ext.commands.NotOwner):
                await ctx.send(":warning: You are not authorized to run this command, "
                               "to be able to run `" + ctx.invoked_with +
                               "` you must be the owner of this bot.")
            else:
                await ctx.send(":warning: Either this command is disabled, you are not authorized to run this command, "
                               "or this command is not being run in the proper context.")
        elif isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send(":x: Your command arguments could not be interpreted, please try again (Did you forget a"
                           " \" character?).")
            if ctx.guild is None:
                await self.get_channel(config.online_logger_id).send("Invalid command arguments from `" +
                                                                     ctx.author.name + "` `: " + ctx.message.content)
            else:
                await self.get_channel(config.online_logger_id).send("Invalid command arguments from `" +
                                                                     ctx.author.name + "` on `" + ctx.guild.name + "`: "
                                                                     + ctx.message.content)

        else:
            await self.send_unexpected_error(ctx, error)

    async def send_unexpected_error(self, ctx, error):
        await ctx.send(":warning: An unexpected error occurred and a report has been sent to the developer.")
        tb = traceback.extract_tb(tb=error.original.__traceback__)
        await self.get_channel(config.online_logger_id).send(":warning: An unexpected error occurred of type `" +
                                                             type(error).__name__ + "` for message `" +
                                                             ctx.message.content + "`: `" + str(error) + "`" +
                                                             " in function `" + tb[-1].name + "`" +
                                                             " on line `" + str(tb[-1].lineno) + "`" +
                                                             " in file `" + tb[-1].filename + "`")


LPBot(EXTENSIONS).run(config.token)
