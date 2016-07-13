# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 15:48:17 2016

@author: JK
"""

# Rating scraper



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

# Kicker Ratings
kickerURL = 'http://www.kicker.de/news/fussball/bundesliga/vereine/1-bundesliga/2015-16/vereine-liste.html'

# initialise selenium
profile = webdriver.FirefoxProfile()
profile.set_preference('network.http.max-connections', 5000)
profile.update_preferences()

browser = webdriver.Firefox(profile)

# go to rating url
browser.get(kickerURL)

# get links to club sites
teamBody = browser.find_element_by_tag_name('tbody')
teamTable = teamBody.find_elements_by_xpath('//*[@class="fest " or @class="fest alt"]')

teamLinks = [link.find_elements_by_tag_name('td')[2]
                    .find_element_by_css_selector('a')
                            .get_attribute('href') 
                        for link in teamTable]

# initialise outputList
kickerOutput = []

for link in teamLinks:
    # set timeout in case it keeps on loading for a long time
    browser.set_page_load_timeout(60)
    browser.get(link)
    time.sleep(random.sample([3, 6], 1)[0])
    team = correct_teamname(browser
                            .find_element_by_xpath('//*[@class="verinsLinkBild"]')
                            .get_attribute('title'))
    teamTab = (browser.find_element_by_xpath('//*[@id="kader_subcont"]')
                        .find_elements_by_tag_name('tr'))
    for tab in teamTab:
        playerDic = {}
        if tab.get_attribute('class') == '' or tab.get_attribute('class') == 'alt':
            if '(' not in tab.text and '.' not in tab.text:
                position = tab.text
            elif '(' in tab.text:
                nameRaw = tab.text.split(' (')[0]
                try:
                    name = nameRaw.split(', ')[1] + ' ' + nameRaw.split(', ')[0]
                except:
                    name = nameRaw
                playerDic['name'] = name.encode('ascii', 'replace')
                playerDic['team'] = team
                playerDic['position'] = position
                playerDic["games"] = playerDic["goals"] = 0
                playerDic["rating"] = '-'
                addInfo = tab.text.split(') ')[1].split(' ')
                if addInfo[1] != '':
                    playerDic["games"] = addInfo[1]
                if addInfo[2] != '':
                    playerDic["goals"] = addInfo[2]
                if addInfo[3] != '':
                    playerDic["rating"] = addInfo[3].replace(',', '.')
                # save in output
                kickerOutput.append(playerDic)
                        
# close browser after work is done
browser.quit()

# write data to disk
write_to_csv("kickerRatings_complete_new.csv", kickerOutput)