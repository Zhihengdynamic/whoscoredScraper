# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 17:23:35 2016

@author: JK
"""

import os
try:
    with open('python-wd.txt', 'r') as f:
        wdPath = f.read()
    f.closed
    os.chdir(wdPath)
except:
    pass



from file_helpers import open_from_csv
from file_helpers import open_from_disk
from file_helpers import write_to_csv
from python_helpers import search_entry
from scraper_helpers import correct_teamname
import datetime
import numpy as np
from tqdm import tqdm


#dataname = 'player_stats'
ending = '_complete'
dataname = 'player_stats' + ending
data = open_from_csv(dataname)

# must be up to date for validation:
matchID = open_from_disk('matchIdTeamLink' + ending)

#data = data[:1000]

game_parameters = ['bigError',
                   'Touches',
                   'TackleWonTotal',
                   'goalScored',
                   'ShotBlocked',
                   'PassLongBallTotal', 
                   'bigClearance', 
                   'DuelAerialWon', 
                   'KeyPassTotal', 
                   'ShotsTotal', 
                   'PassThroughBallAccurate', 
                   'PassThroughBallTotal',
                   'ShotOnTarget', 
                   'PassSuccessInMatch', 
                   'bigChanceMiss', 
                   'FoulCommitted',
                   'OffsideGiven', 
                   'PassLongBallAccurate', 
                   'FoulGiven', 
                   'TotalPasses', 
                   'assists', 
                   'Turnover', 
                   'ClearanceTotal',
                   'DribbleWon',
                   'InterceptionAll', 
                   'PassCrossAccurate',
                   'Dispossessed', 
                   'PassCrossTotal']

specialCases = []
for entry in tqdm(data):
    # give player entries consistent measurement names
    # which means to make first letter a small letter
    for key in entry:
        if key[0].isupper():
           entry[key[0].lower() + key[1:]] = entry.pop(key)
    # set substitution players game time to zero
    entry['substituted'] = False
    if entry['position'] == 'Sub':
        if entry['rating'] == '-':
            check = True
            for key,val in entry.items():
                if key in game_parameters:
                    if val is not '0':
                        if val == '':
                            entry[key] = '0'
                            continue
                        check = False
                        specialCases.append(entry)
            if check:
                entry['playedMinutes'] = '0'
        else:
            entry['substituted'] = True
    # compute points won
    if entry['result'] == 'win':
        entry['pointsWon'] = 3
    elif entry['result'] == 'defeat':
        entry['pointsWon'] = 0
    else:
        entry['pointsWon'] = 1
    # set card values from false/true to numbers
    if entry['yellowCard'] == 'False':
        entry['yellowCard'] = 0
    else:
        entry['yellowCard'] = 1
    if entry['redCard'] == 'False':
        entry['redCard'] = 0
    else:
        entry['redCard'] = 1
    

# prepare matchID information (to validate data later)
matchInfo = []
for ID in matchID:
    matchEntry = {}
    matchEntry['id'] = ID.split('_')[0]
    matchEntry['teams'] = ID.split('_')[1]
    matchEntry['date'] = datetime.datetime.strptime(ID.split('_')[2], '%b %d %Y')     
    month = ID.split('_')[2].split(' ')[0]
    year = ID.split('_')[2].split(' ')[2]
    if month in ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
        matchEntry['season'] = year + '-' + str(int(year) + 1)
    else:
        matchEntry['season'] = str(int(year) - 1) + '-' + year
    matchInfo.append(matchEntry)   
 
seasons = []
seasons = [dic['season'] for dic in matchInfo if dic['season'] not in seasons]
seasons = list(set(seasons))
seasons.sort()
matchInfos = []
for season in seasons:       
    x = [dic for dic in matchInfo if dic['season'] == season]
    seasonSorted = sorted(x, key=lambda entry: entry['date'])
    matchday = 1
    counter = 1
    print 'Season ' + season + ' has ' + str(len(seasonSorted)) + ' games.'  
    secondHalf = False
    for match in seasonSorted:
        match['matchday'] = matchday
        secondLeg = match['teams'].split('-')[1] + '-' + match['teams'].split('-')[0]
        try:
            second = search_entry('teams', secondLeg, seasonSorted)[0]
        except:
            second['id'] = 'Missing'
        match['reMatch ID'] = second['id']

        if counter == 9:
            counter = 0
            matchday += 1
        counter += 1
    matchInfos.extend(seasonSorted)
        
saveData = data
matchesCorrected = []
for entry in tqdm(data):
    if '_' in entry['matchIdentifier']:
        identifier = 'matchIdentifier'
    else:
        identifier = 'matchdayIdentifier'
    matchSeason = entry[identifier].split('_')[0]
    matchTeams = entry[identifier].split('_')[3]
    info = [dic for dic in matchInfos if dic['season'] == matchSeason 
            and matchTeams.split('-')[0] in dic['teams'].split('-')[0] 
            and matchTeams.split('-')[1] in dic['teams'].split('-')[1]]
    if info == []:
        print 'No info for:'
        print matchSeason
        print matchTeams
        break
    info = info[0]
    entry['matchID'] = info['id']
    entry['matchday'] = info['matchday']
    entry['reMatchID'] = info['reMatch ID']
    entry['date'] = info['date']
    del entry['matchdayIdentifier']
    del entry['matchIdentifier']
    matchesCorrected.append(info)

# All matches have been updated    
len(matchesCorrected) == len(data)

# make all players that 
matchIDS = [dic['matchID'] for dic in data]
matchIDS = list(set(matchIDS))

# check whether games have been missed:
validateIDS  = [mID['id'] for mID in matchInfos]

# all match IDS that should be in data but are not yet:
set(validateIDS) - set(matchIDS)
# if set is empty, everything is fine

# above, only substitue player that came into the game were tagged as 
# substituted, now the players that left the pitch will be tagged as well
numberPlayers = []
for ID in tqdm(matchIDS):
    match = search_entry('matchID', ID, data)
    numberPlayers.append(len(match) / float(2))
    
    # clean sheet    
    score = match[0]['score'].split(' : ')
    
    homeCleanSheet = False
    awayCleanSheet = False
    if score[1] == '0':
        homeCleanSheet = True
    if score[0] == '0':
        awayCleanSheet = True

    # compute saves
    onTargetHome = 0
    onTargetAway = 0
    clearanceHome = 0
    clearanceAway = 0
    goalsHome = 0
    goalsAway = 0
    for player in match:
        # clean sheet
        if player['pitch'] == 'home':
            player['cleanSheet'] = homeCleanSheet
        else:
            player['cleanSheet'] = awayCleanSheet
        if player['position'] != 'GK':
            player['saves'] = '0'
            player['savesAccuracy'] = '0'
            if player['pitch'] == "home":
                onTargetHome += int(player['shotOnTarget'])
                clearanceHome += int(player['bigClearance'])
                goalsHome += int(player['goalScored'])
            else:
                onTargetAway += int(player['shotOnTarget'])
                clearanceAway += int(player['bigClearance'])
                goalsAway += int(player['goalScored'])
                
    goaliHome = [player for player in match if player["position"] == 'GK' 
                    and player['pitch'] == 'home'][0]
     
    # saves of home goali are claculated by shot on target of opponent
    # minus saves on the line of the defense minus shots that were not saved(goals)              
    goaliHome['saves'] = onTargetAway - clearanceHome - goalsAway
    
    if (onTargetAway - clearanceHome) > 0:
        goaliHome['savesAccuracy'] = 100 - (goalsAway / float(onTargetAway 
                                            - clearanceHome) * 100)
    else:
        goaliHome['savesAccuracy'] = 100
    
    goaliAway = [player for player in match if player["position"] == 'GK' 
                    and player['pitch'] == 'away'][0]
                    
    goaliAway['saves'] = onTargetHome - clearanceAway - goalsHome
    
    if (onTargetHome - clearanceAway) > 0:
        goaliAway['savesAccuracy'] = 100 - (goalsHome / float(onTargetHome
                                            - clearanceAway) * 100)
    else:
        goaliAway['savesAccuracy'] = 100
     
    
    minutes = [dic['playedMinutes'] for dic in match 
            if dic['position'] != 'Sub']
    fullMinutes = int(np.median(map(int, minutes)))        
    subPlayers = [dic for dic in match 
            if dic['playedMinutes'] != str(fullMinutes) 
            and dic['playedMinutes'] != '0']
    for player in subPlayers:
        player['substituted'] = True
    
    # calculate saves of goalis that have been substituted
    if goaliHome['substituted'] or goaliHome['redCard'] == 0:
        # all saves
        savesTotal = goaliHome['saves']
        goaliMinShare = int(goaliHome['playedMinutes']) / float(fullMinutes)
        goaliHome['saves'] = goaliMinShare * savesTotal
        # find substitute of goali
        goaliSub = [dic for dic in match 
            if dic['playedMinutes'] == str(fullMinutes 
            - int(goaliHome['playedMinutes']) )  and
            dic['position'] == 'Sub']
        if len(goaliSub) != 1:
            names = []
            for goali in goaliSub:
                names.append(goali['name'])
            for name in names:
                for pos in search_entry('name', name, data):
                    if pos == 'GK':
                        goaliSub = goaliSub[names.index(name)]
                        break
                if len(goaliSub) == 1:
                    break
            # if no other goali was found, just take the first entry
            if len(goaliSub) == 0:
                # set goali saves to all saves
                goaliHome['saves'] = savesTotal
            else:
                goaliSub = goaliSub[0]
        else:
            goaliSub = goaliSub[0]
        if len(goaliSub) == 1:
            goaliSub['saves'] = (1 - goaliMinShare) * savesTotal
            goaliSub['savesAccuracy'] = goaliHome['savesAccuracy']
        
    if goaliAway['substituted'] or goaliAway['redCard'] == 0:
        # all saves
        savesTotal = goaliAway['saves']
        goaliMinShare = int(goaliAway['playedMinutes']) / float(fullMinutes)
        goaliAway['saves'] = goaliMinShare * savesTotal
        # find substitute of goali
        goaliSub = [dic for dic in match 
            if dic['playedMinutes'] == str(fullMinutes 
            - int(goaliAway['playedMinutes'])) and
            dic['position'] == 'Sub']
        if len(goaliSub) != 1:
            names = []
            for goali in goaliSub:
                names.append(goali['name'])
            for name in names:
                for pos in search_entry('name', name, data):
                    if pos == 'GK':
                        goaliSub = goaliSub[names.index(name)]
                        break
                if len(goaliSub) == 1:
                    break
            # if no other goali was found, just take the first entry
            if len(goaliSub) == 0:
                # set goali saves to all saves
                goaliHome['saves'] = savesTotal
            else:
                goaliSub = goaliSub[0]
        else:
            goaliSub = goaliSub[0]
        if len(goaliSub) == 1:
            goaliSub['saves'] = (1 - goaliMinShare) * savesTotal
            goaliSub['savesAccuracy'] = goaliAway['savesAccuracy']
        
        
# correct names of teams
teams = [entry["team"] for entry in data]
uniqueTeams = list(set(teams))

for entry in tqdm(data):
    entry['team'] = correct_teamname(entry['team'])
        
# check if team names are unquie now
teamsNew = [entry["team"] for entry in data]
uniqueTeamsNew = list(set(teamsNew))
uniqueTeamsNew.sort()

dataSorted = sorted(data, key=lambda entry: entry['date'])
write_to_csv(dataname + '_validated.csv', dataSorted, append = False)