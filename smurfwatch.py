from lxml import html
import requests
import json
import time

import discord
from discord.ext import tasks, commands
from discord.channel import ChannelType
import asyncio

# pylint: disable=no-member
# pylint doesn't recognise that loops have 'start' and 'cancel' methods so incorrectly throws errors without the above line.
# remove during final debugging but expect to see some number of errors from that

class SmurfWatch(commands.Cog):
    
    def __init__(self,bot):
        self.bot = bot
        self.players = [ # hardcoded for now
            (225255130067369984, 2453530),
            (691407715859169332, 1031005),
            (218657470409605120, 2044647),
            ]
        
        # load players from file eventually, format (discordid, profileid)
        self.exclude = []
        self.smurfCheck.start()

    def cog_unload(self):
        self.smurfCheck.cancel()

    @tasks.loop(seconds=30)
    async def smurfCheck(self):
        players = []
        channels = []
        usersinvoice = {}

        for channel in self.bot.get_all_channels(): # get all voice channels the bot can see
            print(channel.name)
            print(channel.type)
            if channel.type == ChannelType.voice:
                for user in channel.voice_states:
                    usersinvoice[user] = channel.id # add user ids to a list

        print("Smurfwatch: checking users in voice")
        print(usersinvoice)

        print(players)

        for player in self.players: # check if users are in voice
            if player[0] in usersinvoice: #
                players += [player[1]]
                channels += [usersinvoice[player[0]]] # add channel to list
        if players != []:
            if self.check(players):
                vqueue = self.bot.get_cog("VoiceQueue")
                if vqueue is not None:
                    for channel in channels:
                        await vqueue.add(self.bot.get_channel(channel),"audio/smurfwatch/smurfs.mp3")
                    # add smurf.mp3 to voice queue in all channels
                else:
                    print("Enable the VoiceQueue cog in main.py pls")

        #if they are, add smurf.mp3 to voicequeue. if voicequeue isn't there, print a debug message.

    def check(self,players):

        smurf = False
        excludeinternal = self.exclude
        excludeout = []
        matches = []
        finalmatches = []
        playerstocheck = []

        for player in players:

            page = requests.get('https://aoe2.net/api/player/lastmatch?game=aoe2de&profile_id='+ str(player))
            gameinfo = json.loads(page.content)
            matches += [gameinfo]
        
        # exclude any duplicate matches, finished matches, or matches in the exclude list

        for match in matches:
            if match['last_match']['match_id'] in excludeinternal:
                if match['last_match']['finished'] == 'null':
                    excludeout += match['last_match']['match_id']
            else:
                if match['last_match']['finished'] == 'null':
                    excludeinternal += match['last_match']['match_id']
                    excludeout += match['last_match']['match_id']
                    finalmatches += match
                    
        self.exclude = excludeout

        # now we have a list of matches to extract profile ids from

        print("")
        print("players in games:")

        for match in finalmatches: # add players to list of profile ids, ignoring duplicates or ourselves
            for player in match['last_match']['players']:
                print(player['profile_id'])
                if player['profile_id'] not in playerstocheck and int(player['profile_id']) not in players: playerstocheck += [player['profile_id']]

        print("")
        print("checking players:")

        for player in playerstocheck:
            print(player)
            if self.isSmurf(player):
                print(str(player)+ " is a Smurf!")
                smurf = True

        print("Smurfs = " + str(smurf))
        return smurf

    def isSmurf(self,profile_id):
        randomWinRate = 0
        randomPlayed = 0
        teamRandomWinRate = 0
        teamRandomPlayed = 0

        #random leaderboard

        page = requests.get('https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=3&profile_id=' + str(profile_id) + '&count=1')
        playerinfo = json.loads(page.content)
        
        if playerinfo != []:
            randomPlayed = playerinfo[0]['num_wins'] + playerinfo[0]['num_losses']
            randomWinRate = playerinfo[0]['num_wins'] / randomPlayed

        # team random leaderboard

        page = requests.get('https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=4&profile_id=' + str(profile_id) + '&count=1')
        playerinfo = json.loads(page.content)

        if playerinfo != []:
            teamRandomPlayed = playerinfo[0]['num_wins'] + playerinfo[0]['num_losses']
            teamRandomWinRate = playerinfo[0]['num_wins'] / teamRandomPlayed

        # if total played games are above 60 don't bother doing any digging if anything is missing

        if randomPlayed == 0:
            if teamRandomPlayed < 60:
                print("Going detailed!")
                (randomPlayed,randomWinRate) = self.detailedWinRate(profile_id,3)
        
        if teamRandomPlayed == 0:
            if randomPlayed < 60:
                print("Going detailed!")
                (teamRandomPlayed,teamRandomWinRate) = self.detailedWinRate(profile_id,4)

        if randomPlayed+teamRandomPlayed < 60:
            if randomWinRate > 0.7 or teamRandomWinRate > 0.7:
                return True
        return False

    def detailedWinRate(self,profile_id,leaderboard):
        played = 0
        wins = 0

        page = requests.get('https://aoe2.net/api/player/matches?game=aoe2de&profile_id=' + str(profile_id) + '&count=1000')
        matches = json.loads(page.content)
        filteredmatches = []
        for match in matches:
            if match['leaderboard_id'] == leaderboard:
                filteredmatches += [match]

        for match in filteredmatches:
            player_id = []
            played += 1
            for player in match['players']:
                if str(player['profile_id']) == str(profile_id): player_id = player
            if player_id['won']: wins += 1

        return (played,wins/played)
