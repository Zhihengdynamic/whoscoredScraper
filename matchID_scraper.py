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

try:
    with open('python-wd.txt', 'r') as f:
        wdPath = f.read()
    f.closed
    
    os.chdir(wdPath)
except:
    pass

# import local functions
from file_helpers import write_to_disk
from file_helpers import open_from_disk

from scraper_helpers import get_match_ids
from scraper_helpers import extract_teams
#----------------------------------------------------------------------



# Main
seed_urls = ['https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/5870',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/4336',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/3863',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/3424',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/2949',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/2520',
            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/1903',
            ]
seed_urls = ['https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/5870']
            
ending = '_complete'
path = 'player_stats' + ending + '.csv'

scrapedPath = 'scrapedMatchIdInfo' + ending +'.txt'
scrapedDateFile = 'scrapedMatchIdInfo' + ending

phantomscrape = False
phantomscrapeTables = True
allMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


matchIdTeamLink = open_from_disk('matchIdTeamLink' + ending)
matchIdsSaved = list(set(open_from_disk('matchIdsSaved' + ending)))

# get all saved match (saved in payer_stats.csv file) ids
teamLinkIds = [entry.split('_')[0] for entry in matchIdTeamLink]

missingDates = []
for match in matchIdsSaved:
    curID = match.split('-')[0]
    if curID not in teamLinkIds:
        missingDates.append(match.split('-')[1])
        
missingDates = list(set(missingDates))
# check file
checkIds = open_from_disk(scrapedDateFile)
# remove missing dates
try:
    [checkIds.remove(date) for date in missingDates]
except:
    pass
write_to_disk(checkIds, scrapedDateFile)


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
    if os.path.isfile(scrapedPath):
        scrapedDays = open_from_disk(scrapedDateFile)
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
                scrapedDays = open_from_disk(scrapedDateFile)
                if month + ' ' + day.text + ' ' + year in scrapedDays:
                    continue
                write_to_disk(scrapedDays, scrapedDateFile)
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
                        scrapedDays = open_from_disk(scrapedDateFile)
                        if entry.text.split(', ')[1] not in scrapedDays:
                            currentDate = entry.text.split(', ')[1]
                            scrapedDays.append(currentDate)
                            print 'Day ' + entry.text + ' has been scraped.'
                            scraper = True
                            write_to_disk(scrapedDays, scrapedDateFile)
                        else:
                            scraper = False
                    else:
                        if scraper:
                            try:
                                report = entry.find("td", {"class": "toolbar right"}).find('a').contents[0]
                            except:
                                report = ''
                            if report == 'Match Report':
                                matchIdDate = [get_match_ids(entry)[0] + '-' + currentDate]
                                matchIdTeam = [get_match_ids(entry)[0] + '_' +
                                    extract_teams(entry)[0] + '-' + extract_teams(entry)[1] 
                                    + '_' + currentDate]
    
                                matchIdTeamLink.extend(matchIdTeam)
                                matchdayIds.extend(matchIdDate)
                    #matchIds.extend(get_match_ids(entry))
                                
    endseason = time.time()
    print 'Match Id check of season '+ years[0] + '-' + years[1] +' took ' + str(round((endseason - startseason) / 60, 2)) + " minutes."
    browser.quit()
    write_to_disk(matchIdTeamLink, 'matchIdTeamLink' + ending)
                            
              