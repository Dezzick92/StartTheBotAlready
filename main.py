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
import taunts

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

bot.add_cog(voicequeue.VoiceQueue(bot))
bot.add_cog(smurfwatch.SmurfWatch(bot))
bot.add_cog(taunts.Taunts(bot))

@bot.event
async def on_ready():
    print('Connected as')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

bot.run(TOKEN)
