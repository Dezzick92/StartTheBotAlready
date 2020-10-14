# example_bot.py

import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print('Connected as as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run('NzY2MDA2ODg4MzYxODg1NzA3.X4dFgQ.sZ6Q5sP6IFUtT8cadtFlT0LQc0Y')