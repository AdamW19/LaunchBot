import config
import discord
from discord.ext import commands
from discord.ext.commands import Cog


async def gen_join_leave_embed(member, on_leave):
    # Generates the embed when a member leaves/joins the server
    member_mention = member.mention
    member_color = member.colour
    member_roles = member.roles
    member_id = str(member.id)
    member_join = member.joined_at.strftime("%B %d, %Y %H:%M:%S UTC")  # <Abbr mon> <day>, <yr> <hr>:<min>:<sec> UTC
    member_avatar_url = member.avatar_url
    member_name = str(member)

    roles = [role.mention for role in member_roles[1:]]  # skip 1st one because that's `@everyone`
    roles = ' '.join(roles)
    if len(roles) <= 0:
        roles = "*None*"

    if on_leave:
        embed = discord.Embed(color=member_color, title="Member left", description=member_mention + " " + member_name)
        embed.add_field(name="Join date", value=member_join)
        embed.add_field(name="Roles", value=roles)
    else:
        embed = discord.Embed(color=member_color, title="Member joined", description=member_mention + " " + member_name)

    embed.set_author(icon_url=member_avatar_url, name=member_name)
    embed.set_thumbnail(url=member_avatar_url)
    embed.set_footer(text="Discord ID: " + member_id)

    return embed


class Log(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = await gen_join_leave_embed(member, False)
        await self.bot.get_channel(config.online_logger_id).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = await gen_join_leave_embed(member, True)
        await self.bot.get_channel(config.online_logger_id).send(embed=embed)


def setup(bot):
    bot.add_cog(Log(bot))
