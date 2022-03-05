async def Ping(client, settings, ctx):
  await ctx.send(f"Pong: {round(client.latency * 1000)}ms")

import datetime
import calendar

async def Date(client, settings, ctx):
  dt = datetime.datetime.today()
  year = dt.year
  month = calendar.month_name[dt.month]
  day = dt.day
  
  await ctx.send(f"Are you really that lazy...? \n\n Fine, The date is {month} {day} {year}")

import discord

async def Who(client, settings, ctx, user):
  if user == None:
      user = ctx.author
    
  if not settings["Colour"]:
      settings["Colour"] = 0x8f43f0  
  
  embed = discord.Embed(
    title=f"Who is {user.name}?", 
    colour=discord.Colour(settings["Colour"]),
    description=user.mention, 
    timestamp=datetime.datetime.now()
  ) 
  
  embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(user))
  embed.set_author(name=ctx.author.name, icon_url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(ctx.author))

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

async def Say(client, settings, ctx, text):
  for word in settings["Blacklist"]:
    if settings["Symbol"]:
      replacement = settings["Symbol"] * len(word)
    else:
      replacement = settings["Replacement"]
      
    text = text.replace(word, replacement)
  await ctx.send(text)

async def Embed(client, settings, ctx, message, title, description, colour, image, thumbnail):
  if not colour:
    colour = 0x8f43f0

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
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
  
  if image:
    embed.set_image(url=image)
  if thumbnail:
    embed.set_thumbnail(url=thumbnail)

  await ctx.send(content=message, embed=embed)