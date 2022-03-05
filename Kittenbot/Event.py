import random
import discord

async def Create(client, settings, ctx, name, colour, description):
  if not colour:
    colour = 0x8f43f0
      
  index = 0
  while index < len(settings):
    index = index + 1

  if len(settings) > index + 1:
    if not settings[index]:
      settings.pop(index)

  if description == None:
    description = "No description available"

  Embed = discord.Embed(title=name,description=description)
  Embed.set_footer(text=f"Event stored at Index {index}")

  message = await ctx.send(content="New Event!", embed=Embed) 
  settings.insert(index, message.id)
  return settings

async def Start(client, settings, ctx, index, winners, role):
  index = int(index)
  winners = int(winners)
  
  message = await ctx.fetch_message(settings[index])
  
  users = []
  for reaction in message.reactions:
    async for user in reaction.users():
      users.append(user)

  if not users:
    return
  
  all_winners = []
  while len(all_winners) < winners and len(all_winners) < len(users):
    winner = random.choice(users)
    inArray = winner in all_winners

    if not inArray:
      if role:
        await winner.add_roles(role)
      
      await ctx.send(f'{winner.mention} has been selected for the event')
      all_winners.append(winner)

async def Delete(client, settings, ctx, index):
  if index == "all":
    async for message in ctx.history(limit=200):
      if message.id in settings:
        await message.delete()
      
    return []
  
  index = int(index)

  message = await ctx.fetch_message(settings[index])
  await message.delete()
  settings.pop(index)

  i = 0
  for id in settings:
    m = await ctx.fetch_message(settings[i])
    embed = m.embeds[0]
    embed.set_footer(text=f"Event stored at Index {i}")
    await m.edit(content=m.content, embed=embed)
    i += 1

  return settings