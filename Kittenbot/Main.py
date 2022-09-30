import discord
import discord.utils
from discord.ext import commands

import Awake
import Logger
import Storage

import CustomHelp
import Cogs
import Tasks
import Pinbot

import json

def guild_prefix(client, message):
  with open(f"Settings/{message.guild.id}.json", 'r') as f:
    settings = json.load(f)
  return settings["Prefix"]

#Client
activity = discord.Game(name="Now Using discord.py 2.0", type=3)
customHelp = CustomHelp.Help()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix=(guild_prefix), intents=intents, help_command=customHelp, activity=activity, status=discord.Status.online)
client.sync_tree = False #Only sync if changes have been made to hybrid commands 

#On Ready
@client.event
async def on_ready():
  Logger.Setup(
    level = Logger.INFO,
    filelevel = Logger.DEBUG,
    fmt = "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    filename = "Kittenbot.log"
  )

  await client.add_cog(Cogs.Commands(client))
  await client.add_cog(Cogs.Moderation(client))

  if client.sync_tree:
    Logger.Info("Syncing Bot Tree...")
    await client.tree.sync()
    client.sync_tree = False
    
  Logger.Info("We have logged in as {0.user}".format(client))
  
  Tasks.StreamAlert(client)
  
  for guild in client.guilds:
    with open(f"Settings/{guild.id}.json", "r") as f:
      file = json.load(f)

    settings = file["Events"]["On Reaction"]["React for Role"]
    if not settings:
      continue

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
    
    try:
      message = await channel.fetch_message(settings["MessageID"])
      await message.edit(content=settings["Message"], embed=embed)
    except discord.errors.NotFound:
      message = await channel.send(content=settings["Message"], embed=embed)
      file["Events"]["On Reaction"]["React for Role"]["MessageID"] = message.id

      with open(f"Settings/{guild.id}.json", "w") as f:
        json.dump(file, f, indent = 2)
    
    for role in settings["Roles"]:
      await message.add_reaction(role["Emoji"])
    

#Join
@client.event
async def on_member_join(member):
  with open(f"Settings/{member.guild.id}.json", "r") as f:
    settings = json.load(f)["Events"]["Member Join"]
  
  if not settings:
    return

  channel = client.get_channel(settings["Channel"])
  message = f"Welcome {member.mention} to **{member.guild.name}**. We hope you enjoy!"
  await channel.send(message)
  
  for r in settings["Roles"]:
    role = member.guild.get_role(int(r))
    if not role:
      Logger.Info(f"Role with id {r} not found")
    await member.add_roles(role)

#Leave
@client.event
async def on_member_remove(member):
  with open(f"Settings/{member.guild.id}.json", "r") as f:
    settings = json.load(f)["Events"]["Member Join"]
  
  if not settings:
    return

  channel = client.get_channel(settings["Channel"])
  message = f"{member.mention} has left **{member.guild.name}**. We're sad to see you go"
  
  await channel.send(message)

#Reaction Add
@client.event
async def on_raw_reaction_add(payload):
  with open(f"Settings/{payload.guild_id}.json", "r") as f:
    settings = json.load(f)["Events"]["On Reaction"]
  
  if not settings:
    return

  if settings["Pinbot"]:
    await Pinbot.Pin(client, settings["Pinbot"], payload)
  
  if not settings["React for Role"] or payload.user_id == client.user.id:
    return

  if settings["React for Role"]["MessageID"] != payload.message_id:
    return

  guild = client.get_guild(payload.guild_id)
  member = await guild.fetch_member(payload.user_id)
  
  if not member:
    return Logger.Error("Member Not Found in on_raw_reaction_add")

  role = None
  for r in settings["React for Role"]["Roles"]:
    if payload.emoji.name == r["Emoji"]:
      role = guild.get_role(r["Role"])
      await member.add_roles(role)

  if not role:
    Logger.Error("Role not found in on_raw_reaction_add")

#Reaction Remove
@client.event
async def on_raw_reaction_remove(payload):
  with open(f"Settings/{payload.guild_id}.json", "r") as f:
    settings = json.load(f)["Events"]["On Reaction"]
  
  if not settings:
    return

  if settings["Pinbot"]:
    await Pinbot.Unpin(client, settings["Pinbot"], payload)
  
  if not settings["React for Role"]:
    return

  if not settings["React for Role"]["MessageID"] or payload.user_id == client.user.id:
    return

  guild = client.get_guild(payload.guild_id)
  channel = guild.get_channel(settings["React for Role"]["Channel"])
  message = await channel.fetch_message(settings["React for Role"]["MessageID"])
  
  if message.id != payload.message_id:
    return

  member = await guild.fetch_member(payload.user_id)
  if not member:
    return Logger.Error("Member Not Found in on_raw_reaction_remove")

  role = None
  for r in settings["React for Role"]["Roles"]:
    if payload.emoji.name == r["Emoji"]:
      role = guild.get_role(r["Role"])
      await member.remove_roles(role)
      break

  if not role:
    Logger.Error("Role not found in on_raw_reaction_remove")

#On Error
@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.ExtensionError):
    return
  
  embed = discord.Embed(
    title="An Error Occured", 
    colour=0x8f43f0, 
    description = error
  )
  
  embed.add_field(
    name="Error Type", 
    value= str(type(error)).replace("<class 'discord.ext.commands.", "").replace("'>", ""), inline=True
  )
  
  Logger.Error(error)
  await ctx.send(embed=embed)

@client.event
async def on_guild_join(guild):
  with open("Settings/default.json", "r") as f:
    default = json.load(f)

  with open(f"Settings/{guild.id}.json", "w") as f:
    json.dump(default, f, indent = 2)

#Start
Storage.Client = client
Awake.keep_alive()
client.run(Storage.BotKey)