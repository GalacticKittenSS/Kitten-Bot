import discord
from discord.ext import tasks

import Kittenbot.Utils

import datetime
import json

class Twitch:
  def __init__(self, client):
      self.client = client
      self.check.start()
    
  @tasks.loop(seconds=30)
  async def check(self):
    for guild in self.client.guilds:
      settings = json.load(open(f"Settings/{guild.id}.json"))["Events"]["StreamAlert"]
      channel = guild.get_channel(settings["Channel"])
  
      url = None
      for user in settings["Users"]:
        if url:
          url += "&user_login=" + user
        else:
          url = "user_login=" + user
        
      live = Kittenbot.Utils.MakeTwitchRequest("https://api.twitch.tv/helix/streams?" + url)
      if not live:
        return
        
      offline = settings["Users"]
      for user in live:
        offline.remove(user["user_login"])
        await self.alert(user, channel, settings)
  
      if not settings["Remove Offline"]:
        return
        
      for user in offline:
        await self.removeMessage(user, channel, settings)
    
  async def alert(self, values, channel, settings):
    channel_name = values["user_name"]
    stream_title = values["title"]
    stream_game = values["game_name"]
    stream_viewers = values["viewer_count"]
    stream_thumbnail = values["thumbnail_url"].replace("{width}x{height}", "1920x1080")
  
    
    values = Kittenbot.Utils.MakeTwitchRequest("https://api.twitch.tv/helix/users?login=" + channel_name)[0]
    channel_url = "https://twitch.tv/" + values["display_name"]
    channel_image = values["profile_image_url"]
    
    if settings["Description"]:
      channel_description = values["description"]
    else:
      channel_description = discord.Embed.Empty
    
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
  
  async def removeMessage(self, user, channel, settings):
    values = Kittenbot.Utils.MakeTwitchRequest("https://api.twitch.tv/helix/users?login=" + user)[0]
    msg = settings["Message"].replace("{user}", values["display_name"])
    
    async for message in channel.history(limit=200):
      if msg == message.content:
        await message.delete

class Youtube:
  def __init__(self, client, time):
    self.last_checked_time = time
    self.client = client
    self.check.start()
  
  @tasks.loop(seconds=300)
  async def check(self):
    for guild in self.client.guilds:
      settings = json.load(open(f"Settings/{guild.id}.json"))["Events"]["VideoAlert"]
      channel = guild.get_channel(settings["Channel"])

      for user in settings["Ids"]:
        response = Kittenbot.Utils.MakeYoutubeSearchRequest(user, self.last_checked_time)["items"]
        
        if not response:
          continue
          
        for item in response:
          await self.alert(item["snippet"], channel, settings, item["id"])
    
    self.last_checked_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    
  async def alert(self, values, channel, settings, id):
    channel_name = values["channelTitle"]
    url = "https://www.youtube.com/watch?v=" + id["videoId"]
    title = values["title"]
    thumbnail = values["thumbnails"]["high"]["url"]
    
    if settings["Description"]:
      description = values["description"]
    else:
      description = discord.Embed.Empty

    if not settings["Colour"]:
      settings["Colour"] = 0xFF4B4B
  
    embed_text = discord.Embed(
      title=title,
      colour=discord.Colour(settings["Colour"]),
      url=url, 
      description=description, 
      timestamp=datetime.datetime.now()
    )

    if settings["Author"]:
      response = Kittenbot.Utils.MakeYoutubeChannelRequest(values["channelId"])["items"][0]["snippet"]
      channel_url = "https://www.youtube.com/channel/" + values["channelId"]
      channel_image = response["thumbnails"]["high"]["url"]
      
      embed_text.set_author(name=channel_name, icon_url=channel_image, url=channel_url)
    
    if settings["Image"]:
      embed_text.set_image(url=thumbnail)
    
    msg = settings["Message"].replace("{user}", channel_name)
    await channel.send(content=msg, embed=embed_text)