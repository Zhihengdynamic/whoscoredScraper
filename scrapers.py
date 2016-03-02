# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 10:46:23 2016

@author: Jonathan Klaiber
"""

# external modules
import re
from selenium import webdriver
from random import randint
import time
from bs4 import BeautifulSoup

# internal moduels
from python_helpers import merge_dicts
from scraper_helpers import extract_value

# scrape with phantomJS
phantomscrapeTables = True

def player_stat_scraper(datalist):
    returnList = []
    stats = ["ShotsTotal ",
             "ShotOnTarget ",
             "KeyPassTotal ",
             "PassSuccessInMatch ",
             "DuelAerialWon ",
             "Touches ",
             "rating ",
             "DribbleWon ",
             "FoulGiven ",
             "OffsideGiven ",
             "Dispossessed ",
             "Turnover ",
             "TackleWonTotal ",
             "InterceptionAll ",
             "ClearanceTotal ",
             "ShotBlocked ",
             "FoulCommitted ",
             "TotalPasses ",
             "PassSuccessInMatch ",
             "PassCrossTotal ",
             "PassCrossAccurate ",
             "PassLongBallTotal ",
             "PassLongBallAccurate ",
             "PassThroughBallTotal ",
             "PassThroughBallAccurate "]
    firstBody = True
    for body in datalist:
        players = body.findAll('tr')
        for i in range(len(players)):
            player = players[i]
            if firstBody:
                playerDic = {}
                findName = re.findall("Players(.*?)span" , str(player))
                playerDic['Name'] = re.findall(">(.*?)<", findName[0])[0].strip()
                playerDic['Position'] = re.findall('"player-meta-data">, (.*?)<' , str(player))[0].strip()
                #print 'Scraping data of '+ playerDic['Name'] + ' now.'
                specialEvents = check_special_events(player)
                playerDic = merge_dicts(playerDic, specialEvents)
            else:
                playerDic = returnList[i]
            for stat in stats:
                if extract_value(player, stat) is not '':
                    playerDic[stat.strip()] = extract_value(player, stat)
            if firstBody:
                returnList.append(playerDic)
            else:
                returnList[i] = playerDic
        firstBody = False
    return returnList
        
def check_special_events(player):
    incidents = player.findAll("span", {"class" : "incident-wrapper"})

    goalScored = 0
    assists = 0
    bigChanceMiss = 0
    bigError = 0
    bigClearance = 0
    yellowCard = False
    redCard = False
    playedMinutes = 'FT'
    for incident in incidents:
        for event in incident.findAll("span", {"class" : "incident-icon"}):
            datatype = re.findall('data-type="(.*?)">' , str(event))[0]
            if datatype == '18':
                playedMinutes = re.findall('data-minute="(.*?)"' , str(event))[0]
            if datatype == '19':
                playedMinutes = 'FT - ' + re.findall('data-minute="(.*?)"' , str(event))[0]
            if datatype == '17':
                if len(re.findall('redcard' , str(event))) == 1:
                    redCard = True
                if len(re.findall('yellowcard' , str(event))) == 1:
                    yellowCard = True
            if datatype == '16':
                goalScored += 1
            if datatype == '1':
                assists += 1
            if datatype == '14' or datatype == "15":
                bigChanceMiss += 1
            if datatype == "51":
                bigError += 1
            if datatype == "10":
                bigClearance += 1
                
    return {'goalScored': goalScored,
            'assists': assists,
            'bigChanceMiss' : bigChanceMiss,
            'bigError' : bigError,
            'bigClearance' : bigClearance,
            'yellowCard' : yellowCard,
            'redCard' : redCard,
            'playedMinutes': playedMinutes}
            
           
def scrape_single_match(season, match_url, matchdayIdentifier, phantom = True):

    match_centre_url = match_url + '/Live'
    player_stats_url = match_url + "/LiveStatistics"

    # make browser profile
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.http.max-connections', 5000)
    profile.update_preferences()
    #browser = webdriver.Firefox(profile)
    
    
    #/Germany-Bundesliga-' + season + '-'
    
    if phantom:
        browser = webdriver.PhantomJS('./phantomjs.exe')
    else:
        browser = webdriver.Firefox(profile)
        
    # waiting time
    wtime = [3, 4]

    #load all javascript tables
    data = []
    while len(data) != 8:
        
        browser.get(player_stats_url)
        time.sleep(randint(1, 3))
        tables = ['summary', 'offensive', 'defensive', 'passing']
        for tab in tables:
            try:
                browser.find_element_by_css_selector("a[href*='#live-player-home-" + tab + "']").click()
                time.sleep(randint(wtime[0], wtime[1]))
                browser.find_element_by_css_selector("a[href*='#live-player-away-" + tab + "']").click()
                time.sleep(randint(wtime[0], wtime[1]))
            except:
                print "Problems with loading webpage in browser."
                time.sleep(120)
                print 'Sleeping for two minutes. They I will try again'
        # get content
        content = browser.page_source
        soup = BeautifulSoup(''.join(content))
    
        # player data    
        data = soup.findAll("tbody", {"id": "player-table-statistics-body"})
        
        print 'Data has length ' + str(len(data)) + " at the moment."
        
    
    # home data
    home = data[:4]
    # away data
    away = data[4:]
    
    homeDic = player_stat_scraper(home)
    for player in homeDic:
        player['pitch'] = 'home'
    awayDic = player_stat_scraper(away)
    for player in awayDic:
        player['pitch'] = 'away'
    print 'Player stat scraping done.'
    
    # scrape match info
    browser.get(match_centre_url)
    matchContent = browser.page_source
    matchSoup = BeautifulSoup(''.join(matchContent))
    
    browser.quit()
  
    
    timeInfo = matchSoup.find("div", {"class": "timeline-minute has-been-played is-current-minute is-end-of-period"})
    if str(timeInfo) == 'None':
        fullMinutes = '90'
    else:
        fullMinutes = re.findall('data-minute="(.*?)"' , str(timeInfo))[0]
    teams = matchSoup.findAll("a", {"class": "team-link"})
    homeTeam = re.findall('>(.*?)</a>' , str(teams[0]))[0]
    awayTeam = re.findall('>(.*?)</a>' , str(teams[1]))[0]
    result = matchSoup.findAll("td", {"class": "result"})
    score = re.findall('>(.*?)<' , str(result[0]))[0]
    homeScore = re.findall('>(.*?) :' , str(result[0]))[0]
    awayScore = re.findall(': (.*?)<' , str(result[0]))[0]
    
    if int(homeScore) > int(awayScore):
        homeResult = 'win'
        awayResult = 'defeat'
    elif int(homeScore) < int(awayScore):
        homeResult = 'defeat'
        awayResult = 'win'
    else:
        homeResult = 'tie'
        awayResult = 'tie'
        
    date = re.findall(' (.*?)<' , str(matchSoup.findAll('dd')[4]))[0]
    
    match_data = []
    for player in homeDic + awayDic:
        player['matchdayIdentifier'] = matchdayIdentifier
        player['matchIdentifier'] = matchdayIdentifier + "_" + homeTeam + '-' + awayTeam
        player['score'] = score
        player['date'] = date
        player['season'] = season
        if player['playedMinutes'] == 'FT':
            player['playedMinutes'] = fullMinutes
        elif 'FT' in player['playedMinutes']:
            player['playedMinutes'] = str(int(fullMinutes) - int(player['playedMinutes'][5:]))
        if player['pitch'] == "home":
            player['team'] = homeTeam
            player['scoreTeam'] = homeScore
            player['result'] = homeResult
        if player['pitch'] == "away":
            player['team'] = awayTeam
            player['scoreTeam'] = awayScore
            player['result'] = awayResult
        match_data.append(player)
    print 'Gerneral info scraping done.'   
    return match_data

def scrape_matchday(matchIds, matchdayNr, season):
  
    matchdayData = []
    matchdayIdentifier = season + '_matchday_' + str(matchdayNr)
    start = time.time()
    togo = 0
    for matchDate in matchIds:
        mId = matchDate.split('-')[0]
        match_url = 'http://www.whoscored.com/Matches/' + mId
        attempts = 0
        matchday = []
        while len(matchday) == 0:
            try:
                matchday = scrape_single_match(season, match_url, matchdayIdentifier, phantom = phantomscrapeTables)
            except:
                matchday = scrape_single_match(season, match_url, matchdayIdentifier,  phantom = phantomscrapeTables)
                attempts += 1
                print 'Match Id:' + mId
                print 'Attempts to get match data:' + str(attempts)
        matchdayData.append(matchday)
        togo += 1
        print "Match ID " + mId + ' just scraped. ' + str(togo) + "/" + str(len(matchIds)) + ' matches done.'
    
       
    end = time.time()
    print 'Scraping of matchday took ' + str(round((end - start) / 60, 2)) + " minutes."
    return [matchdayData, matchdayIdentifier]