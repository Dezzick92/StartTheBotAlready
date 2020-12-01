# taunts.py
import os
from os import listdir
from os.path import isfile, join
import asyncio

import discord
from discord.ext import tasks, commands
from discord.channel import ChannelType
import asyncio

# pylint: disable=no-member
# pylint doesn't recognise that loops have 'start' and 'cancel' methods so incorrectly throws errors without the above line.
# remove during final debugging but expect to see some number of errors from that

class Taunts(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # get sound files for the aoe2 taunts
        self.soundfiles = [f for f in listdir("audio/taunts/") if isfile(join("audio/taunts/", f))]
        self.validnums = [i for i in range(0,len(self.soundfiles))]
        for i in self.validnums:
            self.validnums[i] += 1
            self.validnums[i] = str(self.validnums[i])

    @commands.Cog.listener()
    async def on_message(self, message): # move this into a listener or something

        if message.author == self.bot.user: # ignore messages from the bot
            return

        if message.content in self.validnums: # if it's a number, do stuff
            #await message.channel.send("audio/" + soundfiles[int(message.content)-1])
            connected = message.author.voice
            vqueue = self.bot.get_cog('VoiceQueue')
            if connected and vqueue is not None:
                await vqueue.add(connected.channel,"audio/taunts/" + self.soundfiles[int(message.content)-1])

