# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 17:23:35 2016

@author: Jonathan Klaiber
"""

import os
os.chdir('C:/Users/Besitzer/Tresor/john.locker/Mega/UGent Statistical Data Analysis/master thesis/repository') 
from file_helpers import open_from_csv
from file_helpers import open_from_disk
from file_helpers import write_to_csv
import datetime
import sys
import numpy as np


data = open_from_csv('player_stats')

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
for entry in data:
    # set substitution players game time to zero
    entry['Substituted'] = False
    if entry['Position'] == 'Sub':
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
            entry['Substituted'] = True
       

matchID = open_from_disk('matchIdTeamLink')

def search_entry(column, term, data):
    return [dic for dic in data if dic[column] == term]

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
        second = search_entry('teams', secondLeg, seasonSorted)[0]
        match['reMatch ID'] = second['id']

        if counter == 9:
            counter = 0
            matchday += 1
        counter += 1
    matchInfos.extend(seasonSorted)
        
saveData = data
counter = 1
matchesCorrected = []
for entry in data:
    matchSeason = entry['matchIdentifier'].split('_')[0]
    matchTeams = entry['matchIdentifier'].split('_')[3]
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
    entry['ReMatchID'] = info['reMatch ID']
    entry['date'] = info['date']
    del entry['matchdayIdentifier']
    del entry['matchIdentifier']
    sys.stdout.write('\r')
    sys.stdout.write(str(round(counter / float(len(data)), 3) * 100) + '% done.')
    sys.stdout.flush()
    counter += 1
    matchesCorrected.append(info)

# All matches have been updated    
len(matchesCorrected) == len(data)

# make all players that 
matchIDS = [dic['matchID'] for dic in data]
matchIDS = list(set(matchIDS))

# above, only substitue player that came into the game were tagged as 
# substituted, now the players that left the pitch will be tagged as well
numberPlayers = []
for ID in matchIDS:
    match = search_entry('matchID', ID, data)
    numberPlayers.append(len(match) / float(2))
    minutes = [dic['playedMinutes'] for dic in match 
            if dic['Position'] != 'Sub']
    subPlayers = [dic for dic in match 
            if dic['playedMinutes'] != str(int(np.median(map(int, minutes))))]
    for player in subPlayers:
        player['Substituted'] = True
        
dataSorted = sorted(data, key=lambda entry: entry['date'])
write_to_csv('player_stats_validated.csv', dataSorted, append = False)