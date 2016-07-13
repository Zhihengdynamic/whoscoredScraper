# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 15:48:17 2016

@author: JK
"""

# Bild Rating scraper



# import external modules
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import random

import os
try:
    with open('python-wd.txt', 'r') as f:
        wdPath = f.read()
    f.closed
    os.chdir(wdPath)
except:
    pass

# import internal modules
from scraper_helpers import correct_teamname
from file_helpers import write_to_csv

def ExtractBildInfo(element):
    playerDic = {}
    # scrape all necessary data
    name = info[1].text
    if ',' in name:
        playerDic['name'] = name.split(', ')[1] + ' ' +  name.split(', ')[0]
    else:
        playerDic['name'] = name
    team = info[2].text
    playerDic['team'] = correct_teamname(team)
    playerDic['position'] = info[3].text
    playerDic['gamesPlayed'] = info[4].text
    playerDic['gamesRated'] = info[5].text
    playerDic['rating'] = info[6].text.replace(',', '.')
    return playerDic
         

# bild Ratings
bildURL = 'http://sportdaten.bild.de'

# initialise selenium
profile = webdriver.FirefoxProfile()
profile.set_preference('network.http.max-connections', 5000)
profile.update_preferences()

browser = webdriver.Firefox(profile)

# go to rating url
browser.get(bildURL)

# initialise outputList
bildOutput = []

# go to top player page that contains the ratings
browser.find_element_by_xpath('//*[@class="wfb-li-ranking-bildscore"]').click()

#sleep for some time
time.sleep(random.sample([10, 12], 1)[0])

# find button to click on next page
nextpage = browser.find_element_by_xpath('//*[@class="next wfb-unselectable"]')

# while next page is clickable, click on it
bildOutput = []
first = True
while nextpage.is_displayed():
    if first:
        first = False
    else:
        nextpage.click()
    # extract data
    content = (browser.page_source).encode('ascii', 'replace')
    soup = BeautifulSoup(''.join(content))

    # get all tables with player data
    datatables = soup.find("tbody", {"class": 'data-body'}).findAll('tr')
    
    for tab in datatables:
        info = tab.findAll('td')
        bildOutput.append(ExtractBildInfo(info))
    #sleep for some time
    time.sleep(random.sample(range(5,8), 1)[0])
    nextpage = browser.find_element_by_xpath('//*[@class="next wfb-unselectable"]')

# close browser after work is done
browser.quit()

# write data to disk
write_to_csv("bildRatings_complete.csv", bildOutput)


    
