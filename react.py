import variable
import discord

async def sortReact(client):
    react_channel = client.get_channel(variable.react_channel)
    react_embed = discord.Embed(title=variable.ping_title,colour=discord.Colour (variable.ping_colour), description=variable.react_description)
    x = 0
    
    while x < len(variable.react_message):
      react_embed.add_field(name=client.get_guild(variable.guild_id).get_role(variable.react_roles[x]).name + " " + variable.react_emojis[x], value=variable.react_message[x], inline=True)
      x += 1

    await checkMessage(react_channel, react_embed)

async def checkMessage(react_channel, react_embed):
    count = 0

    async for message in react_channel.history (limit=200):
      if message.id == variable.ping_expected_message_id:
        variable.ping_expected_message_id = message.id
        await message.edit(content=variable.ping_message, embed=react_embed)
        await addEmoji(message)
        count = 1
        
    if count != 1:
      message = await react_channel.send(content=variable.ping_message, embed=react_embed)
      variable.ping_expected_message_id = message.id
      await addEmoji(message)

async def addEmoji(message):
      for x in variable.react_emojis:
        await message.add_reaction(x)

async def getRole(client, payload, add):
  message_id = payload.message_id
  guild_id = payload.guild_id

  channel = client.get_channel(variable.react_channel)

  async for message in channel.history (limit=200): 
    if  message.id == variable.ping_expected_message_id:
        
      if message_id == variable.ping_expected_message_id:
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        member = discord.utils.find(lambda m: m.id == payload.user_id,guild.members)

        role = None;
          
        if member != None:
          x = 0
          while x < len(variable.react_emojis):
            if payload.emoji.name == variable.react_emojis[x]:
              role = discord.utils.get(guild.roles, id=variable.react_roles[x])
            x += 1
        
          if role != None:
              if add == True:
                await member.add_roles(role)
              else:
                await member.remove_roles(role)
          else:
            print("Role not found")
        else:
           print("Member not found")
    else:
      print("Invalid Reaction")
  return

