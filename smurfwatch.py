from lxml import html
import requests
import json
import time

def SmurfWatch(players = [], exclude = []):

    matches = []
    finalmatches = []
    excludeInternal = exclude
    excludeOut = []
    playersToCheck = []

    smurf = False

    for player in players:

        page = requests.get('https://aoe2.net/api/player/lastmatch?game=aoe2de&profile_id='+ str(player))
        gameinfo = json.loads(page.content)
        matches += [gameinfo]
    
    # exclude any duplicate matches, finished matches, or matches in the exclude list

    for match in matches:
        if match['last_match']['match_id'] in excludeInternal:
            if match['last_match']['finished'] == 'null':
                excludeOut += match['last_match']['match_id']
        else:
            if match['last_match']['finished'] == 'null':
                excludeInternal += match['last_match']['match_id']
                excludeOut += match['last_match']['match_id']
                finalmatches += match

    finalmatches = matches

    # now we have a list of matches to extract profile ids from

    print("")
    print("players in games:")

    for match in finalmatches: # add players to list of profile ids, ignoring duplicates or ourselves
        for player in match['last_match']['players']:
            print(player['profile_id'])
            if player['profile_id'] not in playersToCheck and int(player['profile_id']) not in players: playersToCheck += [player['profile_id']]

    print("")
    print("checking players:")

    for player in playersToCheck:
        print(player)
        if isSmurf(player):
            print(player['name']+ " is a Smurf!")
            smurf = True

    print("Smurfs = " + str(smurf))
    return smurf


def isSmurf(profile_id):
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
            (randomPlayed,randomWinRate) = detailedWinRate(profile_id,3)
    
    if teamRandomPlayed == 0:
        if randomPlayed < 60:
            print("Going detailed!")
            (teamRandomPlayed,teamRandomWinRate) = detailedWinRate(profile_id,4)

    if randomPlayed+teamRandomPlayed < 60:
        if randomWinRate > 0.7 or teamRandomWinRate > 0.7:
            return True
    return False

def detailedWinRate(profile_id,leaderboard):
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


if __name__ == "__main__":
    SmurfWatch([2453530,1031005,2044647],[]) #Joe, Harris, Simon

    print(isSmurf(3159920))
        

            
                
            
