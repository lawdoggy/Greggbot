import asyncio
import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
from dotenv import load_dotenv
import youtube_dl


load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)


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
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
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


queue = []



async def get_title(url):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    return data.get('title')



@bot.command()
async def play(ctx, url):
    if not ctx.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    else:
        channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send(f"Connected to {channel}")
    queue.append({"title": await get_title(url), "url": url})
    if len(queue) == 1:
        play_next(ctx)


async def play_next(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if len(queue) > 0:
        next_song = queue[0]
        source = await YTDLSource.create_source(ctx, next_song['url'], loop=bot.loop)
        voice.play(source, after=lambda e: bot.loop.create_task(play_next(ctx))) # pass in ctx argument here
        await ctx.send(f"Now playing: {next_song['title']}")
        queue.pop(0)
    else:
        await ctx.send("There are no more songs in queue.")
        await voice.disconnect()




@bot.command()
async def skip(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.stop()
        play_next()


@bot.command()
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        voice.stop()
        queue.clear()
        await voice.disconnect()


def play_next():
    voice = get(bot.voice_clients, guild=ctx.guild)

    if queue:
        source = queue.pop(0)
        voice.play(source, after=lambda e: play_next())


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@client.event
async def on_voice_state_update(member, before, after):
    if member == client.user and after.channel is not None and before.channel != after.channel:
        print(f"The bot has joined {after.channel}")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
