import discord
from discord.ext import tasks, commands
import asyncio

# pylint: disable=no-member
# pylint doesn't recognise that loops have 'start' and 'cancel' members so incorrectly throws errors without the above line.
# remove during final debugging but expect to see some number of errors from that

class VoiceQueue(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.queue = []
        self.playing = False
        self.voiceLoop.start()
        
    def cog_unload(self):
        self.voiceLoop.cancel()

    async def add(self,userchannel,audiosource): # add request to play voice in a channel, max of 10
        if len(self.queue) < 10:
            self.queue += [(userchannel,audiosource)]
        else:
            print("Queue full!")

    async def playAudio(self,userchannel,audiosource): # connect to channel, play audio, disconnect
        vc = await userchannel.connect()
        self.playing = True
        vc.play(discord.FFmpegPCMAudio(source=audiosource,executable="ffmpeg/ffmpeg.exe",))
        while vc.is_playing():
            await asyncio.sleep(.1)
        await vc.disconnect()
        self.playing = False

    @tasks.loop(seconds=0.1) # check every 100ms if it has something to play AND not already playing something
    async def voiceLoop(self):
        if not self.queue == []: print(self.queue)
        if not self.playing and not self.queue == []:
            (userchannel,audiosource) = self.queue.pop(0)
            await self.playAudio(userchannel,audiosource)


