import discord.utils
import Utils

import Logger

async def Pin(client, settings, payload):
  if payload.emoji.name != settings["Emoji"]:
    return
  
  message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
  reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
  
  if not reaction or reaction.count < settings["Pins Needed"]:
    return
    
  if settings["Pin to Channel"]:
    await message.pin()
  if settings["Repost"]:
    embed = None
    if message.embeds:
      embed = message.embeds[0]

    files = []
    for a in message.attachments:
      files.append(await Utils.GetFileFromUrl(a.url))
      
    webhook = await client.get_channel(settings["Repost"]).create_webhook(
      name=message.author.name, 
      avatar=await Utils.GetBytesFromUrl(message.author.avatar.url),
      reason=f"Message by {message.author.name} was pinned"
    )
    await webhook.send(
      content=message.content, 
      embed=embed,
      files=files
    )
    await webhook.delete()

async def Unpin(client, settings, payload):
  if payload.emoji.name != settings["Emoji"]:
    return
    
  message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
  reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
  
  if reaction and reaction.count >= settings["Pins Needed"]:
    reaction

  await message.unpin()

  async for msg in client.get_channel(settings["Repost"]).history(limit=200):
    if msg.content == message.content and msg.author.name == message.author.name:
      await msg.delete()
      continue