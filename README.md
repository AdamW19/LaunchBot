# LaunchBot
A bot for LaunchPoint, a pickup server for those who are just starting competitive Splatoon. Could also be a good general purpose draft bot.

## Features
- Pull current and next Ranked/League/Regular/Salmon Run rotations.
- Logs when a member joins or leaves the server.
- Ability to host a draft with a player skill system.
- Private staff commands to start/end a season and to set a draft maplist via a [nkitten code](http://nkitten.net/splatoon2/random/).
- Hosts a global leaderboard and an on-demand leaderboard with pagination.

## How to Run
First, you'll need to clone the repo:
```console
git clone https://github.com/AdamW19/LaunchBot.git
```

Then you'll need to make your own `config.py` file. You are free to use `config_public.py` as the base. You'll need to get your own bot token,
and edit the various logging channels and such.
Then rename it to `config.py`:

```console
cp config_public.py config.py
```
If you forget to rename it, the bot will rename it for you, but will stop code execution just in case you forgot to 
populate the file.

You'll also need to install any dependencies. Use `pip` and the provided `requirements.txt`:
```console
pip install -r requirements.txt
```

Then just run the bot with `python3`:
```console
python3 LPBot.py
```
You should be good to go! For your information, all files used to generate gifs are in `/` and all databases are stored in `/db`. Files used to generate gifs are
auto deleted every 5 minutes as long as the bot is actively running.

## PR and Issues
If you notice a bug, a potential issue, or want to request new functionality with LaunchBot, please feel free to open 
up a new issue! If you're extra amazing, you're also welcome to do a pull request. 

## Technologies Used/Special Thanks
Here is a list of the APIs/technologies we used to make LaunchBot:
- LaunchBot is written in Python 3 with
[discord.py](https://discordpy.readthedocs.io/en/latest/) and 
SQLite. 
- Player power levels uses Microsoft's [Trueskill™](http://research.microsoft.com/en-us/projects/trueskill/) system.

- We would like to thank [splatoon2.ink](https://splatoon2.ink/) for the
rotation API.
- A majority of the rotation commands, the help commands, and the error parsing comes from [ktraw2's SplatBot](https://github.com/ktraw2/SplatBot).

- All other libraries used to make LaunchBot can be found in the given `requirements.txt`.

# License
The code in this repository is licensed under the GNU General Public License v3.0. Please visit [the license](LICENSE) for more information. Note that Microsoft's 
Trueskill™ player ranking system is only licensed for personal and non-commercial use; if you are planning to use this bot for commercial purposes, you will need
to change the player ranking system. Trueskill™ is a registered trademark of the Microsoft Corporation. All rights reserved.
