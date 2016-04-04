# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 15:48:17 2016

@author: JK
"""

# Rating scraper



# import external modules
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import time
import random

import os
with open('python-wd.txt', 'r') as f:
    wdPath = f.read()
f.closed

os.chdir(wdPath)

# import internal modules
from scraper_helpers import correct_teamname
from file_helpers import write_to_csv


def ExtractKickerInfo(element, lastEntry):
    playerDic = {}
    remainerTDS = element.findAll("td")
    name = element.findAll("a", {"class": "link"})[0].contents[0]
    # format the name according to other data
    if ',' in name:
        playerDic['name'] = name.split(', ')[1] + ' ' +  name.split(', ')[0]
    else:
        playerDic['name'] = name
    team = remainerTDS[2].contents[0]
    # if the previous player is of the same team, kicker omits the team
    # this is corrected with the team of the lastEntry
    if team == u'\n':
        playerDic['team'] = lastEntry['team']
    else:
        team = element.findAll("a", {"class": "link verinsLinkBild"})[0].contents[0]
        playerDic['team'] = correct_teamname(team)
    # if the previous player played on the same position, 
    # kicker omits it, this is corrected with the position of the lastEntry
    if remainerTDS[3].contents[0] == u'?':
        playerDic['position'] = lastEntry['position']
    else:
        playerDic['position'] = remainerTDS[3].contents[0]
    playerDic['gamesPlayed'] = remainerTDS[4].contents[0]
    playerDic['gamesRated'] = remainerTDS[5].contents[0]
    # get rating and replace decimal comma with dot
    playerDic['rating'] = remainerTDS[6].contents[0].replace(',', '.')
    
    return playerDic
    
def ScrapeTableContent(browser):
    # scrape content of first page
    content = (browser.page_source).encode('ascii', 'replace')
    soup = BeautifulSoup(''.join(content))
    
    # get all tables with player data
    tables = soup.findAll("tbody")
    
    # get all tables that contain player rating data
    tableList = []
    for tab in tables:
        tableList.extend(tab.findAll("tr", {"class": re.compile('fest')}))
    
    kickerList = []
    first = True
    for element in tableList:
        # the last processed entry has to be inputed into ExtractKickerInfo
        # function because Kicker omits team, position if it's the same as the
        # last entry
        if first:
            first = False
            currentEntry = lastEntry = ExtractKickerInfo(element, element)
        else:
            currentEntry = ExtractKickerInfo(element, lastEntry)
        kickerList.append(currentEntry)
        lastEntry = currentEntry
    return kickerList

# Kicker Ratings
kickerMainURL = 'http://www.kicker.de/news/fussball/bundesliga/'
ratingURL = 'topspieler/1-bundesliga/2015-16/topspieler-der-saison.html'

kickerURL = kickerMainURL + ratingURL

# initialise selenium
profile = webdriver.FirefoxProfile()
profile.set_preference('network.http.max-connections', 5000)
profile.update_preferences()

browser = webdriver.Firefox(profile)

# go to rating url
browser.get(kickerURL)

# initialise outputList
kickerOutput = []

# get to first page of ratings (normally the URL should direct to first 
# page already)
firstPage = browser.find_element_by_xpath('//*[@class="blaettern_anfang"]')
if firstPage.get_attribute('href') is not None:
    firstPage.click()
else:
    #get a time stamp
    timeStamp = browser.find_element_by_xpath('//*[@class="timeStamp"]').text
    # time stamp is unfortunately in German format, but not important
    timeStamp = timeStamp.split(": ")[1]
    time.sleep(1)
    
    

nextpage = browser.find_element_by_xpath('//*[@id="ctl00_PlaceHolderContent_topspieler_blaettern_topspielersaison_PagerForward"]')

count = 1
while nextpage.get_attribute('href') is not None:
    # go to next page
    nextpage.click()
    # sleep for some seconds to not be suspicious
    time.sleep(random.sample([3, 4, 5], 1)[0])
    # get new next page
    nextpage = browser.find_element_by_xpath('//*[@id="ctl00_PlaceHolderContent_topspieler_blaettern_topspielersaison_PagerForward"]')
    # print progress
    print 'Table ' + str(count) + ' just scraped.'
    count += 1
    if count > 20:
        print 'Stop procedure, something went wrong here.'

# all data tables are loaded into browser, data can be extracted now
kickerOutput.extend(ScrapeTableContent(browser))
# close browser after work is done
browser.quit()

# write data to disk
write_to_csv("kickerRatings.csv", kickerOutput)