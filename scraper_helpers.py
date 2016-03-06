# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 10:38:30 2016

@author:  JK
"""
import re
from bs4 import BeautifulSoup
#import urllib2

def get_match_ids(soup):
    matches = soup.findAll("a", {"class": "match-link match-report rc"})
    matchIds = re.findall("Matches/(.*?)/MatchReport", str(matches[0]))
    
    matchIds = []
    for match in matches:
        matchIds.append(re.findall("Matches/(.*?)/MatchReport", str(match))[0])
    return matchIds
        
def extract_value(table, string):
    find = re.findall('"' + string + '">(.*?)<' , str(table))
    return str(find).strip('[]').replace('\\t', '').replace("'", "")

def extract_teams(entry):
    output = []
    allEntries = entry.findAll("a", {"class": "team-link "})
    for teams in allEntries:
        output.append(teams.contents[0])
    return output
    
    
#def get_button_title(soup, side = 'right'):
#    matchButton = soup.findAll("div", {"id": "date-controller"})[0].findAll("a", {"href": "#"})
#    if side == 'right':
#        buttonTitle = re.findall('title="(.*?)">', str(matchButton[2]))[0]
#        return buttonTitle
#    if side == 'left':
#        buttonTitle = re.findall('title="(.*?)">', str(matchButton[0]))[0]
#        return buttonTitle
#    
#def get_content(url):
#    opener = urllib2.build_opener()
#    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
#    resource = opener.open(url)
#    html = resource.read()
#    resource.close() 
#    return html