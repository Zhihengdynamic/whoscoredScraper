# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 15:48:17 2016

@author: JK
"""

# Bild Rating scraper



# import external modules
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

# bild Ratings
bildURL = 'http://www.bild.de/bundesliga/'

# initialise selenium
profile = webdriver.FirefoxProfile()
profile.set_preference('network.http.max-connections', 5000)
profile.update_preferences()

browser = webdriver.Firefox(profile)

# go to bild BL page
browser.get(bildURL)

# initialise outputList
bildOutput = []

# get links for all BL teams
teams = browser.find_element_by_xpath('//*[@class="teams"]')
teamList = teams.find_element_by_tag_name("ol").find_elements_by_tag_name('li')
teamLinks = [link.find_element_by_css_selector('a').get_attribute('href') for link in teamList]

# get widget links (iframe)
widgetLinks = []
checkedLinks = []
while len(widgetLinks) != 18:
    for link in teamLinks:
        widLink = '' 
        if link not in checkedLinks:
            browser.get(link)
            iframes =  browser.find_elements_by_tag_name("iframe")
            widLink = [ilink.get_attribute('src') for 
                        ilink in iframes if 'widget-stats-team' in ilink.get_attribute('src')][0]
            if widLink != '':
                widgetLinks.append(widLink)
                checkedLinks.append(link)
            time.sleep(random.sample([4, 6], 1)[0])
    print 'Widget Links has length ' + str(len(widgetLinks))

# go to every team page and get all information
bildOutput = []
for wlink in widgetLinks:
    team = ''
    while team == '':
        browser.set_page_load_timeout(60)
        browser.get(wlink)
        time.sleep(random.sample([10, 15], 1)[0])
        try:
            team = correct_teamname(browser.find_element_by_xpath('//*[@class="team-away current-team"]').text)
        except:
            pass
    browser.find_element_by_xpath('//*[@id="squad"]').click()
    time.sleep(random.sample([3, 6], 1)[0])
    playerList = browser.find_elements_by_tag_name('tr')
    for entry in playerList:
        if '(' in entry.text:
            nameRaw = entry.text.split('(')[0]
            try:
                name = nameRaw.split(', ')[1] + nameRaw.split(', ')[0]
            except:
                name = nameRaw
            addInfo = entry.text.split(') ')[1].split(' ')
            playerDic = {}
            playerDic['name'] = name.encode('ascii', 'replace')
            playerDic['position'] = entry.get_attribute('class').split(' ')[1]
            playerDic['team'] = team
            playerDic["games"] = playerDic["goals"] = 0
            playerDic["rating"] = '-'
            try:
                playerDic["games"] = addInfo[1]
            except:
                pass
            try:
                playerDic["goals"] = addInfo[2]
            except:
                pass
            try:
                playerDic["rating"] = addInfo[3]
            except:
                pass
            # save in output
            bildOutput.append(playerDic)

# close browser after work is done
browser.quit()

# write data to disk
write_to_csv("bildRatings_complete.csv", bildOutput)


    
