import re
import os
import urllib2
from bs4 import BeautifulSoup
import time
from random import randint
import csv
from selenium import webdriver
import math

#os.chdir(path to working directory) 
                
def get_content(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    resource = opener.open(url)
    html = resource.read()
    resource.close() 
    return html
    
def write_to_disk(data, name, rowwise = False):
    filename = name + ".txt"
    text_file = open(filename, "wb")
    for row in data:
        text_file.write("%s\r\n" % row)

    text_file.close()

def open_from_disk(name):
    filename = name + ".txt"
    output = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as openfile:
            reader = csv.reader(openfile, delimiter='\n')
            for row in reader:
                output.append(row[0])
        return output
    else:
        print 'File ' + filename + ' does not exist!'
        return []

    
def extract_value(table, string):
    find = re.findall('"' + string + '">(.*?)<' , str(table))
    return str(find).strip('[]').replace('\\t', '').replace("'", "")
    

def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

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
        browser = webdriver.PhantomJS(phantomjs_path)
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
 

def get_match_ids(soup):
    matches = soup.findAll("a", {"class": "match-link match-report rc"})
    matchIds = re.findall("Matches/(.*?)/MatchReport", str(matches[0]))
    
    matchIds = []
    for match in matches:
        matchIds.append(re.findall("Matches/(.*?)/MatchReport", str(match))[0])
    return matchIds

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


def get_button_title(soup, side = 'right'):
    matchButton = soup.findAll("div", {"id": "date-controller"})[0].findAll("a", {"href": "#"})
    if side == 'right':
        buttonTitle = re.findall('title="(.*?)">', str(matchButton[2]))[0]
        return buttonTitle
    if side == 'left':
        buttonTitle = re.findall('title="(.*?)">', str(matchButton[0]))[0]
        return buttonTitle
        
#----------------------------------------------------------------------
def write_to_csv(path, data, append = False):
    # preparing data
    outputDic = []
    if type(data[0]) is dict:
        fieldnames = data[0].keys()
        outputDic = data
    else:
        fieldnames = data[0][0].keys()
        for day in data:
            for player in day:
                outputDic.append(player)
    # appending data to existing csv file
    if append:
        with open(path, "ab") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', 
                                    fieldnames=fieldnames, lineterminator='\n')
            for row in outputDic:
                writer.writerow(row)
    # make new csv file
    else:
        with open(path, "wb") as out_file:
            writer = csv.DictWriter(out_file, 
                                    delimiter=',', fieldnames=fieldnames)
            writer.writeheader()
            for row in outputDic:
                writer.writerow(row)
    out_file.close()

def sync_lists(listname1, listname2):          
    syncDays = open_from_disk(listname1)
    syncMatchday = open_from_disk(listname2)
    
    comparison = []
    for syncentry in syncMatchday:
        comparison.append(syncentry.split('-')[1])
    mismatch = [x for x in syncDays if x not in list(comparison)]
    
    print '\n' + str(len(mismatch)) + ' values will be removed from '+ listname1 + '.\n'
    print 'Sync completed.\n'
    for val in mismatch:
        syncDays.remove(val)
    write_to_disk(syncDays, listname1)

def split_list(splitlist, nparts):
    returnList = []
    for i in xrange(0, len(splitlist), nparts):
        returnList.append(splitlist[i:i + nparts])
    return returnList

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
phantomjs_path = r'location of phantom.exe'
allMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']



sync_lists('scrapedDates', 'matchIdsSaved')

for seed_url in seed_urls:
    startseason = time.time()
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.http.max-connections', 5000)
    profile.update_preferences()

    # use phantom?
    if phantomscrape:
        browser = webdriver.PhantomJS(phantomjs_path)
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
                    matchdayData = scrape_matchday(mDay, matchdayNr, str(years[0]) + '-' + str(years[1]))
                    data = matchdayData[0]
                    matchdays.append(matchdayData[1])

                    print 'Matchday ' + str(matchdayNr) + ' of 34 has been scraped and saved.'
                    print "############################################\n\n"

                    if os.path.isfile(path):
                        # open check match ids file
                        savedMatchday = open_from_disk("matchIdsSaved")
                        # if match ids have not been saved before, save them
                        totalIds = len(matchdays) + len(savedMatchday)
                        joined = matchdays
                        joined.extend(savedMatchday)
                        if totalIds == len(set(joined)):
                            for j in range(len(data)):
                                write_to_csv(path, data[j], append = True)
                            savedMatchday.extend(mDay)
                            write_to_disk(savedMatchday, "matchIdsSaved")
                        else:
                            print 'There were doubles in match ids list.'
                    else:
                        write_to_disk(mDay, "matchIdsSaved")
                        write_to_csv(path, data, append = False)                                
                    
                    matchdayNr = math.floor((len(savedMatchday) * 2 ) / float(17))
                    
                    if matchdayNr > 34:
                        matchdayNr = matchdayNr % 34

                        
    endseason = time.time()
    print 'Scraping of season '+ years[0] + '-' + years[1] +' took ' + str(round((endseason - startseason) / 60, 2)) + " minutes."
    browser.quit()

