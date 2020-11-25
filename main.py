# library imports

import os
from os import listdir
from os.path import isfile, join
import asyncio

import discord
from discord.ext import commands
from discord.channel import ChannelType
from dotenv import load_dotenv

# cog imports

import voicequeue
import smurfwatch

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

bot.add_cog(voicequeue.VoiceQueue(bot))
bot.add_cog(smurfwatch.SmurfWatch(bot))

# get sound files for the aoe2 taunts

soundfiles = [f for f in listdir("audio/taunts/") if isfile(join("audio/taunts/", f))]
validnums = [i for i in range(0,len(soundfiles))]
for i in validnums:
    validnums[i] += 1
    validnums[i] = str(validnums[i])

@bot.event
async def on_ready():
    print('Connected as')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')

@bot.event
async def on_message(message):

    if message.author == bot.user: # ignore messages from the bot
        return

    if message.content in validnums: # if it's a number, do stuff
        #await message.channel.send("audio/" + soundfiles[int(message.content)-1])
        connected = message.author.voice
        vqueue = bot.get_cog('VoiceQueue')
        if connected and vqueue is not None:
            await vqueue.add(connected.channel,"audio/taunts/" + soundfiles[int(message.content)-1])

bot.run(TOKEN)
