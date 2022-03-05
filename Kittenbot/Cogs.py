import discord
from discord.ext import commands

import Kittenbot.BotEvents
import Kittenbot.Event
import Kittenbot.Commands
import Kittenbot.Moderation
import Kittenbot.Utils

import json

#-------------------------COMMANDS-------------------------

class Commands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(help="Ping Me!")
  async def ping(self, ctx):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Ping"]):
      await Kittenbot.Commands.Ping(self.bot, settings["Commands"]["Ping"], ctx)
      
      if (settings["Delete Message"]):
        await ctx.message.delete()
  
  @commands.command(help="Whats Todays Date?")
  async def date(self, ctx):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Date"]):
      await Kittenbot.Commands.Date(self.bot, settings["Commands"]["Date"], ctx)
      
      if (settings["Delete Message"]):
        await ctx.message.delete()
  
  #Shows Information about a User
  @commands.command(help="Get member information", aliases=["whois"])
  async def who(self, ctx, *, user: commands.MemberConverter=None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Who"]):
      await Kittenbot.Commands.Who(self.bot, settings["Commands"]["Who"], ctx, user)
      
      if (settings["Delete Message"]):
        await ctx.message.delete()
  
  @commands.command(help="Make me say Something")
  async def say(self, ctx, text):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Say"]):
      await Kittenbot.Commands.Say(self.bot, settings["Commands"]["Say"], ctx, text)
      
      if (settings["Delete Message"]):
        await ctx.message.delete()

  @commands.command(help="Send Something in an embed!")
  async def embed(self, ctx, message, title, description = None, colour = 0x8f43f0, image = None, thumbnail = None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Say"]):
      await Kittenbot.Commands.Embed(
        self.bot, settings["Commands"]["Embed"], ctx, 
        message, title, description, colour, image, thumbnail
      )
      
      if (settings["Delete Message"]):
        await ctx.message.delete()
        
  @commands.group()
  async def event(self, ctx):
    if ctx.invoked_subcommand is None:
      return await ctx.send('Invalid Command. Please use `!help event` for available commands')

    found = False
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    for role in ctx.author.roles:
      if role.name in settings["Moderator Roles"]:
        found = True
        continue

    if not found:
      raise commands.MissingAnyRole(settings["Moderator Roles"])

    if json.load(open(f"Settings/{ctx.guild.id}.json", "r"))["Custom Events"] == False:
      raise commands.DisabledCommand("Custom Events are disabled on this server")
  
  @event.command(help="Create an event at index")
  async def create(self, ctx, Name, colour = 0, *, description=None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Custom Events"] = await Kittenbot.Event.Create(self.bot, settings["Custom Events"], ctx, Name, colour, description)
      
    if (settings["Delete Message"]):
      await ctx.message.delete()
  
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
  @event.command(help= "Start an event at index")
  async def start(self, ctx, index, winners, role : commands.RoleConverter = None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    await Kittenbot.Event.Start(self.bot, settings["Custom Events"], ctx, index, winners, role)
      
    if (settings["Delete Message"]):
      await ctx.message.delete()
  
  @event.command(help= "Delete an event at Index")
  @commands.has_role('Moderators')
  async def delete(self, ctx, index):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Custom Events"] = await Kittenbot.Event.Delete(self.bot, settings["Custom Events"], ctx, index)
      
    if (settings["Delete Message"]):
      await ctx.message.delete()
  
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)

#-------------------------Moderation-------------------------

class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(help="Gives/Removes a role")
  @commands.has_permissions(manage_roles=True)
  async def role(self, ctx, user: commands.MemberConverter, role: commands.RoleConverter):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Role"]):
      await Kittenbot.Moderation.Role(self.bot, settings["Commands"]["Role"], ctx, user, role)
      
      if (settings["Delete Message"]):
        await ctx.message.delete()

  @commands.command(help="Deletes an amount of messages")
  @commands.has_permissions(manage_messages=True)
  async def clear(self, ctx, amount=5):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Clear"]):
      await Kittenbot.Moderation.Clear(self.bot, settings["Commands"]["Clear"], ctx, amount)
  
  @commands.command(help="Deletes messages from user", aliases=["ClearFromUser" "cUser"])
  @commands.has_permissions(manage_messages=True)
  async def clearUser(self, ctx, user: commands.MemberConverter, *, amount=5):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["ClearUser"]):
      await Kittenbot.Moderation.ClearFromUser(self.bot, settings["Commands"]["ClearUser"], ctx, user, amount)
  
  @commands.command(help="Kicks a Member")
  @commands.has_permissions(kick_members=True)
  async def kick(self, ctx, user: discord.Member, *, reason=None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Kick"]):
      await Kittenbot.Moderation.Kick(self.bot, settings["Commands"]["Kick"], ctx, user, reason)
      
      if (settings["Delete Message"]):
        await ctx.message.delete()
  
  @commands.command(help="Bans a Member")
  @commands.has_permissions(ban_members=True)
  async def ban(self, ctx, user: discord.Member, *, reason=None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Ban"]):
      await Kittenbot.Moderation.Ban(self.bot, settings["Commands"]["Ban"], ctx, user, reason)
      
      if (settings["Delete Message"]):
        await ctx.message.delete()
  
  @commands.command(help="Unbans a User")
  async def unban(self, ctx, user):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Unban"]):
      await Kittenbot.Moderation.Unban(self.bot, settings["Commands"]["Unban"], ctx, user)
      
      if (settings["Delete Message"]):
        await ctx.message.delete()
  
  @commands.command(help="Gets Ban List")
  async def banned(self, ctx):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if (settings["Commands"]["Banned"]):
      await Kittenbot.Moderation.GetBanList(self.bot, settings["Commands"]["Banned"], ctx)
      
      if (settings["Delete Message"]):
        await ctx.message.delete()
  
  @commands.command(help="Resets Bot")
  async def reset(self, ctx):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    await Kittenbot.BotEvents.Reset(self.bot, ctx.guild)
    
    if (settings["Delete Message"]):
      await ctx.message.delete()

  #----------------------------Settings----------------------------
  @commands.group(help = "Settings for this guild")
  @commands.has_permissions(administrator=True)
  async def Settings(self, ctx):
    if ctx.invoked_subcommand is None:
      return await ctx.send('Invalid Command. Please use `!help Settings` for available commands')
      
  @Settings.command()
  async def Prefix(self, ctx, prefix):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Prefix"] = prefix
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2 )
    
    if (settings["Delete Message"]):
      await ctx.message.delete()
  
  @Settings.command(help="Sets the Moderator Roles")
  async def Moderator_Roles(self, ctx, *, new):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if new:
      settings["Moderator Roles"] = new.split(" ")
    else:
      settings["Moderator Roles"] = []
      
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    if (settings["Delete Message"]):
      await ctx.message.delete()
      
  @Settings.group(help="Sets Events Settings")
  async def Events(self, ctx):
    if ctx.invoked_subcommand is None:
      return await ctx.send('Invalid Command. Please use `!help Events` for available commands')

  @Events.command(help="Sets ")
  async def Join(self, ctx, command_enabled : bool, channel : int = None, *, roles = None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    
    if command_enabled:
      settings["Events"]["Member Join"] = {}
      settings["Events"]["Member Join"]["Channel"] = channel
      if roles:
        settings["Events"]["Member Join"]["Roles"] = roles.split(" ")
      else:
        settings["Events"]["Member Join"]["Roles"] = []
    else:
      settings["Events"]["Member Join"] = False
      
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Events.command(help="Sets ")
  async def Custom(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    
    if command_enabled:
      settings["Custom Events"] = []
    else:
      settings["Custom Events"] = False
    
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Events.command(help="Sets ")
  async def Leave(self, ctx, command_enabled : bool, channel : int = None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    
    if command_enabled:
      settings["Events"]["Member Leave"] = {}
      settings["Events"]["Member Leave"]["Channel"] = channel
    else:
      settings["Events"]["Member Leave"] = False
    
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Events.command(help="Sets ")
  async def Pins(
    self, ctx, 
    command_enabled : bool, emoji = "", pins_needed : int = 5, 
    pin_to_channel : bool = False, repost : int = 0):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))

    if command_enabled:
      settings["Events"]["On Reaction"]["Pinbot"] = {}
      settings["Events"]["On Reaction"]["Pinbot"]["Emoji"] = emoji
      settings["Events"]["On Reaction"]["Pinbot"]["Pins Needed"] = pins_needed
      settings["Events"]["On Reaction"]["Pinbot"]["Pin to Channel"] = pin_to_channel
      settings["Events"]["On Reaction"]["Pinbot"]["Repost"] = repost
    else:
      settings["Events"]["On Reaction"]["Pinbot"] = False
    
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Events.command(help="Sets ")
  async def React_for_Role(
    self, ctx, command_enabled : bool,
    channel : int = 0, title = "", description = "", message = "", colour : int = 0):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))

    if command_enabled:
      if not settings["Events"]["On Reaction"]["React for Role"]:
        settings["Events"]["On Reaction"]["React for Role"] = {}
        
      settings["Events"]["On Reaction"]["React for Role"]["Channel"] = channel
      settings["Events"]["On Reaction"]["React for Role"]["Title"] = title
      settings["Events"]["On Reaction"]["React for Role"]["Description"] = description
      settings["Events"]["On Reaction"]["React for Role"]["Message"] = message
      settings["Events"]["On Reaction"]["React for Role"]["Colour"] = colour
    else:
      settings["Events"]["On Reaction"]["React for Role"] = False
    
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    if (settings["Delete Message"]):
      await ctx.message.delete()
  
  @Events.command(help="Sets ")
  async def Add_React_for_Role(self, ctx, message, reaction, role : commands.RoleConverter):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
      
    new = {}
    new["Message"] = message
    new["Reaction"] = reaction
    new["Role"] = role.id
    settings["Events"]["On Reaction"]["React for Role"]["Roles"].append(new)
    
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    if (settings["Delete Message"]):
      await ctx.message.delete()
      
  @Events.command(help="Sets ")
  async def Remove_React_for_Role(self, ctx, id : int):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Events"]["On Reaction"]["React for Role"]["Roles"].pop(id)
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Events.command(help="Sets ")
  async def Stream_Alert(self, ctx, command_enabled : bool, 
    channel : commands.TextChannelConverter = None, message = "", 
    remove_when_offline : bool = True, *, users):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))

    if command_enabled:
      settings["Events"]["StreamAlert"] = {}
      settings["Events"]["StreamAlert"]["Channel"] = channel.id
      settings["Events"]["StreamAlert"]["Message"] = message
      settings["Events"]["StreamAlert"]["Remove Offline"] = remove_when_offline
      if users:
        settings["Events"]["StreamAlert"]["Users"] = users.split(" ")
      else:
        settings["Events"]["StreamAlert"]["Users"] = []
      
      settings["Events"]["StreamAlert"]["Colour"] = 0
      settings["Events"]["StreamAlert"]["Game"] = True
      settings["Events"]["StreamAlert"]["Viewers"] = True
      settings["Events"]["StreamAlert"]["Image"] = True
      settings["Events"]["StreamAlert"]["Description"] = True
      settings["Events"]["StreamAlert"]["Author"] = True
    else:
      settings["Events"]["StreamAlert"] = False
      
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Events.command(help="Sets ")
  async def Video_Alert(self, ctx, command_enabled : bool, 
    channel : commands.TextChannelConverter = None, message = "", *, ids):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))

    if command_enabled:
      settings["Events"]["VideoAlert"] = {}
      settings["Events"]["VideoAlert"]["Channel"] = channel.id
      settings["Events"]["VideoAlert"]["Message"] = message
      if ids:
        settings["Events"]["VideoAlert"]["Ids"] = ids.split(" ")
      else:
        settings["Events"]["VideoAlert"]["Ids"] = []
        
      settings["Events"]["VideoAlert"]["Colour"] = 0
      settings["Events"]["VideoAlert"]["Image"] = True
      settings["Events"]["VideoAlert"]["Description"] = True
      settings["Events"]["VideoAlert"]["Author"] = True
    else:
      settings["Events"]["VideoAlert"] = False
      
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Settings.command(help="Set Whether Command Messages Should be Deleted")
  async def Delete_Message(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Delete Message"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Settings.group(help="Sets Command Settings")
  async def Command(self, ctx):
    if ctx.invoked_subcommand is None:
      return await ctx.send('Invalid Command. Please use `!help Commands` for available commands')

  @Command.command(help="Sets !who Settings")
  async def Who(self, ctx, 
    command_enabled : bool, colour : int = 0, account_created : bool = 0, 
    joined_server : bool = 0, roles : bool = 0, perms : bool = 0, 
    *, excluded_perms = None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))

    if command_enabled:
      settings["Commands"]["Who"] = {}
      settings["Commands"]["Who"]["Colour"] = colour
      settings["Commands"]["Who"]["Account Created"] = account_created
      settings["Commands"]["Who"]["Joined Server"] = joined_server
      settings["Commands"]["Who"]["Roles"] = roles
      settings["Commands"]["Who"]["Perms"] = perms
      if excluded_perms == "default":
        settings["Commands"]["Who"]["Excluded Perms"] = [
          "create_instant_invite",
          "add_reactions",
          "stream",
          "read_messages",
          "send_messages",
          "embed_links",
          "attach_files",
          "read_message_history",
          "mention_everyone",
          "external_emojis",
          "connect",
          "speak",
          "use_voice_activation",
          "change_nickname",
          "request_to_speak"
        ]
      elif excluded_perms:
        settings["Commands"]["Who"]["Excluded Perms"] = excluded_perms.split(" ")
      else:
        settings["Commands"]["Who"]["Excluded Perms"] = []
    else:
      settings["Commands"]["Who"] = False
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !ping Settings")
  async def Ping(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Commands"]["Ping"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !date Settings")
  async def Date(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Commands"]["Date"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !say Settings")
  async def Say(
    self, ctx, command_enabled : bool, 
    symbol = None, replacement = None, *, blacklist = None):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if command_enabled:
      settings["Commands"]["Say"] = {}
      if symbol:
        settings["Commands"]["Say"]["Symbol"] = symbol
      if replacement:
        settings["Commands"]["Say"]["Replacement"] = replacement
      if blacklist:
        settings["Commands"]["Say"]["Blacklist"] = blacklist.split(" ")
      else:
        settings["Commands"]["Say"]["Blacklist"] = []
    else:
      settings["Commands"]["Say"] = False
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !embed Settings")
  async def Embed(self, ctx, command_enabled : bool, author : bool = True, timestamp : bool = True):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    if command_enabled:
      settings["Commands"]["Embed"] = {}
      settings["Commands"]["Embed"]["Author"] = author
      settings["Commands"]["Embed"]["Timestamp"] = timestamp
    else:
      settings["Commands"]["Embed"] = False
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !role Settings")
  async def Role(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Commands"]["Role"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !clear Settings")
  async def Clear(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Commands"]["Clear"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !clearUser Settings")
  async def ClearUser(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Commands"]["ClearUser"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !kick Settings")
  async def Kick(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Commands"]["Kick"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !ban Settings")
  async def Ban(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Commands"]["Ban"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !unban Settings")
  async def Unban(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Commands"]["Unban"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()

  @Command.command(help="Sets !banned Settings")
  async def Banned(self, ctx, command_enabled : bool):
    settings = json.load(open(f"Settings/{ctx.guild.id}.json", "r"))
    settings["Commands"]["Banned"] = command_enabled
    json.dump(settings, open(f"Settings/{ctx.guild.id}.json", "w"), indent = 2)
  
    if (settings["Delete Message"]):
      await ctx.message.delete()