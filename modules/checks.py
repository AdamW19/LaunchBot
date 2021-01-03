import os
import config
from discord.ext import commands


def user_is_developer(ctx):
    for id in config.developers:
        if ctx.author.id == id:
            return True
    return False


def message_from_guild(id):
    def predicate(ctx):
        return ctx.message.guild.id == id
    return commands.check(predicate)


# not a discord.py check, but it still checks things
def make_sure_file_exists(path: str, alt_path: str):
    if os.path.exists(path):
        print("[LPBot] Found {}".format(path))
    else:
        if os.path.exists(alt_path):
            print("[LPBot] Found {} but not {}: renaming to {}".format(alt_path, path, alt_path))
            os.rename(alt_path, path)
        else:
            raise FileNotFoundError("ERROR: {} or {} not found!".format(path, alt_path))
