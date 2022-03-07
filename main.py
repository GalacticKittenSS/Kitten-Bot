import discord
from discord.ext import commands

import Kittenbot.Cogs

import os
import awake
import json

def guild_prefix(client, message):
   settings = json.load(open(f"Settings/{message.guild.id}.json", 'r'))
   return settings["Prefix"]
  
#Client
client = commands.Bot(command_prefix=guild_prefix, intents=discord.Intents.all())

#On Ready
@client.event
async def on_ready():
  await Kittenbot.BotEvents.OnReady(client)

#Join
@client.event
async def on_member_join(member):
  settings = json.load(open(f"Settings/{member.guild.id}.json", "r"))["Events"]["Member Join"]
  if (settings):
    await Kittenbot.BotEvents.Join(client, settings, member)

#Leave
@client.event
async def on_member_remove(member):
  settings = json.load(open(f"Settings/{member.guild.id}.json", "r"))["Events"]["Member Leave"]
  if (settings):
    await Kittenbot.BotEvents.Leave(client, settings, member)

#Reaction Add
@client.event
async def on_raw_reaction_add(payload):
  settings = json.load(open(f"Settings/{payload.guild_id}.json", "r"))["Events"]["On Reaction"]
  if (settings):
    await Kittenbot.BotEvents.OnReaction(client, settings, payload)

#Reaction Remove
@client.event
async def on_raw_reaction_remove(payload):
  settings = json.load(open(f"Settings/{payload.guild_id}.json", "r"))["Events"]["On Reaction"]
  if (settings):
    await Kittenbot.BotEvents.OnReactionRemove(client, settings, payload)

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
  
  await ctx.send(embed=embed)

@client.event
async def on_guild_join(guild):
  default = json.load(open("Settings/default.json", "r"))
  json.dump(default, open(f"Settings/{guild.id}.json", "w"), indent = 2)

#Start
awake.keep_alive()
client.add_cog(Kittenbot.Cogs.Commands(client))
client.add_cog(Kittenbot.Cogs.Moderation(client))
client.run(os.getenv("Bot Key"))