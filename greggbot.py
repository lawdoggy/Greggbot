import discord
from discord.ext import commands
import traceback
import yt_dlp
import re
import os
import random
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True
intents.message_content = True 

commands.Bot.case_insensitive = True # this will make all commands case-insensitive

bot = commands.Bot(command_prefix="!", intents=intents)



ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename), data=data)



youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='play', help='To play song')
async def play(ctx,url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        # Check if the bot is already connected to a voice channel
        if not voice_channel:
            # If not, connect to the user's voice channel
            user_voice_channel = ctx.author.voice.channel
            await user_voice_channel.connect()
            voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except Exception as e:
        print(e)
        print(str(e))
        traceback.print_exc()
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command()
async def hithere(ctx):
  voice_channel = ctx.author.voice.channel
  voice_client = await voice_channel.connect()
  audio_source = discord.FFmpegPCMAudio('C:/Python/Greggbot/Sounds/hithere.mp3')
  
  # Play the audio source on the voice client
  voice_client.play(audio_source)
  
  # Wait for a specified number of seconds before disconnecting from the voice channel
  await asyncio.sleep(2) # Wait for 5 seconds before disconnecting
  await ctx.voice_client.disconnect()

@bot.command() # don't forget the parentheses
async def hello(ctx): # use lowercase h for consistency
    responses = ["Hi there", "I like you. What do you think of me?", "I’m Old Gregg. Pleased to meet you.",
                 "I do watercolors.", "Do you love me?", "Could you learn to love me?",
                 "You think you could ever love me?", "You love me, and you’ve seen me, and you know me. I’m Old Gregg!",
                 "You must love me exactly as I love you", "Why can’t we do it now?", "Yes, sir. Thank you sir.",
                 "How does it work? Tell me how it works", "What do you mean?", "You must love me exactly as I love you",
                 "Do you love me? Are you playin’ your love games with me? I just want to know what to do, because I need your love a lot. Oh, come on now."
                 ]
    await ctx.send(random.choice(responses)) # send a random response from the list

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}') # use bot.user instead of client.user

load_dotenv()
token = os.getenv('TOKEN')
bot.run(token) # run the bot object instead of the client object






