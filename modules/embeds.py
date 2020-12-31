import discord
import config
import math

help_embed_fields = {
    "rotation_commands":
        {"title": "Rotation Commands",
         "body": "`l?schedule` - gets more specific help for all rotation commands.\n"
                 "`l?schedule [regular|ranked|league|salmon]` - get the current mode for the given battle type.\n"
                 "`l?schedule [regular|ranked|league|salmon] next` - gets the next rotation for the given mode."
         },
    "profile_commands":
        {"title": "Profile Commands",
         "body": "`l?profile` - gets your profile.\n"
                 "`l?profile [discord_name|discord_id]` - gets someone else's profile.\n"
                 "`l?profile [set|delete] [fc]` - adds/deletes your friend code from your profile.\n"
         },
    "draft_commands":
        {"title": "Draft Commands -- `Launchpoint` role required",
         "body": "`l?draft` - starts a draft. \n"
         },
    "misc_commands":
        {"title": "Misc. Commands",
         "body": "`l?help` - view the help for LaunchBot\n"
                 "`l?ping` - pong! tests to see if LaunchBot is functioning properly (also shows ping time)\n"
                 "`l?special_thanks` - a special thank you for the technologies used to make LaunchBot"
         },
    "staff_commands":
        {
            "title": "Staff Commands -- `Staff` role required",
            "body": "`l?settings` - for a list of all staff commands.\n"
        },
    "command_syntax":
        {"title": "Command Syntax",
         "body": "Commands are formatted like this: `l?command [argument]`. "
                 "Some commands have more than one argument, in which case arguments are separated by a space. "
                 "You *do not* type the brackets around the command argument.\n"
                 "**Examples:**\n"
                 "1. `l?schedule regular`\n"
                 "2. `l?rotation salmon next`\n"
                 "3. `l?settings season start`\n"
         }
}


def add_list_embed_fields(output_string, embed, header, cutoff_mode=False):
    if len(output_string) <= 1024:
        embed.add_field(name=header, value=output_string)
    else:
        sections = []
        num_sections = math.ceil(len(output_string) / 1024)
        index_of_first_newline = 0
        index_of_last_newline = 0
        for i in range(0, num_sections):
            n = index_of_first_newline
            for c in output_string[index_of_first_newline:index_of_first_newline + 1024]:
                if c == '\n' or cutoff_mode:
                    index_of_last_newline = n
                n += 1
            sections.append(output_string[index_of_first_newline:index_of_last_newline + 1])
            index_of_first_newline = index_of_last_newline
        continued_string = ""
        for section in sections:
            embed.add_field(name=header + continued_string, value=section)
            continued_string = " (Continued)"


def generate_base_help_embed(bot):
    help_embed = discord.Embed(title=bot.user.name + " Help", color=config.embed_color)
    help_embed.set_thumbnail(
        url=bot.user.avatar_url)
    help_embed.set_footer(text="Developed by Adam!#888 and DRF#6237")
    return help_embed


def add_help_embed_field(help_embed, key):
    help_embed.add_field(name=help_embed_fields[key]["title"], value=help_embed_fields[key]["body"])


def add_help_embed_footer_links(help_embed, bot):
    help_embed.add_field(name="<:github:791151957226160178>  Github",
                         value="Visit the code for " + bot.user.name + " [here.](https://github.com/AdamW19/LaunchBot)")
    help_embed.add_field(name=":pray:  Special Thanks",
                         value="Type `l?special_thanks` for any credit for any APIs and technology used to make " +
                               bot.user.name)
