#!/usr/bin/python
import sqlite3, urllib.request, json, re, datetime
from socket import timeout
from style import *
from useragents import *
  
con = sqlite3.connect('hackable.db')

def isScanned(url):
  cursorObj = con.cursor()
  cursorObj.execute("SELECT * FROM scanned WHERE url = '" + url + "'")
  if(len(cursorObj.fetchall()) == 0):
    return False
  else:
    return True

def insertScanned(url):
  cursorObj = con.cursor()
  if(not isScanned(url)):
    cursorObj.execute("INSERT INTO scanned (url) VALUES('" + url + "')")
  con.commit()
	
def insertWebsite(url,cms="NULL",version="NULL"):
  cursorObj = con.cursor()
  if(isScanned(url)):
    cursorObj.execute("INSERT INTO websites (url, cms, version) VALUES('" + url + "', '" + cms + "', '" + version + "')")
  else:
    cursorObj.execute("UPDATE websites SET cms = '" + cms + "', version = '" + version + "' WHERE url = '" + url + "'")
  con.commit()

def is200(url):
  try:
    req = urllib.request.Request(url, headers = randomUserAgent())
    res = urllib.request.urlopen(req, timeout=10)
    if(res.getcode() == 200):
      return True
  except urllib.error.HTTPError as msg:
    error(msg)
    return False
  except urllib.error.URLError as msg:
    error(msg)
    return False
  except Exception as e:
    with open('error.log', 'a') as error_log:
      error_log.write(str(datetime.datetime.now()) + " :\n" + "function : is200" + "\nurl : " + url + "\nerror : " + str(e) + "\n" + "=" * 50 + "\n")
  except timeout:
    error("urllib urlopen timeout")
    return False
	
def getGroupNames(regex):
  Regex4GroupNames = r"\(\?P<([a-zA-Z]+)>"
  groupNames = re.findall(Regex4GroupNames, regex)
  return groupNames

def getCharSet(res, html):
  if(res.getheader('Content-Type').find('charset=') != -1):
    return res.getheader('Content-Type')[res.getheader('Content-Type').find('charset=')+8:]
  else:
    html = str(html)
    html = html[html.find('charset'):]
    return html[html.find('charset')+8:html.find('"')]
  
def RegexMatch(url, regex):
  try:
    req = urllib.request.Request(url, headers = randomUserAgent())
    res = urllib.request.urlopen(req, timeout=10)
    html = res.read()
    html = html.decode(getCharSet(res, html))
    matches = re.finditer(regex, html, re.MULTILINE)
    groupNames = getGroupNames(regex)
    AllMatchs = []
    for matchNum, match in enumerate(matches, start=1):
      AllMatchs.append(match.groups())
    if(len(AllMatchs) > 0):
      return dict(zip(groupNames, AllMatchs[0]))
    else:
      error("Regex Notting Match")
      return False
  except urllib.error.HTTPError as msg:
    error(msg)
    return False
  except urllib.error.URLError as msg:
    error(msg)
    return False
  except Exception as e:
    with open('error.log', 'a') as error_log:
      error_log.write(str(datetime.datetime.now()) + " :\n" + "function : RegexMatch" + "\nurl : " + url + "\nregex :" + regex + "\nerror : " + str(e) + "\n" + "=" * 50 + "\n")
  except timeout:
    error("urllib urlopen timeout")
    return False

def getVersion(url,vendor):
  logo()
  print(url)
  with open('cms.json', 'r') as cms_conf:
    cms_conf_dict = json.load(cms_conf)
    print("=" * 65)
    print(vendor + " version Scanning")
    print("=" * 65)
    for version_method_num, version_method in enumerate(cms_conf_dict['vendors'][vendor]['version']):
      if(version_method['type'] == 'is200'):
        if(is200(url + version_method['path'])):
          success(vendor + " Detected ")
          insertWebsite(url=url, cms=vendor)
          getVersion(url)
          return
      elif(version_method['type'] == 'RegexMatch'):
        match = RegexMatch(url + version_method['path'], version_method['regex'])
        if(match):
          for groupName in match.keys():
            exec("global " + groupName + "\n" + groupName + " = \"" + match[groupName] + "\"")
          success(vendor + " Detected")
          success(version + " version Detected")
          insertWebsite(url=url, cms=vendor, version=version)
          for groupName in match.keys():
            exec("global " + groupName + "\ndel " + groupName)
          return
			
def getCMS(url):
  insertScanned(url)
  with open('cms.json', 'r') as cms_conf:
    cms_conf_dict = json.load(cms_conf)
    for vendor in cms_conf_dict['vendors'].keys():
      print("=" * 65)
      print(vendor + " Scanning")
      print("=" * 65)
      for validation_num, valitation_methods in enumerate(cms_conf_dict['vendors'][vendor]['validation']):
        if(valitation_methods['type'] == 'is200'):
          if(is200(url + valitation_methods['path'])):
            success(vendor + " Detected ")
            insertWebsite(url=url, cms=vendor)
            getVersion(url,vendor)
            return
        elif(valitation_methods['type'] == 'RegexMatch'):
          match = RegexMatch(url + valitation_methods['path'], valitation_methods['regex'])
          if(match):
            for groupName in match.keys():
              exec("global " + groupName + "\n" + groupName + " = \"" + match[groupName] + "\"")
            if(vendor.lower() == cms.lower()):
              success(vendor + " Detected")
              success(version + " version Detected")
              insertWebsite(url=url, cms=vendor, version=version)
              for groupName in match.keys():
                exec("global " + groupName + "\ndel " + groupName)
              return

def parseURL(url):
  parsedURL = {}
  if(url.find('://') == -1):
    parsedURL['protocol'] = 'http'
    if(url.find('/') == -1):
      parsedURL['domain'] = url
    else:
      parsedURL['domain'] = url[:url.find('/')]
  else:
    parsedURL['protocol'] = url[:url.find('://')]
    if(url.find('/',url.find('://')+3) != -1):
      parsedURL['domain'] = url[url.find('://')+3:url.find('/',url.find('://')+3)]
    else:
      parsedURL['domain'] = url[url.find('://')+3:]
  return (parsedURL['protocol'] + '://' + parsedURL['domain'] + '/')
  
def googleSearch():
  dork = input('Google Search : ')
  regex = '<cite[\ ]+class="[A-Za-z0-9\ \-]+">(?P<cite>[A-Za-z0-9:.\/]+)'
  try:
    start = 0
    while True:
      print("http://www.search-results.com/web?q=" + urllib.parse.quote(dork) + "&hl=en&page=" + str(start) + "&src=hmp")
      req = urllib.request.Request("https://www.google.com.tr/search?q=" + urllib.parse.quote(dork) + "&start=" + str(start), headers = randomUserAgent())
      start += 10
      #req = urllib.request.Request("http://www.search-results.com/web?q=" + urllib.parse.quote(dork) + "&hl=en&page=" + str(start) + "&src=hmp", headers = randomUserAgent())
      #start += 1
      #req.set_proxy('156.54.63.245:8080', 'http')
      res = urllib.request.urlopen(req, timeout=10)
      html = res.read()
      print(html)
      html = html.decode(getCharSet(res, html))
      matches = re.finditer(regex, html, re.MULTILINE)
      groupNames = getGroupNames(regex)
      AllMatchs = []
      for matchNum, match in enumerate(matches, start=1):
        AllMatchs.append(match.groups()[0])
      for num , Match in enumerate(AllMatchs):
        if(num % 2 == 0):
          print(parseURL(Match))
          logo()
          print(parseURL(Match))
          if(not isScanned(parseURL(Match))):
            getCMS(parseURL(Match))
  except urllib.error.HTTPError as msg:
    error(msg)
    return False
  except urllib.error.URLError as msg:
    error(msg)
    return False
  except timeout:
    error("urllib urlopen timeout")
    return False

			  
def main():
  logo()
  with open("targets.txt", 'r') as targets:
    for target in targets.readlines():
      target = target.replace("\n","")
      logo()
      print(target)
      getCMS(target)
	  
if __name__=="__main__":
  logo()
  googleSearch()
  #main()