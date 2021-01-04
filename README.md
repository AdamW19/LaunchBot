# LaunchBot
A bot for LaunchPoint. Could also be a good general purpose draft server.

## Features
- Pull current and next Ranked/League/Regular/Salmon Run rotations.
- Logs when a member joins or leaves the server
- Ability to host a draft with a player skill system.
- Private staff commands to start/end a season and to set a draft maplist via a [nkitten code](http://nkitten.net/splatoon2/random/).
- Hosts a leaderboard with pagination and updating post.

## How to Run
You'll need to make your own `config.py` file. You are free to use `config_public.py` as the base. You'll need to get your own bot token,
and edit the various logging channels and such.
Then rename it to `config.py`:

```console
cp config_public.py config.py
```
If you forget to rename it, the bot will rename it for you, but will stop code execution just in case you forget to 
populate the file.

You'll also need to install any dependencies. Use `pip` and the provided `requirements.txt`:
```console
pip install -r requirements.txt
```

Then just run the bot with `python3`:
```console
python3 LPBot.py
```
You should be good to go!

## PR and Issues
If you notice a bug, a potential issue, or want to request new functionality with LaunchBot, please feel free to open 
up a new issue! If you're extra amazing, you're also welcome to do a pull request. 

## Technologies Used/Special Thanks
Here is a list of the APIs/technologies we used to make LaunchBot:
- We would like to thank [splatoon2.ink](https://splatoon2.ink/) for the
rotation API.
- LaunchBot is written in Python 3 with
[discord.py](https://discordpy.readthedocs.io/en/latest/) and 
SQLite. 
- Player power levels uses [Trueskill™](http://research.microsoft.com/en-us/projects/trueskill/).
Trueskill™ is a registered trademark of the Microsoft Corporation. All rights reserved.
- A majority of the rotation commands and the error parsing comes from [ktraw2's Splatbot](https://github.com/ktraw2/SplatBot).

# License
This repo is licensed under the GNU General Public License v3.0. Please visit [the license](LICENSE) for more information.
