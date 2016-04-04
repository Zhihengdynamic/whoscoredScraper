# -*- coding: utf-8 -*-
"""
Created on Thu Mar 03 13:54:15 2016

@author: JK
"""

# Exernal modules

from bs4 import BeautifulSoup
import time
from selenium import webdriver

# change wd
import os
with open('python-wd.txt', 'r') as f:
    wdPath = f.read()
f.closed

os.chdir(wdPath)

# import local functions
from file_helpers import write_to_disk
from file_helpers import open_from_disk

from scraper_helpers import get_match_ids
from scraper_helpers import extract_teams
#----------------------------------------------------------------------



# Main
seed_urls = ['https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/4336',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/3863',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/3424',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/2949',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/2520',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/1903']
#seed_urls = ['https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/4336']
            
            
path = 'player_stats.csv'
phantomscrape = True
phantomscrapeTables = True
allMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


matchIdTeamLink = []

#sync_lists('scrapedDates', 'matchIdsSaved')

for seed_url in seed_urls:
    startseason = time.time()
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.http.max-connections', 5000)
    profile.update_preferences()

    # use phantom?
    if phantomscrape:
        browser = webdriver.PhantomJS('./phantomjs.exe')
    else:
        browser = webdriver.Firefox(profile)
    
    browser.get(seed_url)
        
    browser.find_element_by_xpath('//*[@id="date-config-toggle-button"]').click()
    
    content = browser.page_source
    soup = BeautifulSoup(''.join(content))
    
    firstyear = soup.findAll("td", {"class": " selectable"})[0].contents[0]
    
    
    years = [firstyear, str(int(firstyear) + 1)]
    if os.path.isfile('scrapedDates.txt'):
        scrapedDays = open_from_disk("scrapedDates")
    else:
        scrapedDays = []
    if len(scrapedDays) > 0:
        matchdayNr = len(scrapedDays) / 9
    else:
        matchdayNr = 1
    matchIds = []
    
    for year in years:
        browser.find_element_by_xpath("//table[@class='years']//tbody//tr//td[@data-value=" + year + "]").click()
        time.sleep(4)
        contentYear = browser.page_source
        soupYear = BeautifulSoup(''.join(contentYear))
        totalMonths = soupYear.findAll("table", {"class": "months"})[0].findAll("td", {"class": " selected selectable"})
        totalMonths.extend(soupYear.findAll("table", {"class": "months"})[0].findAll("td", {"class": " selectable"}))
        
        months = map(lambda month : month.attrs['data-value'], totalMonths)
        months.sort(key = int)

        for monthIndex in months:
            not_correct_month = True
            while not_correct_month:
                browser.find_element_by_xpath("//table[@class='months']//tbody//tr//td[@data-value=" + monthIndex + "]").click() 
                time.sleep(4)
                contentMonth = browser.page_source
                soupMonth = BeautifulSoup(''.join(contentMonth)) 
                month = soupMonth.findAll("td", {"class": " selected selectable"})[1].contents[0]  
                selectables = soupMonth.findAll("table", {"class": "days"})[0].findAll("td", {"class": " selected selectable"})
                selectables.extend(soupMonth.findAll("table", {"class": "days"})[0].findAll("td", {"class": " selectable"}))
                
                if month == allMonths[int(monthIndex)]:
                    not_correct_month = False
                else:
                    print 'Not correct month!'
                    time.sleep(4)
            for day in selectables:
                scrapedDays = open_from_disk("scrapedDates")
                if month + ' ' + day.text + ' ' + year in scrapedDays:
                    continue
                write_to_disk(scrapedDays, 'scrapedDates')
                browser.find_element_by_xpath("//table[@class='days']//tbody//tr//td[@data-value=" + day.attrs["data-value"] + "]").click()
                time.sleep(3)
                contentDay = browser.page_source
                soupDay = BeautifulSoup(''.join(contentDay)) 
                
                date = month + ' ' + day.contents[0] + ' ' + year
                
                #headers = soup.findAll("tr", {"class": "rowgroupheader"})
                
                fixTable = soupDay.findAll("table", {"id": "tournament-fixture"})[0].findAll('tr')
                                
                
                scraper = False
                counter = 0
                matchdayIds = []
                for entry in fixTable:
                    if entry.attrs['class'][0] == 'rowgroupheader':
                        scrapedDays = open_from_disk("scrapedDates")
                        if entry.text.split(', ')[1] not in scrapedDays:
                            currentDate = entry.text.split(', ')[1]
                            scrapedDays.append(currentDate)
                            print 'Day ' + entry.text + ' has been scraped.'
                            scraper = True
                            write_to_disk(scrapedDays, 'scrapedDates')
                        else:
                            scraper = False
                    else:
                        if scraper:
                            matchIdDate = [get_match_ids(entry)[0] + '-' + currentDate]
                            matchIdTeam = [get_match_ids(entry)[0] + '_' +
                                extract_teams(entry)[0] + '-' + extract_teams(entry)[1] 
                                + '_' + currentDate]

                            matchIdTeamLink.extend(matchIdTeam)
                            matchdayIds.extend(matchIdDate)
                    #matchIds.extend(get_match_ids(entry))
                            
write_to_disk(matchIdTeamLink, 'matchIdTeamLink')               