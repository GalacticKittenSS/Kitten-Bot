async def Role(client, settings, ctx, role, user):
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

async def Clear(client, settings, ctx, amount):
	amount += 1
	await ctx.channel.purge(limit=amount)

async def ClearFromUser(client, settings, ctx, user, amount):
  async for message in ctx.history(limit=amount):
    if message.author == user:
      await message.delete()

async def Kick(client, settings, ctx, user, reason):
  if user == ctx.author:
    await ctx.send("You can't kick yourself, silly!")
    return
    
  await user.kick(reason=reason)
  
  if reason == None:
    reason = "Unknown"
  
  await ctx.send(f"Kicked: {user.mention} for {reason}")

    
async def Ban(client, settings, ctx, user, reason):
  if user == ctx.author:
    await ctx.send("You can't ban yourself, silly!")
    return
    
  await user.ban(reason=reason)
  
  if reason == None:
    reason = "Unknown"
    
  await ctx.send(f"Banned: {user.mention} for {reason}")
  
async def Unban(client, settings, ctx, user):    
  banned = await ctx.guild.bans()
  
  name, discriminator = user.split('#')
  for entry in banned:
    user = entry.user
		
    if (user.name, user.discriminator) == (name, discriminator):
      await ctx.guild.unban(user)
      await ctx.channel.send(f"Unbanned: {user.mention}")
      return

async def GetBanList(client, settings, ctx):
	banned = await ctx.guild.bans()
	if len(banned) == 0:
		return await ctx.send("No Banned User Found")
		
	message = "Currently Banned Users:"
	for entry in banned:
		reason = entry.reason
		if reason == None:
			reason = "Unknown"
  
		message += "\n> User: " + entry.user.mention + "#" + entry.user.discriminator + ", Reason: `" + reason + "`"
  
	await ctx.channel.send(content=message)