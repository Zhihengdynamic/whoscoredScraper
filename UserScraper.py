# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 15:48:17 2016

@author: JK
"""

# SPOX (Comunio) Rating scraper

# import external modules
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import random
import re
from tqdm import tqdm

import os
with open('python-wd.txt', 'r') as f:
    wdPath = f.read()
f.closed

os.chdir(wdPath)

# import internal modules
from scraper_helpers import correct_teamname
from file_helpers import write_to_csv
from python_helpers import search_dicts


def CreateSpoxURL(spieltagNr):
    # nr is spieltagnur
    nr = str(spieltagNr)
    spoxURL1 = ('http://www.spox.com/de/sport/fussball'
            '/bundesliga/saison2015-2016/spieltag-')
    spoxURL2 = "/aufstellungen-noten-einzelkritik-"
    spoxURL3 = "-spieltag.html"
    spoxURL4 = "/aufstellungen-einzelkritik-noten-"
    spoxURL5 = "http://www.spox.com/de/sport/fussball/bundesliga/1508/Artikel/"
    spoxURL6 = "-spieltag-aufstellungen-einzelkritik-noten.html"
    spoxURL7 = "/voraussichtliche-aufstellungen-"

    # go to rating url
    if nr in ["19", "20"] or nr >= "22":
        curURL = spoxURL1 + nr + spoxURL2 + nr + spoxURL3
    elif nr == "1":
        curURL = spoxURL1 + nr + spoxURL7 + nr + spoxURL3
    elif nr == "2":
        curURL = spoxURL1 + nr + spoxURL4 + nr + spoxURL3
    elif nr == "3":
        curURL = spoxURL5 + nr + spoxURL6
    elif nr in ["7", "8"]:
        curURL = spoxURL1 + nr + spoxURL4[:len(spoxURL4) - 1] + '.html'
    else:
        curURL = spoxURL1 + nr + spoxURL2[:len(spoxURL2) - 1] + '.html'
    return curURL

def ExtractUserRatingPage(soup, spieltagNr):
    # get all divs that are realted to the ratings
    allDivs = soup.findAll('div', {'class': re.compile('user_noten_')})
    # find the team headers for the tow teams
    teams = soup.findAll('div', {'class':'user_noten_team_top'})
    # split the all div list in divs related to home and away team
    homePlayers = allDivs[:allDivs.index(teams[1])]
    # filter the home team name
    homeTeam = teams[0].find('div', {'class':'user_noten_team_top_col1'})
    homeTeam = homeTeam.text.replace(' ', '').split("\n")
    homeTeam = correct_teamname([sp for sp in homeTeam if len(sp) > 0 ][0])
    # split the all div list in divs related to home and away team
    awayPlayers = allDivs[allDivs.index(teams[1]):]
    # filter the away team name
    awayTeam = teams[1].find('div', {'class':'user_noten_team_top_col1'})
    awayTeam = awayTeam.text.replace(' ', '').split("\n")
    awayTeam = correct_teamname([sp for sp in awayTeam if len(sp) > 0 ][0])
    
    # make output list
    spieltagList = []
    playerActive = False
    # loop trough all divs associated with home or away team
    for player, team in (zip(homePlayers, [homeTeam] * len(homePlayers)) 
                        + zip(awayPlayers, [awayTeam] * len(awayPlayers))):
        # create new player dic when no other dic is active                    
        if not playerActive:
            playerDic = {}
        # look for divs that contain name, user rating or sportal rating
        foundName = player.find("div", 
                                {"class": 'user_noten_player_top_col1'})
        foundUser = player.find("div", 
                                {"class": 'user_noten_player_bottom_col3'})
        foundSpo = player.find("div", 
                               {"class": "user_noten_player_bottom_col4"})
        # if a name is found, activate new player dic
        if foundName is not None:
            playerDic['name'] = foundName.text.replace("\n","")
            playerDic['team'] = team
            playerDic['spieltag'] = spieltagNr
            playerActive = True
        # if user rating is found in div, save it in active player dic
        if foundUser is not None:
            user = foundUser.text
            userInfo = [sp for sp in user.split('\n') if len(sp) > 0 ]
            playerDic['userRating'] = userInfo[0].replace(',', '.')
            playerDic['userRated'] = userInfo[1].split(' ')[0]
        # if sportal rating is found, save player dic and close it
        if foundSpo is not None:
            sportal = foundSpo.text
            playerDic['sportalRating'] = (sportal.replace('\n', '')
                                                 .replace(',', '.'))
            # saveing player dic
            spieltagList.append(playerDic)
            # closing active player dic, next iter will make a new
            playerActive = False
    return spieltagList
    
# initialise selenium
profile = webdriver.FirefoxProfile()
profile.set_preference('network.http.max-connections', 5000)
profile.update_preferences()

browser = webdriver.Firefox(profile)

lastSpieltag = 28
userOutput = []
# tqdm for monitoring progres
for spieltagNr in tqdm(range(1, lastSpieltag + 1)):
    # create appropriate link
    curURL = CreateSpoxURL(spieltagNr)
    # go to link address
    browser.get(curURL)
    # find paage elements that contain game links
    pageElements = browser.find_elements_by_xpath('//*[@class="tlink ospox"]')
    
    # obtain all 9 game links
    pageLinks = []
    for element in pageElements:
        if 'User-Noten' in element.text:
            # there is a broken link for the last game of matchday 2
        # her it is fixed
            if "mario-gomez" in element.get_attribute('href'):
                pageLinks.append("http://www.spox.com/de/sport/fussball/"
                         "bundesliga/saison2015-2016/spieltag-2/spielberichte/"
                         "gladbach-mainz/gladbach-mainz-user-noten.html")
            else:
                pageLinks.append(element.get_attribute('href'))

    # loop trough all games of that matchday
    for link in pageLinks:
        # go to website of that game
        browser.get(link)
        # identify iframe element in wich information is stored
        ele = browser.find_element_by_xpath("//div[@class='artCmp artCmpM']")
        # make browser to switch to iframe object
        browser.switch_to.frame(ele.find_element_by_tag_name("iframe"))
        # reveal ratings that are initially hidden
        uncover = browser.find_elements_by_xpath("//div[@class="
                  "'user_noten_team_top_aufdecken']")
        # click on all four uncover buttons
        for aufdecken in uncover:
            aufdecken.click()
            # sleep quickly (not necessary)
            time.sleep(random.sample([1, 2], 1)[0])
        # extract page content to obtain player into
        content = (browser.page_source).encode('ascii', 'replace')
        soup = BeautifulSoup(''.join(content))
        # get info of all players of the game
        spieltagList = ExtractUserRatingPage(soup, spieltagNr)
        # save game info into general output list
        userOutput.extend(spieltagList)
        # sleep for a moment before going on
        time.sleep(random.sample([5, 7], 1)[0])
        
# close browser after work is done
browser.quit()        
# compute average rating of players
diskOutput = []
nameList = []
for entry in userOutput:
    for col in ['userRating', 'userRated', 'sportalRating']:
        if entry[col] == '':
            entry[col] = 0.0
    if entry['name'] not in nameList:
        nameList.append(entry['name'])
        aggregatedPlayer = {}
        aggregatedPlayer['name'] = entry['name']
        aggregatedPlayer['cumUser'] = float(entry['userRating'])
        aggregatedPlayer['cumUserRated'] = float(entry['userRated'])
        aggregatedPlayer['cumSportal'] = float(entry['sportalRating'])
        aggregatedPlayer['ratedMatchdays'] = 1.0
        diskOutput.append(aggregatedPlayer)
    else:
        ind = search_dicts(diskOutput, 'name', 
                           entry['name'], 
                           returnIndex = True)[0]
        diskOutput[ind]["cumUser"] += float(entry['userRating'])
        diskOutput[ind]['cumUserRated'] += float(entry['userRated'])
        diskOutput[ind]['cumSportal'] += float(entry['sportalRating'])
        diskOutput[ind]['ratedMatchdays'] += 1.0
        
# now divided the summed ratings by the number of ratings to get average
for entry in diskOutput:
    for col in ['cumUser', 'cumUserRated', 'cumSportal']:
        entry[col] = round(entry[col] / entry['ratedMatchdays'], 2)
        

# write data to disk
write_to_csv("userRatings.csv", diskOutput)