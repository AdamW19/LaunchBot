import discord
import aiohttp
import config
import traceback
import sys
from discord.ext import commands
import os
import asyncio

print("Initializing...")

EXTENSIONS = []

class LPBot(commands.Bot):
    def __init__(self, extensions):
        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        intents.reactions = True

        super().__init__(command_prefix=config.prefix, description=config.description, case_insensitive=True,
                         intents=intents)

        for e in extensions:
            self.load_extension(e)

    async def on_ready(self):
        print("Connected")
        self.session = aiohttp.ClientSession()
        await self.get_channel(config.online_logger_id).send("*Connected to Discord*")

    async def on_command(self, ctx):
        await self.get_channel(config.online_logger_id).send("Command received from `" + ctx.author.name + "` on `" +
                                                             ctx.guild.name + "`: " + ctx.message.content)

    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.Forbidden) or "missing permissions" in str(error).lower():
            await ctx.send(":x: I do not have permission to send embedded messages in this channel and/or server!  "
                           "Make sure I have the permission `Embed Links`, or I can't function!")
            await self.get_channel(config.online_logger_id).send(":information_source: A handled error occured "
                                                                 "of type `" + type(error).__name__ + "` for message `"
                                                                 + ctx.message.content + "`: `" + str(error) + "`")
        elif (isinstance(error, discord.HTTPException) or isinstance(error, aiohttp.ClientOSError)) \
                and not hasattr("on_error", ctx.command):
            await self.send_unexpected_error(ctx, error)
        elif isinstance(error, discord.ext.commands.CommandNotFound):
            if config.send_invalid_command:
                await ctx.send(":x: Sorry, `" + ctx.invoked_with +
                               "` is not a valid command.  Type `l?help` for a list of commands.")
            await self.get_channel(config.online_logger_id).send("Invalid command received from `" + ctx.author.name +
                                                                 "` on `" + ctx.guild.name + "`: " +
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
            await self.get_channel(config.online_logger_id).send("Invalid command arguments received from `" +
                                                                 ctx.author.name + "` on `" + ctx.guild.name + "`: " +
                                                                 ctx.message.content)
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
