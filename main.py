# example_bot.py

import os
from os import listdir
from os.path import isfile, join
import asyncio

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

soundfiles = [f for f in listdir("audio/") if isfile(join("audio/", f))]
validnums = [i for i in range(0,len(soundfiles))]
for i in validnums:
    validnums[i] += 1
    validnums[i] = str(validnums[i])

@client.event
async def on_ready():
    print('Connected as as {0.user}'.format(client))

@client.event
async def on_message(message):

    if message.author == client.user: # ignore messages from the bot
        return

    if message.content in validnums: # if it's a number, do stuff
        #await message.channel.send("audio/" + soundfiles[int(message.content)-1])
        connected = message.author.voice
        if connected:
            vc = await connected.channel.connect()
            vc.play(discord.FFmpegPCMAudio(source="audio/" + soundfiles[int(message.content)-1],executable="ffmpeg/ffmpeg.exe",))
            while vc.is_playing():
                await asyncio.sleep(.1)
            await vc.disconnect()
            

            

client.run(TOKEN)
