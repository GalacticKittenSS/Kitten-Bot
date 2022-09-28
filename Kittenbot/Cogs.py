import discord
from discord.ext import commands

import Storage
import Logger

import datetime
import calendar
import json

async def CheckSettings(ctx, command_name):
  with open(f"Settings/{ctx.guild.id}.json", "r") as f:
    settings = json.load(f)
  
  if not settings["Commands"][command_name]:
    await ctx.reply("This Command is Disabled")

  return settings["Commands"][command_name]

#-------------------------COMMANDS-------------------------
class Commands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command(help="Ping Me!")
  async def ping(self, ctx):
    if await CheckSettings(ctx, "Ping"):
      await ctx.send(f"Pong: {round(Storage.Client.latency * 1000)}ms")
  
  @commands.hybrid_command(help="Whats Todays Date?")
  async def date(self, ctx):
    if not await CheckSettings(ctx, "Date"):
      return
    
    dt = datetime.datetime.today()
    year = dt.year
    month = calendar.month_name[dt.month]
    day = dt.day
    
    await ctx.send(f"Are you really that lazy? \n\nFine...The date is {month} {day} {year}")
  
  #Shows Information about a User
  @commands.hybrid_command(help="Get member information", aliases=["whois"])
  async def who(self, ctx, user: discord.Member):
    settings = await CheckSettings(ctx, "Who")
    if not settings:
      return
    
    if not settings["Colour"]:
        settings["Colour"] = 0x8f43f0
    
    embed = discord.Embed(
      title=f"Who is {user.name}?", 
      colour=discord.Colour(settings["Colour"]),
      description=user.mention, 
      timestamp=datetime.datetime.now()
    ) 
    
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

    weekDays = ("Mon","Tues","Wed","Thur","Fri","Sat","Sun")
    
    if (settings["Account Created"]):
      embed.add_field(name= "Account Created:", value= f"{weekDays[user.created_at.date().weekday()]}, {user.created_at.day} {user.created_at.date().strftime('%b')}, {user.created_at.year} \n {user.created_at.strftime('%H:%M')} ", inline=True)
    
    if (settings["Joined Server"]):
      embed.add_field(name="Joined Server:", value=f"{weekDays[user.joined_at.date().weekday()]}, {user.joined_at.day} {user.joined_at.date().strftime('%b')}, {user.joined_at.year} \n {user.joined_at.strftime('%H:%M')} ", inline=True)
    
    if (settings["Roles"]):
      role_list = []
      roles= " "
    
      for role in user.roles:
        role_list.append(role.mention)
    
      role_list.pop(0)
      role_list.reverse()
      roles =  " ".join(role_list)  
      embed.add_field(name=f"Roles [{len(role_list)}]", value= roles, inline=False)

    if (settings["Perms"]):
      perm_list = []
      permissions = "" 
      excluded_perms = settings["Excluded Perms"]

      for value in user.guild_permissions:
        if value[1] and value[0] not in excluded_perms:
          perm_list.append(value[0])
    
      if len(perm_list) > 0:
        permissions =  ", ".join(perm_list).replace("_", " ").title()
        embed.add_field(name=f"Additional Permissions [{len(perm_list)}]", value= permissions, inline=False)

    embed.set_footer(text='ID: ' + str(user.id))
    await ctx.send(embed=embed)

  @commands.hybrid_command(help="Send Something in an embed!")
  async def embed(self, ctx, message, title, description = None, colour = 0x8f43f0, image = None, thumbnail = None):
    settings = await CheckSettings(ctx, "Embed")
    if not settings:
      return
      
    if not description:
      description = discord.Embed.Empty
    
    timestamp = discord.Embed.Empty
    if settings["Timestamp"]:
      timestamp = datetime.datetime.now()
    
    embed = discord.Embed(
      title=title, 
      colour=discord.Colour(colour), 
      description=description,
      timestamp=timestamp
    )
    
    if settings["Author"]:
      embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    
    if image:
      embed.set_image(url=image)
    if thumbnail:
      embed.set_thumbnail(url=thumbnail)

    await ctx.send(content=message, embed=embed)

#-------------------------Moderation-------------------------
class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command(help="Gives/Removes a role")
  @commands.has_permissions(manage_roles=True)
  async def role(self, ctx, user: commands.MemberConverter, role: commands.RoleConverter):
    if not await CheckSettings(ctx, "Role"):
      return
    
    context = "add"
    for value in user.roles:
      if value == role:
        context = "remove"
        
    if context == "add":
      await user.add_roles(role)
      await ctx.send(f"{user.mention} has acquired {role.mention} by {ctx.author.mention}")
    
    elif context == "remove":
      await user.remove_roles(role)
      await ctx.send(f"{user.mention} has lost {role.mention} by {ctx.author.mention}")

  @commands.hybrid_command(help="Deletes an amount of messages")
  @commands.has_permissions(manage_messages=True)
  async def clear(self, ctx, amount=5):
    if not await CheckSettings(ctx, "Clear"):
      return
      
    await ctx.defer(ephemeral=True)
    await ctx.channel.purge(limit=amount)
    await ctx.reply(f"Cleared {amount} messages", ephemeral=True)

  @commands.hybrid_command(help="Deletes messages from user", aliases=["ClearFromUser" "cUser"])
  @commands.has_permissions(manage_messages=True)
  async def clearuser(self, ctx, user: commands.MemberConverter, *, amount=5):
    if not await CheckSettings(ctx, "ClearUser"):
      return
    
    async for message in ctx.history(limit=amount):
      if message.author == user:
        await message.delete()
        
    await ctx.reply(f"Cleared messages from {user.mention} in last {amount}", ephemeral=True)
    
  @commands.hybrid_command(help="Kicks a Member")
  @commands.has_permissions(kick_members=True)
  async def kick(self, ctx, user: discord.Member, *, reason=None):
    if not await CheckSettings(ctx, "Kick"):
      return
    
    if user == ctx.author:
      await ctx.send("You can't kick yourself, silly!")
      return
      
    await user.kick(reason=reason)
    
    if reason == None:
      reason = "Unknown"
    
    await ctx.reply(f"Kicked: {user.mention} for {reason}")
  
  @commands.hybrid_command(help="Bans a Member")
  @commands.has_permissions(ban_members=True)
  async def ban(self, ctx, user: discord.Member, *, reason=None):
    if not await CheckSettings(ctx, "Ban"):
      return
      
    if user == ctx.author:
      await ctx.reply("You can't ban yourself, silly!")
      return
    
    await user.ban(reason=reason)
    
    if reason == None:
      reason = "Unknown"
      
    await ctx.reply(f"Banned: {user.mention} for {reason}")
  
  @commands.hybrid_command(help="Unbans a User")
  @commands.has_permissions(ban_members=True)
  async def unban(self, ctx, user):
    if not await CheckSettings(ctx, "Unban"):
      return
      
    banned = await ctx.guild.bans()
  
    name, discriminator = user.split('#')
    for entry in banned:
      user = entry.user
      
      if (user.name, user.discriminator) == (name, discriminator):
        await ctx.guild.unban(user)
        await ctx.reply(f"Unbanned: {user.mention}")
        break
  
  @commands.hybrid_command(help="Gets Ban List")
  @commands.has_permissions(ban_members=True)
  async def banned(self, ctx):
    if not await CheckSettings(ctx, "Banned"):
      return
    
    message, number = "", 0
    async for entry in ctx.guild.bans(limit=150):
      reason = entry.reason
      if reason is None:
        reason = "Unknown"

      number += 1
      message += f"\n> User: {entry.user.mention}#{entry.user.discriminator}, Reason: `{reason}`"
      
    await ctx.reply(f"Found {number} Banned Users\n{message}")

  #-------------------------Settings-------------------------
  def ToggleCommandSettings(self, guild_id, command_name):
    with open(f"Settings/{guild_id}.json", "r") as f:
      settings = json.load(f)
    
    value = not bool(settings["Commands"][command_name])
    
    if value and command_name == "Who":
      value = {
        "Colour": 0,
        "Account Created": True, "Joined Server": True,
        "Roles": True, "Perms": True,
        "Excluded Perms": [
          "create_instant_invite", "add_reactions", "stream",
          "read_messages", "send_messages", "read_message_history",
          "embed_links", "attach_files",
          "mention_everyone", "external_emojis", "change_nickname", 
          "speak", "use_voice_activation", "connect", "request_to_speak"
        ]
      }
    elif value and command_name == "Embed":
      value = { "Author" : True, "Timestamp" : True}
    
    settings["Commands"][command_name] = value

    with open(f"Settings/{guild_id}.json", "w") as f:
      json.dump(settings, f, indent=2)
    
    return bool(value)

  async def ChangeCommandSettings(self, ctx, command_name, value):
      with open(f"Settings/{ctx.guild.id}.json", "r") as f:
        settings = json.load(f)
      
      settings["Commands"][command_name] = value
      
      with open(f"Settings/{ctx.guild.id}.json", "w") as f:
        json.dump(settings, f, indent=2)
      
      await ctx.reply(f"Changed Settings for {command_name} to {value}") 
    
  async def ChangeReactionSettings(self, ctx, category, value):
      with open(f"Settings/{ctx.guild.id}.json", "r") as f:
        settings = json.load(f)
      
      settings["Events"]["On Reaction"][category] = value
      
      with open(f"Settings/{ctx.guild.id}.json", "w") as f:
        json.dump(settings, f, indent=2)
      
      await ctx.reply(f"Changed Settings for {category} to {value}") 
  
  async def ChangeEventSettings(self, ctx, category, value):
      with open(f"Settings/{ctx.guild.id}.json", "r") as f:
        settings = json.load(f)
      
      settings["Events"][category] = value
      
      with open(f"Settings/{ctx.guild.id}.json", "w") as f:
        json.dump(settings, f, indent=2)
      
      await ctx.reply(f"Changed Settings for {category} to {value}") 

  @commands.hybrid_group(help = "Settings for this guild")
  @commands.has_permissions(administrator=True)
  async def settings(self, ctx):
    if ctx.invoked_subcommand is None:
      return await ctx.reply('Invalid Command. Please use `!help Settings` for available commands')
  
  @settings.command(help="Enable/Disable a Command")
  async def toggle_command(self, ctx, command : str):
    try:
      command = command.capitalize()
      enabled = self.ToggleCommandSettings(ctx.guild.id, command)
      await ctx.reply(f"{['Disabled', 'Enabled'][int(enabled)]} command {command}")
    except KeyError:
      await ctx.reply(f"Command with name {command} not found")

  @settings.command(help="Adjust Settings for Command Who")
  async def who(self, ctx, enabled : bool, colour : int = 0, 
    account_created : bool = True, joined_server: bool = True,
    roles: bool = True, perms: bool = True):
    settings = enabled
    if enabled:
      settings = {}
      settings["Colour"] = colour
      settings["Account Created"] = account_created
      settings["Joined Server"] = joined_server
      settings["Roles"] = roles
      settings["Perms"] = perms
      settings["Excluded Perms"] = [
        "create_instant_invite", "add_reactions", "stream",
        "read_messages", "send_messages", "read_message_history",
        "embed_links", "attach_files",
        "mention_everyone", "external_emojis", "change_nickname", 
        "speak", "use_voice_activation", "connect", "request_to_speak"
      ]
    
    await self.ChangeCommandSettings(ctx, "Who", settings)

  @settings.command(help="Adjust Settings for Command Embed")
  async def embed(self, ctx, enabled : bool, author : bool = True, timestamp : bool = True):
    settings = enabled
    if enabled:
      settings = {}
      settings["Author"] = author
      settings["Timestamp"] = timestamp

    await self.ChangeCommandSettings(ctx, "Embed", settings)

  @settings.command(help="Adjust Pinbot Settings")
  async def pinbot(self, ctx, enabled : bool, 
    emoji : str ="\ud83d\udccc", pins_needed : int = 5,
    pin_to_channel : bool = True, repost_channel : discord.TextChannel = None):
    settings = enabled
    if enabled:
      settings = {}
      settings["Emoji"] = emoji
      settings["Pins Needed"] = pins_needed
      settings["Pin to Channel"] = pin_to_channel
      if not repost_channel:
        settings["Repost"] = 0
      else:
        settings["Repost"] = repost_channel.id
      
    await self.ChangeReactionSettings(ctx, "Pinbot", settings)

  async def EditReactForRole(self, ctx, settings):
    channel = Storage.Client.get_channel(settings["Channel"])
    embed = discord.Embed(
      title=settings["Title"],
      colour=discord.Colour(settings["Colour"]), 
      description=settings["Description"]
    )
    
    for role in settings["Roles"]:
      embed.add_field(name=ctx.guild.get_role(role["Role"]).name + " " + role["Emoji"], value=role["Message"], inline=True)
    
    try:
      message = await channel.fetch_message(settings["MessageID"])
      await message.edit(content=settings["Message"], embed=embed)
    except discord.errors.NotFound:
      message = await channel.send(content=settings["Message"], embed=embed)
      settings["MessageID"] = message.id

    for role in settings["Roles"]:
      await message.add_reaction(role["Emoji"])

  @settings.command(help="Adjust React for Role Settings")
  async def react_for_role(self, ctx, enabled : bool,  channel : discord.TextChannel,
    message : str = "", title : str = "", description : str = "", 
    colour : int = 9389040):
    settings = enabled
    if enabled:
      with open(f"Settings/{ctx.guild.id}.json", "r") as f:
        settings = json.load(f)["Events"]["On Reaction"]["React for Role"]
        if not settings:
          settings = {}
      
      settings["Channel"] = channel.id
      settings["Title"] = title
      settings["Description"] = description
      settings["Message"] = message
      settings["Colour"] = colour
      if not colour:
        settings["Colour"] = 0x8f43f0

      await self.EditReactForRole(ctx, settings)
      
    await self.ChangeReactionSettings(ctx, "React for Role", settings)
  
  @settings.command(help="Add Role from React for Role")
  async def add_react_role(self, ctx, role : discord.Role, emoji : str, message : str):
    roleSettings = {}
    roleSettings["Role"] = role.id
    roleSettings["Emoji"] = emoji
    roleSettings["Message"] = message

    with open(f"Settings/{ctx.guild.id}.json", "r") as f:
      settings = json.load(f)["Events"]["On Reaction"]["React for Role"]
    
    settings["Roles"].append(roleSettings)
    await self.EditReactForRole(ctx, settings)
    await self.ChangeReactionSettings(ctx, "React for Role", settings)

  @settings.command(help="Remove Role from React for Role")
  async def remove_react_role(self, ctx, role : discord.Role):
    with open(f"Settings/{ctx.guild.id}.json", "r") as f:
      settings = json.load(f)["Events"]["On Reaction"]["React for Role"]
    
    roleSettings = []
    for r in settings["Roles"]:
      if r["Role"] == role.id:
        try:
          channel = Storage.Client.get_channel(settings["Channel"])
          message = await channel.fetch_message(settings["MessageID"])
          await message.clear_reaction(r["Emoji"])
        except:
          Logger.Error("Unable to Remove Reaction")
        continue
      roleSettings.append(r)
    settings["Roles"] = roleSettings
    
    await self.EditReactForRole(ctx, settings)
    await self.ChangeReactionSettings(ctx, "React for Role", settings)
  
  @settings.command(help="Remove Role from React for Role")
  async def change(self, ctx, prefix, roles):
    with open(f"Settings/{ctx.guild.id}.json", "r") as f:
      settings = json.load(f)

    roles = roles.split(", ")
    settings["Prefix"] = prefix
    settings["Moderator Roles"] = roles
    
    with open(f"Settings/{ctx.guild.id}.json", "w") as f:
      json.dump(settings, f, indent=2)

    await ctx.reply(f"Changed Prefix to {prefix} and Roles to {roles}")
  
  @settings.command(help="Change Settings for Member Join")
  async def member_join(self, ctx, enabled : bool, channel : discord.TextChannel = None, roles : str = ""):
    roles = roles.split(", ")
    
    settings = enabled
    if enabled:
      settings = {}
      settings["Roles"] = roles
      settings["Channel"] = 0
      if channel:
        settings["Channel"] = channel.id
      
    await self.ChangeEventSettings(ctx, "Member Join", settings)

  @settings.command(help="Change Settings for Member Leave")
  async def member_leave(self, ctx, enabled : bool, channel : discord.TextChannel = None):
    settings = enabled
    if enabled:
      settings = {}
      settings["Channel"] = 0
      if channel:
        settings["Channel"] = channel.id

    await self.ChangeEventSettings(ctx, "Member Leave", settings)
