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
    
def correct_teamname(teamname):
    teamname = teamname.encode('ascii', 'ignore')
    if 'Leverkusen' in teamname:
        return 'Leverkusen'
    if 'Bayern' in teamname:
        return 'Bayern Munich'
    if 'Mainz' in teamname:
        return 'Mainz'
    if 'Hamburg' in teamname:
        return 'Hamburg'
    if 'Stuttgart' in teamname:
        return 'Stuttgart'
    if 'Hannover' in teamname:
        return 'Hannover'
    if 'Schalke' in teamname:
        return 'Schalke'
    if 'Wolfsburg' in teamname:
        return 'Wolfsburg'
    if 'Dortmund' in teamname:
        return 'Dortmund'
    if u'Kln' in teamname:
        return 'Cologne'
    if 'Cologne' in teamname:
        return 'Cologne'
    if 'Bremen' in teamname:
        return 'Bremen'
    if 'Frankfurt' in teamname:
        return 'Frankfurt'
    if 'Berlin' in teamname:
        return 'Berlin'
    if u'Nrnberg' in teamname:
        return 'Nuernberg'
    if 'Nuernberg' in teamname:
        return 'Nuernberg'
    if 'Hoffenheim' in teamname:
        return 'Hoffenheim'
    if 'Bochum' in teamname:
        return 'Bochum'
    if 'Gladbach' in teamname:
        return 'Gladbach'
    if 'Freiburg' in teamname:
        return 'Freiburg'
    if 'Kaiserslatuern' in teamname:
        return 'Kaiserslatuern'
    if 'Pauli' in teamname:
        return 'St. Pauli'
    if 'Duesseldorf' in teamname:
        return 'Duesseldorf'
    if u'Dsseldorf' in teamname:
        return 'Duesseldorf'
    if 'Fuerth' in teamname:
        return 'Fuerth'
    if u'Frth' in teamname:
        return 'Fuerth'
    if 'Brauenschweig' in teamname:
        return 'Brauenschweig'
    if 'Paderborn' in teamname:
        return 'Paderborn'
    if 'Ingolstadt' in teamname:
        return 'Ingolstadt'
    if 'Darmstadt' in teamname:
        return 'Darmstadt'
    return teamname
        
    
    
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