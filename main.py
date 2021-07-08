import os
import datetime
import calendar
import random
import itertools
import discord
from discord.ext import commands
from awake import keep_alive
from streamalert import checkstream
import variable
from react import sortReact
from react import getRole

#CUSTOM HELP
class CustomHelp(commands.DefaultHelpCommand):
  def __init__(self, **options):
    self.paginator = options.pop('paginator', None)
    
    if self.paginator is None:
      self.paginator = commands.help.Paginator()
      
    super().__init__(**options)
    self.paginator.__init__("```", "```")
    
    
  def add_command_formatting(self, command):
    if command.description:
     self.paginator.add_line(command.description, empty=True)
     
    signature = get_command_signature(command)
    self.paginator.add_line(signature, empty=True)
     
    if command.help:
      try:
        self.paginator.add_line(command.help, empty=True)
      except RuntimeError:
        for line in command.help.splitlines():
          self.paginator.add_line(line)
        self.paginator.add_line()

    
  async def send_pages(self, channel = None, message = None, pages = False):
    try:
      destination = self.get_destination()

      for page in self.paginator.pages:
        variable.current_sorted_commands = page
        embed = discord.Embed(title="Help", description=page)
        message = await destination.send(embed=embed)
        variable.current_help_message.append(message)
        variable.current_help_commands.append(page)
        variable.current_help_index.append(-1)
      
        await message.add_reaction("⏮️")
        await message.add_reaction("⏭️")
    except:
      destination = client.get_channel(channel.id)
      if pages:
        page = variable.current_sorted_commands
        embed = discord.Embed(title="Help", description=page)
        await message.edit(embed=embed)

      for page in self.paginator.pages:
        embed = discord.Embed(title="Help", description=page)
        await message.edit(embed=embed)
          
  async def send_bot_help(self, mapping):
    sorted = await super().filter_commands(client.commands, sort=True)
    sorted = itertools.groupby(sorted)

    variable.current_help_commands = []

    for command, category in sorted:
      variable.current_help_commands.append(command)
    await super().send_bot_help(mapping)
  
  async def send_cog_help(self, cog):
    await super().send_cog_help(cog)
    
  async def send_group_help(self, group):
    await super().send_group_help(group)
    
  async def send_next_help(self, channel, message, page=False, command = None):
    if page:
      await self.send_pages(channel=channel, message=message, pages=True)
    else:
      self.add_command_formatting(command)
      self.paginator.close_page()
      await self.send_pages(channel=channel, message=message)


  async def send_command_help(self, command):
    self.add_command_formatting(command)
    self.paginator.close_page()
    await self.send_pages()

def get_command_signature(command):
	parent = command.parent
	entries = []
	while parent is not None:
		if not parent.signature or parent.invoke_without_command:
			entries.append(parent.name)
		else:
			entries.append(parent.name + ' ' + parent.signature)
		parent = parent.parent
	parent_sig = ' '.join(reversed(entries))

	if len(command.aliases) > 0:
		aliases = '|'.join(command.aliases)
		fmt = '[%s|%s]' % (command.name, aliases)
		if parent_sig:
			fmt = parent_sig + ' ' + fmt
		alias = fmt
	else:
		alias = command.name if not parent_sig else parent_sig + ' ' + command.name

	return '%s%s %s' % ("!", alias, command.signature)

#CLIENT
client = commands.Bot(command_prefix='!', help_command=CustomHelp(), intents=discord.Intents.all())

#JOIN AND LEAVE
@client.event
async def on_member_join(member):
	print(f"Member {member} Joined")

	channel = client.get_channel(variable.welcome_channels)
	message = f"Welcome {member.mention} to **{member.guild.name}**. We hope you enjoy! Be sure to read {client.get_channel(variable.rule_channel).mention} before heading to {client.get_channel(variable.react_channel).mention} to claim a role."
	role = discord.utils.get(member.guild.roles, id=variable.welcome_role)

	await channel.send(message)
	await member.add_roles(role)

@client.event
async def on_member_remove(member):
	print(f"Member {member} Left")

	channel = client.get_channel(variable.welcome_channel)
	message = f"{member.mention} has left **{member.guild.name}**. We're sad to see you go"

	await channel.send(message)

#ON CLIENT READY
@client.event
async def on_ready():
	print("We have logged in as {0.user}".format(client))

	await sortReact(client)

	await checkstream.start(client)

#REACTIONS
@client.event
async def on_raw_reaction_add(payload):
  count = -1
  for value in variable.current_help_message:
    channel = client.get_channel(value.channel.id) 
    count = count + 1
    async for message in channel.history(limit=200):
      if message == variable.current_help_message[count] and payload.user_id != 796667304816410675 and message.id== payload.message_id:
        index = variable.current_help_index[count]

        if payload.emoji.name == "⏭️":
          index = index + 1
          await message.remove_reaction("⏭️", client.get_user(payload.user_id))
        if payload.emoji.name == "⏮️":
          index = index - 1
          await message.remove_reaction("⏮️", client.get_user(payload.user_id))

        if index == len(variable.current_help_commands) and len(variable.current_help_commands) > 0:
          index = -len(variable.current_help_commands)
        elif index == -len(variable.current_help_commands) and len(variable.current_help_commands) > 0:
          index = len(variable.current_help_commands)
        
        variable.current_help_index[count]= index
        print(index)
        if index + 1 == len(variable.current_help_commands) or index == -1:
          cmd = variable.current_help_commands[index - 1]
          await CustomHelp().send_next_help(command=cmd, channel=channel, message= message, page=True)
        else:
          cmd = variable.current_help_commands[index]
          await CustomHelp().send_next_help(command=cmd, channel=channel, message= message)
      
  await getRole(client, payload, True)

@client.event
async def on_raw_reaction_remove(payload):
	await getRole(client, payload, False)

#COMMANDS
@client.event
async def on_command_error(ctx, error):
  await ctx.send(f"Error: {error}")
  print(error)
  if ctx.command != None: 
    sig = get_command_signature(ctx.command)
    await ctx.send(f"```{sig} \n \n{ctx.command.help}```")
  await ctx.message.delete()

@client.command(help="Bot Ping")
async def ping(ctx):
	await ctx.send(f"Ping: {round(client.latency * 1000)}ms")
	await ctx.message.delete()

@client.command(help="Todays date")
async def date(ctx):
	dt = datetime.datetime.today()
	year = dt.year
	month = calendar.month_name[dt.month]
	day = dt.day
	await ctx.send(f"The date is {month} {day} {year}")
	await ctx.message.delete()

@client.command(help="Gives a role to user")
@commands.has_permissions(manage_roles=True)
async def role(ctx, user: commands.MemberConverter, role: commands.RoleConverter):
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
    
  await ctx.message.delete()

@client.command(help="Deletes an amount of messages")
@commands.has_permissions(kick_members=True)
async def clear(ctx, amount=5):
	amount = amount + 1
	await ctx.channel.purge(limit=amount)

@client.command(help="Kicks a player")
@commands.has_permissions(manage_roles=True)
async def kick(ctx, user: discord.Member, *, reason=None):
	await ctx.message.delete()
	await user.kick(reason=reason)
	await ctx.send(f"{user.mention} was kicked by {ctx.author.mention}")
	
@client.command(help= "Create an event at index", aliases = ["createEvent"])
@commands.has_role('Moderator')
async def eCreate(ctx, Name, *, description=None):
  Index = 0

  while variable.Event_Message_Id[Index] != None:
    Index = Index + 1

  if len(variable.Event_Message_Id) > Index + 1:
    if variable.Event_Message_Id[Index] == None:
      variable.Event_Message_Id.pop(Index)

  if description == None:
    description = "No description available"

  Embed = discord.Embed(title=Name,description=description)
  Embed.set_footer(text="Event stored at Index {Index}")

  message = await ctx.send(content="New Event!", embed=Embed) 
  variable.Event_Message_Id.insert(Index, message.id)
  
  await ctx.message.delete()
	
@client.command(help="Start an event at index", aliases=["startEvent"])
@commands.has_role('Moderator')
async def eStart(ctx, Index: int, *, winners: int = 5 , role : commands.RoleConverter = None):
  message = await ctx.fetch_message(variable.Event_Message_Id[Index])
  users = []
  for reaction in message.reactions:
      async for user in reaction.users():
          users.append(user)

  count = 0
  safetyNet = 0
  all_winners = ["None"]
  while count < winners and safetyNet < 200:
    winner = random.choice(users)
    isAlreadyInArray = False
    for value in all_winners:
      if winner == value:
        isAlreadyInArray = True

    
    if isAlreadyInArray != True:
      if role != None:
        await winner.add_roles(role)
      await ctx.send(f'{winner.mention} has been selected for the event')
      all_winners.append(winner)
      count = count + 1
    else:
      safetyNet = safetyNet + 1

  await ctx.message.delete()

@client.command(help= "Delete an event at Index", aliases=["deleteEvent"])
@commands.has_role("Moderator")
async def eDelete(ctx, Index : int):
  async for message in ctx.history(limit=200):
    if message.id == variable.Event_Message_Id[Index]:
      await message.delete()
    
  variable.Event_Message_Id[Index] = None
  await ctx.message.delete()

@client.command(help="Get member information", aliases=["whois"])
async def who(ctx, *, user: commands.MemberConverter=None):
  if user == None:
    user = ctx.author
  
  embed = discord.Embed(title=f"Who is {user.name}?", description=user.mention, timestamp=datetime.datetime.now())  
  

  embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(user))
  

  embed.set_author(name=ctx.author.name, icon_url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(ctx.author))
  

  weekDays = ("Mon","Tues","Wed","Thur","Fri","Sat","Sun")
  
  embed.add_field(name= "Account Created:", value= f"{weekDays[user.created_at.date().weekday()]}, {user.created_at.day} {user.created_at.date().strftime('%b')}, {user.created_at.year} \n {user.created_at.strftime('%H:%M')} ", inline=True)

  
  embed.add_field(name="Joined Server:", value=f"{weekDays[user.joined_at.date().weekday()]}, {user.joined_at.day} {user.joined_at.date().strftime('%b')}, {user.joined_at.year} \n {user.joined_at.strftime('%H:%M')} ", inline=True)
  
  
  role_list = []
  roles= " "

  for role in user.roles:
    role_list.append(role.mention)

  role_list.pop(0)
  role_list.reverse()
  roles =  " ".join(role_list)  
  embed.add_field(name=f"Roles [{len(role_list)}]", value= roles, inline=False)


  perm_list = []
  permissions = " "
  excluded_perms = ["create_instant_invite", "add_reactions", "stream","read_messages", "send_messages", "embed_links", "attach_files","read_message_history", "mention_everyone", "external_emojis", "connect", "speak", "use_voice_activation", "change_nickname"]


  for value in user.guild_permissions:
    if value[1] and value[0] not in excluded_perms:
      perm_list.append(value[0])

  if len(perm_list) > 0:
    permissions =  ", ".join(perm_list).replace("_", " ").title()
    embed.add_field(name=f"Additional Permissions [{len(perm_list)}]", value= permissions, inline=False)

  embed.set_footer(text='ID: ' + str(user.id))
  
  await ctx.send(embed=embed)
  
  await ctx.message.delete()
  
@client.command(help="Deletes messages from user", aliases=["ClearFromUser" "clearUser"])
@commands.has_permissions(manage_messages=True)
async def cUser(ctx, user: commands. MemberConverter, *, amount=5):
  async for message in ctx.history(limit=amount):
    if message.author == user:
      await message.delete()
      
  if ctx.author != user:
    await ctx.message.delete()

@client.command(help="Make me say anything")
async def say(ctx, *, text=''):
    if text == '':
        ctx.send("You need to say something")
    else:
        await ctx.send(text)
        await ctx.message.delete()

keep_alive()
client.run(os.getenv("DISCORD"))
