import discord
from discord.ext import commands
import asyncio
import os
import yt_dlp
import subprocess
from dotenv import load_dotenv

load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")

bot = commands.Bot(command_prefix='!')

ytdl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

def download_audio(url, output_file):
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        print(f'Downloading audio from "{video_title}"...')
        ydl.download([url])
        # Convert the downloaded file to MP3 using FFmpeg
        # You will need to have FFmpeg installed on your system to do this.
        subprocess.run(['ffmpeg', '-i', f'{video_title}.webm', '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', output_file])
        print(f'Successfully downloaded and converted to MP3: "{output_file}"')

@bot.event
async def on_ready():
    print('Bot is ready!')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('pong')

@bot.command(name='play')
async def play(ctx, url):
    # Check if the user is in a voice channel
    if not ctx.author.voice:
        await ctx.send('You are not connected to a voice channel.')
        return
    channel = ctx.author.voice.channel
    # Connect to the voice channel
    await channel.connect()
    # Download the audio from the YouTube URL
    output_file = f'{url.split("=")[1]}.mp3'
    download_audio(url, output_file)
    # Play the downloaded audio
    voice_client = ctx.voice_client
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(output_file))
    voice_client.play(source)
    # Wait for the audio to finish playing
    while voice_client.is_playing():
        await asyncio.sleep(1)
    # Disconnect from the voice channel
    await voice_client.disconnect()
    # Remove the downloaded audio file
    os.remove(output_file)

bot.run(DISCORD_TOKEN)
