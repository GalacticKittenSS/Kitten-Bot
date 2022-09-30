import Storage

import requests
import aiohttp

async def GetBytesFromUrl(my_url):
  async with aiohttp.ClientSession() as session:
    async with session.get(my_url) as resp:
      if resp.status != 200:
          return
        
      return await resp.read()

def MakeTwitchRequest(url):
  head = {
    'Client-ID' : Storage.TwitchClient,
    'Authorization' : "Bearer " + Storage.TwitchKey
  }

  values = requests.get(url, headers=head).json()["data"]
  return values