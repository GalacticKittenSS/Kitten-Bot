import json
import urllib
import os

from googleapiclient.discovery import build

import io
import aiohttp
import discord

async def GetFileFromUrl(my_url):
  async with aiohttp.ClientSession() as session:
    async with session.get(my_url) as resp:
      if resp.status != 200:
          return
        
      data = io.BytesIO(await resp.read())
      return discord.File(data, my_url)

async def GetBytesFromUrl(my_url):
  async with aiohttp.ClientSession() as session:
    async with session.get(my_url) as resp:
      if resp.status != 200:
          return
        
      return await resp.read()
      
def MakeYoutubeChannelRequest(channel_id):
  youtube = build('youtube', 'v3', developerKey=os.getenv("Youtube Token"))
  request = youtube.channels().list(
    part="snippet",
    id=channel_id
  )
  response = request.execute()
  youtube.close()
  return response

def MakeYoutubeSearchRequest(channel_id, last_checked_time):
  youtube = build('youtube', 'v3', developerKey=os.getenv("Youtube Token"))
  request = youtube.search().list(
    part="snippet",
    channelId=channel_id,
    maxResults=1,
    publishedAfter=last_checked_time,
    order="date"
  )
  response = request.execute()
  youtube.close()
  return response

def MakeTwitchRequest(url):
  request = urllib.request.Request(url)
  request.add_header("Client-ID", os.getenv("Twitch Client"))
  request.add_header("Authorization", "Bearer " + os.getenv("Twitch Token"))
    
  f = urllib.request.urlopen(request)
  values = json.load(f)["data"]
  f.close()

  if values:
    return values
  else:
    return False