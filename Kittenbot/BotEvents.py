import discord.utils
import discord
import Kittenbot.Tasks
import Kittenbot.Utils

import datetime
import json

async def OnReady(client):
  print("We have logged in as {0.user}".format(client))
  
  Kittenbot.Tasks.Twitch(client)
  Kittenbot.Tasks.Youtube(client, datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))
  
  for guild in client.guilds:
    await Reset(client, guild)

async def Reset(client, guild):
  settings = json.load(open(f"Settings/{guild.id}.json", "r"))["Events"]["On Reaction"]["React for Role"]
  if settings:
    await sendReaction(client, settings, guild)

async def Join(client, settings, member):
  channel = client.get_channel(settings["Channel"])
  message = f"Welcome {member.mention} to **{member.guild.name}**. We hope you enjoy!"
  await channel.send(message)
  
  for r in settings["Roles"]:
    role = discord.utils.get(member.guild.roles, id=r)
    await member.add_roles(role)
    
async def Leave(client, settings, member):
  channel = client.get_channel(settings["Channel"])
  message = f"{member.mention} has left **{member.guild.name}**. We're sad to see you go"
  
  await channel.send(message)

from discord.utils import get

async def OnReaction(client, settings, payload):
  if settings["Pinbot"]:
    await Pin(client, settings["Pinbot"], payload)
  if settings["React for Role"]:
    await getRole(client, settings["React for Role"], payload, True)

async def OnReactionRemove(client, settings, payload):
  if settings["Pinbot"]:
    await Unpin(client, settings["Pinbot"], payload)
  if settings["React for Role"]:
    await getRole(client, settings["React for Role"], payload, False)
    
async def Pin(client, settings, payload):
  if payload.emoji.name != settings["Emoji"]:
    return
  
  message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
  reaction = get(message.reactions, emoji=payload.emoji.name)
  
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
      files.append(await Kittenbot.Utils.GetFileFromUrl(a.url))
      
    webhook = await client.get_channel(settings["Repost"]).create_webhook(
      name=message.author.name, 
      avatar= await Kittenbot.Utils.GetBytesFromUrl("https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(message.author))
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
  reaction = get(message.reactions, emoji=payload.emoji.name)
  
  if reaction and reaction.count >= settings["Pins Needed"]:
    reaction

  await message.unpin()

  async for msg in client.get_channel(settings["Repost"]).history(limit=200):
    if msg.content == message.content and msg.author.name == message.author.name:
      await msg.delete()
      continue

async def sendReaction(client, settings, guild):
  if not settings["Colour"]:
    settings["Colour"] = 0x8f43f0
  
  channel = client.get_channel(settings["Channel"])
  embed = discord.Embed(
    title=settings["Title"],
    colour=discord.Colour(settings["Colour"]), 
    description=settings["Description"]
  )
  
  for role in settings["Roles"]:
    embed.add_field(name=guild.get_role(role["Role"]).name + " " + role["Emoji"], value=role["Message"], inline=True)
  
  message = 0
  async for msg in channel.history(limit=200):
    if msg.content == settings["Message"]:
      message = msg
      await msg.edit(content=settings["Message"], embed=embed)
  
  if not message:
    message = await channel.send(content=settings["Message"], embed=embed)
  
  for role in settings["Roles"]:
    await message.add_reaction(role["Emoji"])
    
async def getRole(client, settings, payload, add):
  if payload.user_id == client.user.id:
    return
  
  guild = client.get_guild(payload.guild_id)
  channel = guild.get_channel(settings["Channel"])
  member = guild.get_member(payload.user_id)

  if not member:
    return print("Member Not Found")

  async for message in channel.history(limit=200): 
    if message.id != payload.message_id or message.content != settings["Message"]:
      continue

    role = None;
    for r in settings["Roles"]:
      if payload.emoji.name == r["Emoji"]:
        role = guild.get_role(r["Role"])
        
        if add:
          await member.add_roles(role)
        else:
          await member.remove_roles(role)

    if not role:
      print("Role not found")

    return