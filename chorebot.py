import discord
from discord.ext import commands
import asyncio
import pymongo
from pymongo import MongoClient
from music import music
import datetime
import math
                ############## Discord Bot Commands ##############

                            ### Initialization ###
################################################################################
cluster = MongoClient("")
db = cluster.get_database('chorebot')
client = commands.Bot(command_prefix = '-', case_Insenitive = True, intents = discord.Intents.all())
client.add_cog(music(client))
client.remove_command("help")

@client.event
async def on_ready():
    print('Bot is ready.')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
################################################################################

                    ### Improper Function Call Handler ###
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("ERROR: Command does not exist or was called incorrectly.")
                                ###Functions###
################################################################################

### Test Command ###
@client.command(pass_context=True)
async def test(ctx, member: discord.Member=None):
    await ctx.send("Command received.")

### Help Function ###
@client.command(pass_context=True)
async def help(ctx, arg = "all"):
    slCmdArr = ["-add [Quantity](optional) [Item]\n", 
                "-remove [Quantity](optional) [Item]\n", 
                "-mark [Item]", 
                "-markall", 
                "-unmark [Item]", 
                "-unmarkall", 
                "-clear"]
    slDescArr = ["Adds and item or quantity of an item to your list.",
                 "Removes and item or quantity of an item to your list.",
                 "Marks an item on your list.",
                 "Marks all items on your list.",
                 "Unmarks an item on your list.",
                 "Unmarks all items on your list.",
                 "Clears all items from your list."]
    mCmdArr = ["-play/-p [Link or Title]",
               "-pause",
               "-resume",
               "-skip/-next/-s/-n",
               "-queue/-q",
               "-clear/-c",
               "-stop/-leave/-disconnect/-dc"]
    mDescArr = ["Plays a track from given title or link.",
               "Pauses track.",
               "Resumes track.",
               "Skips the current track.",
               "Displays the queue.",
               "Clears all songs from the queue.",
               "Disconnects the bot from the voice channel."]

    if ((arg == "sl") | (arg == "shoppinglist")):
        cmdStr = ""
        descStr = ""
        for i in range(len(slCmdArr)):
            cmdStr = cmdStr + slCmdArr[i] + "\n"
            descStr = descStr + slDescArr[i] + "\n"
        embed=discord.Embed(title="Shopping List Commands", description="All shopping list commands.", color=0x6F9D90)

    if ((arg == "m") | (arg == "music")):
        cmdStr = ""
        descStr = ""
        for i in range(len(slCmdArr)):
            cmdStr = cmdStr + mCmdArr[i] + "\n"
            descStr = descStr + mDescArr[i] + "\n"
        embed=discord.Embed(title="Music Commands", description="All music commands.", color=0x94D0E1)

    if ((arg == "a") | (arg == "all") | (arg == "")):
        cmdArr = slCmdArr + mCmdArr
        descArr = slDescArr + mDescArr
        cmdStr = ""
        descStr = ""
        for i in range(len(cmdArr)):
            cmdStr = cmdStr + cmdArr[i] + "\n"
            descStr = descStr + descArr[i] + "\n"
        embed=discord.Embed(title="All Commands", description="List of commands.", color=0xDBE6EA)
    
    embed.set_author(name="Chore Bot Help",icon_url="https://imgur.com/ODYt1Tx.jpg")
    embed.set_thumbnail(url="https://imgur.com/ODYt1Tx.jpg")
    embed.add_field(name="Command", value=cmdStr, inline=True)
    embed.add_field(name="Description", value=descStr, inline=True)
    await ctx.send(embed = embed)

### Generate Shopping List Embed ###
def shopList(ctx, uid):
    collection = db.get_collection("User Data")
    userData = collection.find_one({"_id":uid})
    data = userData["Shopping List"]
    itemStr = ""
    qtyStr = ""
    chkStr = ""
    if (len(data) != 0):
        for item in data:
            itemStr = itemStr + item.get('name') + "\n"
            qtyStr = qtyStr + str(item.get('qty')) + "\n"
            if (item.get('chk') == True):
                chkStr = chkStr + ":white_check_mark:" + "\n"
            else:
                chkStr = chkStr+ ":x:" + "\n"
    else:
        itemStr = "------"
        qtyStr = "------------"
        chkStr = "-------"

    embed=discord.Embed(title="Shopping List", description="For a list of commands use: -help shoppinglist",color=0x6F9D90)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.add_field(name="Item", value=itemStr, inline=True)
    embed.add_field(name="Quantity", value=qtyStr, inline=True)
    embed.add_field(name="Check", value=chkStr, inline=True)
    return embed

### Add To Shopping List Command ###
@client.command(pass_context=True)
async def add(ctx, *args):
    if (len(args) == 0):
        await ctx.send("Error | Proper command syntax is: -add [Quantity](optional) [Item]")
        return
    collection = db.get_collection("User Data")
    uid = ctx.message.author.id
    if (args[0].isnumeric() == 0):
        qty = 1
        name = args[0]
        for i in range(1, len(args)):
            name = name + " " + args[i]
    else:
        qty = int(args[0])
        name = args[1]
        for i in range(2, len(args)):
            name = name + " " + args[i]
    if collection.count_documents({"_id":uid}) == 0:
            data = {"_id" : uid, "Shopping List":[{"name":name, "qty":qty, "chk":False}]}
            collection.insert_one(data)

            await ctx.send(embed = shopList(ctx, uid))
            return
    else:
        userData = collection.find_one({"_id":uid})
        data = userData["Shopping List"]
        found = 0
        for item in data:
            if item.get('name') == name:         
                item["qty"] = (item.get("qty") + int(qty))
                found = 1
                break
        if (found == 1):
            collection.update_one({"_id":uid}, {"$set": {"Shopping List" : data}})
        else:
            collection.update_one({"_id":uid}, {"$push": {"Shopping List" : {"name":name, "qty":qty, "chk":False}}})
        await ctx.send(embed = shopList(ctx, uid))

### Remove from Shopping List Command ###
@client.command(pass_context=True)
async def remove(ctx, *args):
    if len(args) == 0:
        await ctx.send("Error | Proper command syntax is: -remove [Quantity](optional) [Item]")
        return
    collection = db.get_collection("User Data")
    uid = ctx.message.author.id
    userData = collection.find_one({"_id":uid})
    data = userData["Shopping List"]
    if (args[0].isnumeric() == 0):
        qty = 1
        name = args[0]
        for i in range(1, len(args)):
            name = name + " " + args[i]
        found = 0
        index = 0
        for item in data:
            if item.get('name') == name:         
                data.remove(data[index])
                found = 1
                break
            index = index + 1
        if (found == 0):
            await ctx.send("Error | This item was not on your list.")
            return
        collection.update_one({"_id":uid}, {"$set": {"Shopping List" : data}})
        
        await ctx.send(embed = shopList(ctx, uid))
        
        return
    else:
        qty = int(args[0])
        name = args[1]
        for i in range(2, len(args)):
            name = name + " " + args[i]
        found = 0
        index = 0
        for item in data:
            if (item.get('name') == name):   
                newQty = item.get('qty') - qty
                found = 1
                if (newQty < 1):
                    data.remove(data[index])
                    break
                else:
                    data[index].update({"qty":newQty})
                    break
            index = index + 1
        if (found == 0):
            await ctx.send("Error | This item was not on your list.")
            return
        collection.update_one({"_id":uid}, {"$set": {"Shopping List" : data}})
        
        await ctx.send(embed = shopList(ctx, uid))

        return

### Mark List Item Command ###
@client.command(pass_context=True)
async def mark(ctx, *args):
    if (len(args) == 0):
        await ctx.send("Error | Proper command syntax is: -mark [Item]")
        return
    collection = db.get_collection("User Data")
    uid = ctx.message.author.id
    userData = collection.find_one({"_id":uid})
    data = userData["Shopping List"]
    name = args[0]
    for i in range(1, len(args)):
        name = name + " " + args[i]
    found = 0
    index = 0
    for item in data:
        if item.get('name') == name:         
            item["chk"] = True
            found = 1
            break
        index = index + 1
    if (found == 0):
        await ctx.send("Error | This item was not on your list.")
        return
    collection.update_one({"_id":uid}, {"$set": {"Shopping List" : data}})
    
    await ctx.send(embed = shopList(ctx, uid))
    return

### Mark All List Item Command ###
@client.command(pass_context=True)
async def markall(ctx):
    collection = db.get_collection("User Data")
    uid = ctx.message.author.id
    userData = collection.find_one({"_id":uid})
    data = userData["Shopping List"]
    for item in data:       
        item["chk"] = True
    collection.update_one({"_id":uid}, {"$set": {"Shopping List" : data}})
    await ctx.send(embed = shopList(ctx, uid))
    return


### Unmark List Item Command ###
@client.command(pass_context=True)
async def unmark(ctx, *args):
    if (len(args) == 0):
        await ctx.send("Error | Proper command syntax is: -unmark [Item]")
        return
    collection = db.get_collection("User Data")
    uid = ctx.message.author.id
    userData = collection.find_one({"_id":uid})
    data = userData["Shopping List"]
    name = args[0]
    for i in range(1, len(args)):
        name = name + " " + args[i]
    found = 0
    index = 0
    for item in data:
        if item.get('name') == name:         
            item["chk"] = False
            found = 1
            break
        index = index + 1
    if (found == 0):
        await ctx.send("Error | This item was not on your list.")
        return
    collection.update_one({"_id":uid}, {"$set": {"Shopping List" : data}})
    
    await ctx.send(embed = shopList(ctx, uid))
    return

### Unmark All List Item Command ###
@client.command(pass_context=True)
async def unmarkall(ctx):
    collection = db.get_collection("User Data")
    uid = ctx.message.author.id
    userData = collection.find_one({"_id":uid})
    data = userData["Shopping List"]
    for item in data:       
        item["chk"] = False
    collection.update_one({"_id":uid}, {"$set": {"Shopping List" : data}})
    await ctx.send(embed = shopList(ctx, uid))
    return

### Clear List Item Command ###
@client.command(pass_context=True)
async def clearlist(ctx):
    collection = db.get_collection("User Data")
    uid = ctx.message.author.id
    data = []
    collection.update_one({"_id":uid}, {"$set": {"Shopping List" : data}})
    await ctx.send(embed = shopList(ctx, uid))
    return

### Display Shopping List Command ###
@client.command(pass_context=True)
async def list(ctx):
    uid = ctx.message.author.id
    await ctx.send(embed = shopList(ctx, uid))

                            ### Debts Functions ###
################################################################################
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def addDebt(sid, uid, user, value, note, date):
    collection = db.get_collection("Debts")
    debtDict = {"note":note,"value":value, "user": user, "date":date,"paid":False}
    if collection.count_documents({"_id":sid}) == 0:
        entry = {"_id" : sid, "Users":{str(uid):[debtDict]}}
        collection.insert_one(entry)
        return
    else:
        data = collection.find_one({"_id":sid})["Users"]
        if (str(uid) not in data):
            data[str(uid)] = [debtDict]
        else:
            temp = data.get(str(uid))
            temp.append(debtDict)
            data.update({str(uid):temp})
        collection.update_one({"_id":sid}, {"$set": {"Users" : data}})
        return

@client.command(pass_context=True)
async def owe(ctx, member:discord.Member=None, *args):
    if ((isfloat(args[0]) == True) and (member is not None) and (len(args) >= 2)):
        sid = ctx.guild.id
        uid = ctx.author.id
        user = member.id
        value = float(args[0])
        note = args[1]
        date = str(datetime.datetime.utcnow().month) + "/" + str(datetime.datetime.utcnow().day) + "/" + str(datetime.datetime.utcnow().year)
        print(date)
        for i in range(2, len(args)):
            note = note + " " + args[i]
        addDebt(sid, uid, user, value, note, date)
        
        titleStr = "You Owe " + "{:.2f}".format(value) + "$ to "+ member.display_name + "."
        c2Str = "\"" + note + "\""
        embed=discord.Embed(title=titleStr, color=0xAC111C)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Note", value=c2Str, inline=True)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed = embed)
        return
    else:
        await ctx.send("Error | Proper command syntax is: -request [User] [Amount] [Note]")
        return

@client.command(pass_context=True)
async def request(ctx, member:discord.Member=None, *args):
    if ((isfloat(args[0]) == True) and (member is not None) and (len(args) >= 2)):
        sid = ctx.guild.id
        uid = member.id
        user = ctx.author.id
        value = float(args[0])
        note = args[1]
        date = str(datetime.datetime.utcnow().month) + "/" + str(datetime.datetime.utcnow().day) + "/" + str(datetime.datetime.utcnow().year)
        for i in range(2, len(args)):
            note = note + " " + args[i]
        addDebt(sid, uid, user, value, note, date)
        
        titleStr = "You requested " + "{:.2f}".format(value) + "$ from "+ member.display_name + "."
        c2Str = "\"" + note + "\""
        embed=discord.Embed(title=titleStr, color=0xAC111C)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Note", value=c2Str, inline=True)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed = embed)
        return
    else:
        await ctx.send("Error | Proper command syntax is: -request [User] [Amount] [Note]")
        return

def debtsEmbed(ctx, uid, sid):
    collection = db.get_collection("Debts")
    userData = collection.find_one({"_id":sid})
    data = userData["Users"]
    data = data.get(str(uid))
    if (data == None):
        #await ctx.send("Error | User has no debts.")
        return
    else:
        for i in range(math.ceil(len(data)/10)):
            embed=discord.Embed(title="Debts", description="For a list of commands use: -help debts or -help d",color=0xAC111C)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name="Amount", value="Bruh", inline=True)
            embed.add_field(name="To", value="Bruh", inline=True)
            embed.add_field(name="Date", value="Bruh", inline=True)
            yield "bruh"


@client.command(pass_context=True)
async def debts(ctx, member:discord.Member=None):
    sid = ctx.guild.id
    uid = ctx.author.id
    for j in debtsEmbed(ctx,uid,sid):
        print(j, end=" ")
    
    embedsArr = []###

    client.help_pages = embedsArr
    buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"] # skip to start, left, right, skip to end
    current = 0
    msg = await ctx.send(embed=client.help_pages[current])
    for button in buttons:
        await msg.add_reaction(button)
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)
        except asyncio.TimeoutError:
            return print("test")
        else:
            previous_page = current
            if reaction.emoji == u"\u23EA":
                current = 0
            elif reaction.emoji == u"\u2B05":
                if current > 0:
                    current -= 1
            elif reaction.emoji == u"\u27A1":
                if current < len(client.help_pages)-1:
                    current += 1
            elif reaction.emoji == u"\u23E9":
                current = len(client.help_pages)-1
            for button in buttons:
                await msg.remove_reaction(button, ctx.author)
            if current != previous_page:
                await msg.edit(embed=client.help_pages[current])



client.run('')