"""
Created on Wed Mar 02 10:46:23 2016

@author: JK
"""
# Exernal modules
import os
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import math
import schedule

# change wd to rep location
with open('python-wd.txt', 'r') as f:
    wdPath = f.read()
f.closed
os.chdir(wdPath)


# import local functions
from file_helpers import write_to_disk
from file_helpers import open_from_disk
from file_helpers import write_to_csv

from python_helpers import sync_lists
from python_helpers import split_list

from scraper_helpers import get_match_ids

from scrapers import scrape_matchday
#----------------------------------------------------------------------

# Main

# Budesliga seasons 2009/2010 to 2014/2015
#seed_urls = ['https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/4336',
#            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/3863',
#            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/3424',
#            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/2949',
#            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/2520',
#            'https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/1903']
# Bundesliga season 2015/2016
seed_urls = ['https://www.whoscored.com/Regions/81/Tournaments/3/Seasons/5870']

# schedule interval in minutes, if greater than 0 the scrapers will automatically
# restart after the time interval to prevent that they get stuck
# does not work yet
scheduleInterval = 0
path = 'player_stats_15_16.csv'
scrapedDatesPath = 'scrapedDates_15_16'
matchIdsSavedPath = 'matchIdsSaved_15_16'
phantomscrape = True
phantomscrapeTables = True
allMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                 
def main():
    sync_lists(scrapedDatesPath, matchIdsSavedPath)
    
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
        if os.path.isfile(scrapedDatesPath + '.txt'):
            scrapedDays = open_from_disk(scrapedDatesPath)
        else:
            scrapedDays = []
        if len(scrapedDays) > 0:
            matchdayNr = len(scrapedDays) / 9.0
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
                    scrapedDays = open_from_disk(scrapedDatesPath)
                    if month + ' ' + day.text + ' ' + year in scrapedDays:
                        continue
                    write_to_disk(scrapedDays, scrapedDatesPath)
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
                            scrapedDays = open_from_disk(scrapedDatesPath)
                            if entry.text.split(', ')[1] not in scrapedDays:
                                currentDate = entry.text.split(', ')[1]
                                scrapedDays.append(currentDate)
                                print 'Day ' + entry.text + ' has been scraped.'
                                scraper = True
                                write_to_disk(scrapedDays, scrapedDatesPath)
                            else:
                                scraper = False
                        else:
                            if scraper:
                                matchIdDate = [get_match_ids(entry)[0] + '-' + currentDate]
                                #print '\nCurrent matchIdDate:'
                                #print matchIdDate
                                #print '\n\n'
                                #time.sleep(1)
                                matchdayIds.extend(matchIdDate)
                        #matchIds.extend(get_match_ids(entry))
    
                    mDays = split_list(matchdayIds, 9)
                    matchdayIds = []
                    for mDay in mDays:
                        matchdays = []
                        matchdayData = scrape_matchday(mDay, 
                                                       matchdayNr, 
                                                       str(years[0]) + '-' + str(years[1]),
                                                       phantomscrapeTables)
                        data = matchdayData[0]
                        matchdays.append(matchdayData[1])
    
                        print 'Matchday ' + str(matchdayNr) + ' of 34 has been scraped and saved.'
                        print "############################################\n\n"
    
                        if os.path.isfile(path):
                            # open check match ids file
                            savedMatchday = open_from_disk(matchIdsSavedPath)
                            # if match ids have not been saved before, save them
                            totalIds = len(matchdays) + len(savedMatchday)
                            joined = matchdays
                            joined.extend(savedMatchday)
                            if totalIds == len(set(joined)):
                                for j in range(len(data)):
                                    write_to_csv(path, data[j], append = True)
                                savedMatchday.extend(mDay)
                                write_to_disk(savedMatchday, matchIdsSavedPath)
                            else:
                                print 'There were doubles in match ids list.'
                        else:
                            write_to_disk(mDay, matchIdsSavedPath)
                            write_to_csv(path, data, append = False)
                            savedMatchday = open_from_disk(matchIdsSavedPath)                     
                        
                        matchdayNr = math.floor((len(savedMatchday) * 2 ) / float(17))
                        
                        if matchdayNr > 34:
                            matchdayNr = matchdayNr % 34
    
                            
        endseason = time.time()
        print 'Scraping of season '+ years[0] + '-' + years[1] +' took ' + str(round((endseason - startseason) / 60, 2)) + " minutes."
        browser.quit()
        
if scheduleInterval > 0:
    # does not work yet
    schedule.every(scheduleInterval).minutes.do(main)
    while 1:
        schedule.run_pending()
        time.sleep(1)
else:
    main()
