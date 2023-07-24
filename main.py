import time, threading, json, os
import discord
from discord.ext import commands
from discord import app_commands

from libs import twitch

class Data():
    tokens_data = open('integrity.txt',"r").read().splitlines()

def update_tok():
    while True:
        Data.tokens_data = open('integrity.txt',"r").read().splitlines()
        time.sleep(20)

threading.Thread(target=update_tok).start()

config = json.loads(open("config.json","r", encoding="utf8").read())

banner = "https://cdn.discordapp.com/attachments/1113512911583858728/1125458369281527930/baner.png"
embed_color = 15548997

    
class Cooldown:
    def __init__(self, duration):
        self.duration = duration
        self.last_end_time = None
    def remaining_time(self):
        if self.last_end_time is None:
            return 0
        else:
            return max(self.last_end_time - time.time(), 0)
    def start(self):
        self.last_end_time = time.time() + self.duration
    def is_on_cooldown(self):
        return self.remaining_time() > 0


class Discord_Bot:

    bot = None
    TwitchTools = None
    followed_users = []

    def __init__(self) -> None:

        self.cooldown = {}
        self.cooldown_kick = {}
        self.followed = {}

        self.TwitchTools = twitch.Tools()
        self.TwitchFollowers = twitch.Follow()

        self.bot_prefix = config['bot_config']["prefix"]
        self.bot_token = config['bot_config']["token"]
        self.server_id = config['bot_config']["server_id"]
        self.twitch_channel = config['bot_config']["channel"]

        os.system("cls")

        self.run_bot()
        

    def commands(self):

        @self.bot.event
        async def on_ready():
            await self.tree.sync(guild=discord.Object(id=self.server_id))
            await self.bot.change_presence(activity=discord.Game(name=f"excer.pro"))


        # USER
        
        @self.tree.command(name="tfollow",description="[TWITCH] Send followers to selected channel", guild=discord.Object(id=self.server_id))
        async def tfollow(interaction, username: str,):
            if interaction.channel.id == self.twitch_channel:
                target_id = self.TwitchTools.user_id(username)
                
                if target_id != False:

                    if not target_id in self.cooldown:
                        self.cooldown[target_id] = Cooldown(240)     
                    

                    self.cooldown[target_id]
                    if not self.cooldown[target_id].is_on_cooldown():
                        self.cooldown[target_id].start()
                    else:
                        embed = discord.Embed(color=embed_color, description="```Cooldown: {}```".format(self.cooldown[target_id].remaining_time() / 60))
                        embed.set_image(url=banner)
                        await interaction.response.send_message(embed=embed)
                        return
                                    
                    for role_name in reversed(config['tfollow']):
                        if discord.utils.get(interaction.guild.roles, name=role_name) in interaction.user.roles:
                            follow_count = config['tfollow'][role_name]
                            self.TwitchFollowers.send_follow(target_id, follow_count, Data.tokens_data)

                            

                            embed = discord.Embed(color=embed_color, description=f"```Excer Followers -> {follow_count}```")
                            embed.set_image(url=banner)
                            await interaction.response.send_message(embed=embed)
                            return
                else:
                    embed = discord.Embed(color=embed_color, description=f"```Invalid Username```")
                    embed.set_image(url=banner)
                    await interaction.response.send_message(embed=embed)
                    return
  
        # ADMIN

        
        @self.tree.command(name="nuke",description="[ADMIN] Channel nuke", guild=discord.Object(id=self.server_id))
        @commands.has_permissions(administrator=True)
        async def nuke(interaction, channel: discord.TextChannel):
            if interaction.user.guild_permissions.administrator:
                nuke_channel = discord.utils.get(interaction.guild.channels, name=channel.name)
                if nuke_channel is not None:
                    new_channel = await nuke_channel.clone(reason="Has been Nuked!")
                    await new_channel.edit(position=nuke_channel.position)
                    await nuke_channel.delete()
                    embed = discord.Embed(color=embed_color, description=f"```Excer Nuke```")
                    embed.set_image(url=banner)
                    await new_channel.send(embed=embed)
                else:
                    await interaction.send(f"No channel named {channel.name} was found!")

            
        @self.tree.command(name="embed",description="[ADMIN] Send Embed", guild=discord.Object(id=self.server_id))
        @commands.has_permissions(administrator=True)
        async def embed(interaction, embed_description: str, image_url: str = None, ping: bool = False):
            if interaction.user.guild_permissions.administrator:
                embed = discord.Embed(color=embed_color, description=embed_description.replace(r"\n","\n"))
                if image_url != None:
                    embed.set_image(url=image_url)
                else:
                    embed.set_image(url=banner)
                if ping == True:
                    await interaction.channel.send("||@everyone||",embed=embed)
                else:
                    await interaction.channel.send(embed=embed)

                return
        
    def run_bot(self):

        self.bot = discord.Client(
            command_prefix=self.bot_prefix, 
            help_command=None, 
            intents=discord.Intents().all()
        )

        self.tree = app_commands.CommandTree(self.bot)

        self.commands()
        self.bot.run(self.bot_token)
        


if __name__ == "__main__":

    Discord_Bot()
