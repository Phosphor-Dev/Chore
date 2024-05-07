import discord
from discord.ext import commands
#from youtube_dl import YoutubeDL
from yt_dlp import YoutubeDL
import datetime
class music(commands.Cog):
    #####
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client # Get the member in the channel
        if voice_state is not None and len(voice_state.channel.members) == 1: # If bot is alone
            await voice_state.disconnect() # Disconnect
    #####

    def __init__(self, bot):
        self.cp = ""
        self.bot = bot
        self.vc = None
        self.music_queue = []
        self.is_paused = False
        self.is_playing = False
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False
        return {'source': info['formats'][0]['url'], 'title': info['title']}
    
    def play_next(self, ctx):
        if len(self.music_queue) > 0:
            m_url = self.music_queue[0][0]['source']
            self.cp = self.music_queue[0][0]['title']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            self.is_playing = True
        else:
            self.vc.stop()
            self.cp = ""
            self.is_playing = False
            self.is_paused = False
            self.music_queue = []
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            m_url = self.music_queue[0][0]['source']
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            self.cp = self.music_queue[0][0]['title']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            self.is_playing = True  
        else:
            self.vc.stop()
            self.cp = ""
            self.is_playing = False
            self.is_paused = False
            self.music_queue = []
            self.is_playing = False
    
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *args):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is None and self.vc is not None:
            self.cp = ""
            self.is_playing = False
            self.is_paused = False
            self.music_queue = []
            self.vc = None

        query = " ".join(args)
        voice_channel = ctx.author.voice.channel
        if not ctx.author.voice:
            await ctx.send("You need to be connected to a voice channel to use this.")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                self.music_queue.append([song, voice_channel])
                if self.is_playing == False and self.is_paused == False:
                    embed=discord.Embed(title="Now Playing",description=self.music_queue[0][0]['title'],color=0x94D0E1)
                    await self.play_music(ctx)
                else:
                    embed=discord.Embed(title="Added To Queue",description=self.music_queue[-1][0]['title'],color=0x94D0E1)
                embed.set_author(name="Chore",icon_url="https://imgur.com/ODYt1Tx.jpg")
                embed.timestamp = datetime.datetime.utcnow()
                await ctx.send(embed = embed)

    @commands.command(name="pause")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            embed=discord.Embed(title="Pausing Track...", description=self.cp,color=0x94D0E1)
            embed.set_author(name="Chore",icon_url="https://imgur.com/ODYt1Tx.jpg")
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed = embed)

    @commands.command(name = "resume")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            embed=discord.Embed(title="Resuming Track...", description=self.cp,color=0x94D0E1)
            embed.set_author(name="Chore",icon_url="https://imgur.com/ODYt1Tx.jpg")
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed = embed)

    @commands.command(name="skip", aliases=["-next", "-n", "-s"])
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            if len(self.music_queue) > 0:
                embed=discord.Embed(title="Now Playing",description=self.music_queue[0][0]['title'],color=0x94D0E1)
                embed.set_author(name="Chore",icon_url="https://imgur.com/ODYt1Tx.jpg")
                embed.timestamp = datetime.datetime.utcnow()
                await ctx.send(embed = embed)
                retval = ""
                for i in range(1, len(self.music_queue)):
                    if (i > 9): break
                    retval += str(i) + " - " + self.music_queue[i][0]['title'] + "\n"
                embed=discord.Embed(title="Up Next", description="For a list of commands use: -commandlist music",color=0x94D0E1)
                embed.set_author(name="Chore", icon_url="https://imgur.com/ODYt1Tx.jpg")
                embed.set_thumbnail(url="https://imgur.com/ODYt1Tx.jpg")
                embed.timestamp = datetime.datetime.utcnow()
                if retval != "":
                    embed.add_field(name="Title", value=retval, inline=True)
                else:
                    embed.add_field(name="Title", value="_The queue is empty._", inline=True)
                await ctx.send(embed = embed)
            else:
                embed=discord.Embed(title="Up Next", description="For a list of commands use: -commandlist music",color=0x94D0E1)
                embed.set_author(name="Chore", icon_url="https://imgur.com/ODYt1Tx.jpg")
                embed.set_thumbnail(url="https://imgur.com/ODYt1Tx.jpg")
                embed.timestamp = datetime.datetime.utcnow()
                embed.add_field(name="Title", value="_The queue is empty._", inline=True)
                await ctx.send(embed = embed)
            self.vc.pause()
            self.vc.stop()


    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            if (i > 9): break
            retval += str(i+1) + " - " + self.music_queue[i][0]['title'] + "\n"
        embed=discord.Embed(title="Up Next", description="For a list of commands use: -commandlist music",color=0x94D0E1)
        embed.set_author(name="Chore", icon_url="https://imgur.com/ODYt1Tx.jpg")
        embed.set_thumbnail(url="https://imgur.com/ODYt1Tx.jpg")
        embed.timestamp = datetime.datetime.utcnow()
        if retval != "":
            embed.add_field(name="Title", value=retval, inline=True)
        else:
            embed.add_field(name="Title", value="_The queue is empty._", inline=True)
        await ctx.send(embed = embed)

    @commands.command(name="clear", aliases=["c"])
    async def clear(self, ctx):
        if self.vc and self.is_playing:
            embed=discord.Embed(title="Queue Has Been Cleared",color=0x94D0E1) 
        else:
            embed=discord.Embed(title="Queue Is Currently Empty",color=0x94D0E1)
        self.cp = ""
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
        self.vc.stop()
        embed.set_author(name="Chore",icon_url="https://imgur.com/ODYt1Tx.jpg")
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed = embed)

    @commands.command(name="stop", aliases=["disconnect", "leave", "dc"])
    async def stop(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if self.vc != None or voice_client is not None:
            self.cp = ""
            self.is_playing = False
            self.is_paused = False
            await self.vc.disconnect()
            self.vc.stop()
            self.music_queue = []
            self.vc = None
            embed=discord.Embed(title="Leaving Voice Channel",color=0x94D0E1)
            embed.set_author(name="Chore",icon_url="https://imgur.com/ODYt1Tx.jpg")
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed = embed)
        else:
            embed=discord.Embed(title="Not Connected To A Voice Channel",color=0x94D0E1)
            embed.set_author(name="Chore",icon_url="https://imgur.com/ODYt1Tx.jpg")
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed = embed)
    
    @commands.command()
    async def info(self, ctx):
        print("----------------------------------------------------------")
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        print("Current utils vc:")
        if (voice_client is None):
            print("voice_client:\nNone")
        else:
            print(voice_client)
        print("Current self.vc:")
        print(self.vc)
        print("Currently playing:")
        print(self.cp)
        print("Items in music queue:")
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += str(i+1) + " - " + self.music_queue[i][0]['title'] + "\n"
        if retval != "":
            print("------------")
            print(retval)
            print("------------")
        else:
            print("-Queue is empty.-")
        print("Is paused:")
        print(self.is_paused)
        print("Is playing:")
        print(self.is_playing)
        print("----------------------------------------------------------")