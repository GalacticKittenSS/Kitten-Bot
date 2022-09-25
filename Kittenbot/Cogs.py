import discord
from discord.ext import commands

import Storage

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
    if not await CheckSettings(ctx, "Embed"):
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
    
    banned = await ctx.guild.bans()
    if len(banned) == 0:
      return await ctx.send("No Banned User Found")
      
    message = "Currently Banned Users:"
    for entry in banned:
      reason = entry.reason
      if reason == None:
        reason = "Unknown"
    
      message += "\n> User: " + entry.user.mention + "#" + entry.user.discriminator + ", Reason: `" + reason + "`"
    
    await ctx.reply(content=message)

  #-------------------------Settings-------------------------
  def ToggleCommandSettings(self, guild_id, command_name):
    with open(f"Settings/{guild_id}.json", "r") as f:
      settings = json.load(f)
    
    value = not bool(settings["Commands"][command_name])
    
    if value and command_name == "Who":
      value = {}
      value["Colour"] = 0
      value["Account Created"] = True
      value["Joined Server"] = True
      value["Roles"] = True
      value["Perms"] = True
      value["Excluded Perms"] = [
        "create_instant_invite", "add_reactions", "stream",
        "read_messages", "send_messages", "read_message_history",
        "embed_links", "attach_files",
        "mention_everyone", "external_emojis", "change_nickname", 
        "speak", "use_voice_activation", "connect", "request_to_speak"
      ]
    elif value and command_name == "Embed":
      settings = {}
      settings["Author"] = True
      settings["Timestamp"] = True

    settings["Commands"][command_name] = value

    with open(f"Settings/{guild_id}.json", "w") as f:
      json.dump(settings, f, indent=2)
    
    return bool(value)

  async def SetCommandSettings(self, ctx, command_name, value):
      with open(f"Settings/{ctx.guild.id}.json", "r") as f:
        settings = json.load(f)
      
      settings["Commands"][command_name] = value
      
      with open(f"Settings/{ctx.guild.id}.json", "w") as f:
        json.dump(settings, f, indent=2)
      
      await ctx.reply(f"Changed Settings for {command_name} to {value}") 

  @commands.hybrid_group(help = "Settings for this guild")
  @commands.has_permissions(administrator=True)
  async def settings(self, ctx):
    if ctx.invoked_subcommand is None:
      return await ctx.reply('Invalid Command. Please use `!help Settings` for available commands')
  
  @settings.command(help="Enable/Disable a Command")
  async def toggle(self, ctx, command : str):
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
    
    await self.SetCommandSettings(ctx, "Who", settings)

  @settings.command(help="Adjust Settings for Command Embed")
  async def embed(self, ctx, enabled : bool, author : bool = True, timestamp : bool = True):
    settings = enabled
    if enabled:
      settings = {}
      settings["Author"] = author
      settings["Timestamp"] = timestamp

    await self.SetCommandSettings(ctx, "Embed", settings)
