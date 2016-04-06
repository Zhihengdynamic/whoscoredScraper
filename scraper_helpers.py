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
    teamname = teamname.lower()
    if 'leverkusen' in teamname:
        return 'Leverkusen'
    if 'bayern' in teamname:
        return 'Bayern Munich'
    if 'mainz' in teamname:
        return 'Mainz'
    if 'hamburg' in teamname:
        return 'Hamburg'
    if 'stuttgart' in teamname:
        return 'Stuttgart'
    if 'hannover' in teamname:
        return 'Hannover'
    if 'schalke' in teamname:
        return 'Schalke'
    if 'wolfsburg' in teamname:
        return 'Wolfsburg'
    if 'dortmund' in teamname:
        return 'Dortmund'
    if u'kln' in teamname:
        return 'Cologne'
    if u'k?ln' in teamname:
        return 'Cologne'
    if 'cologne' in teamname:
        return 'Cologne'
    if 'bremen' in teamname:
        return 'Bremen'
    if 'frankfurt' in teamname:
        return 'Frankfurt'
    if 'berlin' in teamname:
        return 'Berlin'
    if u'n?rnberg' in teamname:
        return 'Nuernberg'
    if 'nuernberg' in teamname:
        return 'Nuernberg'
    if 'hoffenheim' in teamname:
        return 'Hoffenheim'
    if 'bochum' in teamname:
        return 'Bochum'
    if 'gladbach' in teamname:
        return 'Gladbach'
    if 'freiburg' in teamname:
        return 'Freiburg'
    if 'kaiserslatuern' in teamname:
        return 'Kaiserslatuern'
    if 'pauli' in teamname:
        return 'St. Pauli'
    if 'duesseldorf' in teamname:
        return 'Duesseldorf'
    if u'd?sseldorf' in teamname:
        return 'Duesseldorf'
    if u'dsseldorf' in teamname:
        return 'Duesseldorf'
    if 'fuerth' in teamname:
        return 'Fuerth'
    if u'frth' in teamname:
        return 'Fuerth'
    if u'f?rth' in teamname:
        return 'Fuerth'
    if 'brauenschweig' in teamname:
        return 'Brauenschweig'
    if 'paderborn' in teamname:
        return 'Paderborn'
    if 'ingolstadt' in teamname:
        return 'Ingolstadt'
    if 'darmstadt' in teamname:
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