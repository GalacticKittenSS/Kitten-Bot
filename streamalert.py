import discord
import json
from discord.ext import tasks
from datetime import datetime
import urllib
import os
import variable

@tasks.loop(seconds=10)
async def checkstream(client):

  role = client.get_guild(variable.guild_id).get_role(variable.react_roles[0])
  channel = client.get_channel(variable.streamalert_channel)
  
  url = "https://api.twitch.tv/kraken/streams/" + os.getenv("TWITCH_CHANNEL_ID")
  
  request = urllib.request.Request(url)
  request.add_header('Accept', 'application/vnd.twitchtv.v5+json')
  request.add_header("Client-ID", os.getenv("client_id"))
  request.add_header("Authorization", "OAuth jo6pf9bfqqqvpyoq56fdtz2t81vu5g")
  request.add_header("Content-Type", "application/json")

  f = urllib.request.urlopen(request)
  values = json.load(f)
  f.close()

  if values["stream"] != None:
    channel_name = values['stream']['channel']["display_name"]
    stream_title = values["stream"]["channel"]["status"]
    stream_game = values["stream"]["game"]
    stream_viewers = values["stream"]["viewers"]
    channel_url = values["stream"]["channel"]["url"]
    channel_description = values["stream"]["channel"]["description"]
    channel_image = values["stream"]["channel"]["logo"]

    embed_text = discord.Embed(title=stream_title,colour=discord.Colour(0x8f43f0),url=channel_url,description=channel_description)
    embed_text.set_image(url=channel_image)
    embed_text.set_author(name=channel_name, icon_url=channel_image)
    if stream_game != None:
      embed_text.add_field(name="Playing", value=stream_game, inline=True)
    if stream_viewers != None:
      embed_text.add_field(name="Viewers",value=stream_viewers,inline=False)
    embed_text.set_footer(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
      
    count = 0
    async for message in channel.history (limit=200):
      if "GalacticKittenSS is live!" in message.content:
        await message.edit(content=role.mention + " GalacticKittenSS is live!", embed=embed_text)
        count = 1
        
    if count == 0:
      await channel.send(content=role.mention + " GalacticKittenSS is live!", embed=embed_text)


  if values["stream"] == None:
    async for message in channel.history (limit=200):
      if "GalacticKittenSS is live!" in message.content:
        await message.delete()