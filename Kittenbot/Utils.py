import os
import requests

import Storage

from googleapiclient.discovery import build
import aiohttp

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
  head = {
    'Client-ID' : Storage.TwitchClient,
    'Authorization' : "Bearer " + Storage.TwitchKey
  }

  values = requests.get(url, headers=head).json()["data"]
  return values