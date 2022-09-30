import discord
from discord.ext import tasks

import Utils

import datetime
import json

class StreamAlert:
  def __init__(self, client):
    self.client = client
    self.check.start()
  
  @tasks.loop(seconds=120)
  async def check(self):
    for guild in self.client.guilds:
      with open(f"Settings/{guild.id}.json", "r") as f:
        settings = json.load(f)["Events"]["StreamAlert"]
      
      if not settings:
        continue

      channel = guild.get_channel(settings["Channel"])

      if len(settings['Users']) == 0:
        return
  
      url = f"user_login={settings['Users'][0]}"
      for user in settings['Users']:
        if settings['Users'][0] == user:
          continue
        url += f"&user_login={user}" 

      live = Utils.MakeTwitchRequest("https://api.twitch.tv/helix/streams?" + url)
        
      offline = settings["Users"]
      for user in live:
        offline.remove(user["user_login"])
        await self.alert(user, channel, settings)
  
      if not settings["Remove Offline"]:
        return
        
      for user in offline:
        await self.remove_message(user, channel, settings)
    
  async def alert(self, values, channel, settings):
    channel_name = values["user_name"]
    channel_login = values['user_login']
    stream_title = values["title"]
    stream_game = values["game_name"]
    stream_viewers = values["viewer_count"]
    stream_thumbnail = values["thumbnail_url"].replace("{width}x{height}", "1920x1080")
  
    values = Utils.MakeTwitchRequest("https://api.twitch.tv/helix/users?login=" + channel_login)[0]
    channel_url = "https://twitch.tv/" + channel_login
    channel_image = values["profile_image_url"]
    
    channel_description = None
    if settings["Description"]:
      channel_description = values["description"]
    
    if not settings["Colour"]:
      settings["Colour"] = 0x8f43f0
  
    embed_text = discord.Embed(
      title=stream_title,
      colour=discord.Colour(settings["Colour"]),
      url=channel_url, 
      description=channel_description, 
      timestamp=datetime.datetime.now()
    )

    if settings["Author"]:
      embed_text.set_author(name=channel_name, icon_url=channel_image)
    
    if settings["Image"]:
      embed_text.set_image(url=stream_thumbnail)
      
    if stream_game and settings["Game"]:
      embed_text.add_field(name="Playing", value=stream_game, inline=True)
    
    if stream_viewers and settings["Viewers"]:
      embed_text.add_field(name="Viewers",value=stream_viewers, inline=True)
    
    msg = settings["Message"].replace("{user}", channel_name)
    
    found = False
    async for message in channel.history(limit=200):
      if msg == message.content:
        await message.edit(content=msg, embed=embed_text)
        found = True
        
    if not found:
      await channel.send(content=msg, embed=embed_text)
  
  async def remove_message(self, user, channel, settings):
    values = Utils.MakeTwitchRequest("https://api.twitch.tv/helix/users?login=" + user)[0]
    msg = settings["Message"].replace("{user}", values["display_name"])
    
    async for message in channel.history(limit=200):
      if msg == message.content:
        await message.delete()