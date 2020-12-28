import config
import discord
from modules.gif_generator import generate_gif
from modules.splatoon_rotation import SplatoonRotation, ModeTypes
from modules.splatnet import Splatnet
from datetime import datetime
from discord.ext import commands
from modules.date_difference import DateDifference


class Rotation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.splatnet = Splatnet(session=bot.session)

    async def on_ready(self):
        self.splatnet.connection = self.bot.session

    @commands.group(case_insensitive=True, invoke_without_command=True, aliases=["schedule", "schedules", "rotations",
                                                                                 "info", "r"])
    async def rotation(self, ctx):
        # General help embed
        embed = discord.Embed(title="Rotation Help", color=config.embed_color, description="Alias for command are "
                                                                                           "`rotation`, `schedule`, "
                                                                                           "`schedules`, `rotations`, "
                                                                                           "`info`, or "
                                                                                           "`r`.")  # PEP 8 is stupid
        embed.add_field(name="Turf War", value="The subcommand for Turf War is `regular`, `turf`, `t`, `tw`, or `reg`.")
        embed.add_field(name="Ranked", value="The subcommand for Ranked is `ranked`, `rank`, `rk`, `r`, or `rked`.")
        embed.add_field(name="League", value="The subcommand for League is `league`, `l`, `double`, or `quad`.")
        embed.add_field(name="Salmon Run", value="The subcommand for Salmon Run is `salmon`, `sr`, `s`, or `sal`.")

        embed.set_footer(text="You can get the next rotation by adding `next` or `n` as an argument.")

        await ctx.send(embed=embed)

    @rotation.group(case_insensitive=True, invoke_without_command=True, aliases=["turf", "t", "reg", "tw"])
    async def regular(self, ctx):
        await self.make_single_rotation(ModeTypes.REGULAR, ctx)

    @rotation.group(case_insensitive=True, invoke_without_command=True, aliases=["rank", "rk", "rked", "r"])
    async def ranked(self, ctx):
        await self.make_single_rotation(ModeTypes.RANKED, ctx)

    @rotation.group(case_insensitive=True, invoke_without_command=True, aliases=["l", "double", "quad"])
    async def league(self, ctx):
        await self.make_single_rotation(ModeTypes.LEAGUE, ctx)

    @rotation.group(case_insensitive=True, invoke_without_command=True, aliases=["sr", "s", "sal"])
    async def salmon(self, ctx):
        await self.make_single_rotation(ModeTypes.SALMON, ctx)

    @salmon.command(name="next", aliases=["n"])
    async def salmon_next(self, ctx):
        await self.make_next_rotation(ModeTypes.SALMON, ctx, False)

    @ranked.command(name="next", aliases=["n"])
    async def ranked_next(self, ctx):
        await self.make_next_rotation(ModeTypes.RANKED, ctx, False)

    @league.command(name="next", aliases=["n"])
    async def league_next(self, ctx):
        await self.make_next_rotation(ModeTypes.LEAGUE, ctx, False)

    @regular.command(name="next", aliases=["n"])
    async def turf_next(self, ctx):
        await self.make_next_rotation(ModeTypes.REGULAR, ctx, False)

    async def make_single_rotation(self, schedule_type: ModeTypes, ctx):
        channel_id = ctx.channel.id
        time = datetime.now()

        self.splatnet.update_connection(self.bot.session)  # It's really dumb but sometimes on_ready doesn't run...

        rotation = SplatoonRotation(time, schedule_type, self.splatnet)
        success = await rotation.populate_data()

        if success:
            if rotation.mode_type is ModeTypes.SPLATFEST:
                await ctx.send(":warning: It's currently Splatfest -- **Ranked/League modes are not available.**")
            embed, file = await self.generate_embed(rotation, channel_id, False, False)
            if file is None:
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=embed, file=file)
        else:
            if rotation.mode_type is ModeTypes.SALMON:
                await ctx.send(":warning: Salmon Run is currently **not** available. Here is the next rotation:")
                await self.make_next_rotation(schedule_type, ctx, True)
            else:
                await ctx.send(":x: Not able to get rotation information. Contact the developers.")

    async def make_next_rotation(self, schedule_type: ModeTypes, ctx, overflow: bool):
        channel_id = ctx.channel.id
        time = datetime.now()

        self.splatnet.update_connection(self.bot.session)   # It's really dumb but sometimes on_ready doesn't run...

        rotation = SplatoonRotation(time, schedule_type, self.splatnet)
        await rotation.populate_data()
        rotation.target_time = rotation.next_rotation
        success = await rotation.populate_data()

        if success:
            embed, file = await self.generate_embed(rotation, channel_id, True, overflow)
            if file is None:
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=embed, file=file)
        else:
            await ctx.send(":x: Not able to get rotation. Contact the developers.")

    async def generate_embed(self, rotation: SplatoonRotation, channel_id: str, is_next: bool, overflow: bool):
        title = ""
        if is_next:
            title = "Next"
        title += " Rotation Information - "
        thumbnail = ""
        if rotation.mode_type is ModeTypes.SPLATFEST:
            title += "Splatfest Battle"
            thumbnail = config.images["splatfest"]
        elif rotation.mode_type is ModeTypes.REGULAR:
            title += "Regular Battle"
            thumbnail = config.images["regular"]
        elif rotation.mode_type is ModeTypes.RANKED:
            title += "Ranked Battle"
            thumbnail = config.images["ranked"]
        elif rotation.mode_type is ModeTypes.LEAGUE:
            title += "League Battle"
            thumbnail = config.images["league"]
        elif rotation.mode_type is ModeTypes.SALMON:
            title += "Salmon Run"
            thumbnail = config.images["salmon"]

        embed = discord.Embed(title=title, color=config.embed_color)
        embed.set_thumbnail(url=thumbnail)

        # custom stuff for salmon run
        if rotation.mode_type is ModeTypes.SALMON:
            # Use helper method to generate salmon run info
            embed = await Rotation.generate_salmon_embed(embed, rotation)
        else:
            embed.add_field(name="Mode", value=rotation.mode)
            if rotation.mode_type is ModeTypes.SPLATFEST:
                stage_str = rotation.stage_a + "\n" + rotation.stage_b + "\n" + rotation.splatfest.stage_c
            else:
                stage_str = rotation.stage_a + "\n" + rotation.stage_b
            embed.add_field(name="Stages", value=stage_str)

        # If we've come here b/c there's no current salmon run, print when the next rotation will end instead
        if overflow:
            time = rotation.next_rotation
        elif is_next:
            time = rotation.start_time
        else:
            time = rotation.end_time

        # Calculates the amount of time until the next rotation
        time_diff = DateDifference.subtract_datetimes(time, datetime.now())
        time_str = str(time_diff)

        if rotation.mode_type is ModeTypes.SALMON and not overflow and not is_next:
            time_until_str = "Time Until End of Rotation"
        elif is_next:
            time_until_str = "Time Until Start of Rotation"
        else:
            time_until_str = "Time Until Next Rotation"
        embed.add_field(name=time_until_str, value=time_str, inline=False)

        embed, file = await self.generate_send_gif(embed, rotation, rotation.mode_type, channel_id)
        return embed, file

    async def generate_send_gif(self, embed, rotation_data: SplatoonRotation, schedule_type: ModeTypes,
                                channel_id: str):
        if schedule_type is not ModeTypes.SALMON:
            #  generate the gif, make it a discord file, and send it off
            generated_gif = await generate_gif(rotation_data, channel_id, self.bot)
            file = discord.File(generated_gif)
            embed.set_image(url="attachment://" + generated_gif)

            return embed, file
        else:
            return embed, None

    @staticmethod
    async def generate_salmon_embed(embed: discord.Embed, rotation: SplatoonRotation):
        embed.set_image(url=rotation.stage_a_image)
        embed.add_field(name="Stage", value=rotation.stage_a)
        # use special formatting because salmon run can occur between two separate days
        embed.add_field(name="Weapons",
                        value=SplatoonRotation.print_sr_weapons(rotation.weapons_array))
        return embed


def setup(bot):
    bot.add_cog(Rotation(bot))
