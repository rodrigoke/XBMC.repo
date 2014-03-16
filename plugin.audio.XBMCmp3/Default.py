#    Copyright (C) 2013 Rodrigo
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see [http://www.gnu.org/licenses/].



#### Imports
import os, re, urllib, urllib2                                                  # Import python function
import xbmc, xbmcaddon, xbmcgui, xbmcplugin                                     # Import XBMC plugins
import buggalo                                                                  # Import 3rd party addons
try:
        from addon.common.addon import Addon

except:
        from t0mm0.common.addon import Addon


#### Constants & initialization
buggalo.SUBMIT_URL = 'http://buggalo.xbmchub.com/submit.php'                    # Official XBMC error report generator
ADDON_NAME = 'plugin.audio.XBMCmp3'                                             # Addon namespace
__addon__ = xbmcaddon.Addon(ADDON_NAME)                                         # Initializing addon properties
__t0mm0addon__ = Addon(ADDON_NAME, sys.argv)                                    # Initializing addon properties
__language__ = __addon__.getLocalizedString

__addonname__   = __addon__.getAddonInfo('name')                                # Humanly readable addon name
PATH = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')       # Path where the addon resides (needs absolute paths)

THEME = __t0mm0addon__.get_setting('theme')                                     # Theme settings
THEME_PATH = os.path.join(PATH, 'art', 'themes', THEME)                         # Theme dir

playlist = xbmc.PlayList( xbmc.PLAYLIST_MUSIC )  

class switch(object):

    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False
            
def art(name):
    if '#' in name: name=name.replace('#','0');
    art_img = os.path.join(THEME_PATH, name + ".jpg")
    return art_img

def HOME():
    addDir(__language__(70000), 'search.php', 'searchMP3',  art('searchMP3'), '',1)
    #addDir(__language__(70001), 'search.php', 'help',       art('help'), '',1)
    
def GetPage(url):
    # Grabbing the URL
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (iPad; U; CPU OS OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B367 Safari/531.21.10')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        return link
    except:
        return ""

def getLinksFromGoogle(url):

    linksarray = {}
    link = GetPage(url);
    
    """
    fullpath = os.path.join(PATH,"Output.htm")
    print fullpath
    with open(fullpath, "w") as text_file:
        #text_file.write("Purchase Amount: {0}".format(TotalAmount))
        text_file.write(GetPage(url))
    """
    alllinks = re.compile('<a href="\/url\?q=(.+?)\&amp\;sa=.+?">').findall(link)
    
    for i in range(len(alllinks)):
        if checkIfNotInForbidden(alllinks[i]) == 1:
            googleURL = urllib.unquote(alllinks[i]).decode('utf8') 
            #print "Grabbing: " + googleURL
            linksarray[i] = googleURL
            #linksarray[i] = getMp3FromUrl(googleURL, querystring)
    return linksarray

def checkIfNotInForbidden(url):
    if "webcache.googleusercontent.com" in url:
        return 0
    if "www.mp3toss.com" in url:
        return 0
    if "mp3brainz.com" in url:
        return 0
    if "www.index-of-mp3s.com" in url:
        return 0
    if "www.mp3s.pl" in url:
        return 0

    return 1
    
def getMp3sFromUrl(url):
    filearray = list()
    
    sourceURL = GetPage(url)
    #regexfiles = re.compile('<IMG .+?>.+?<A.+?HREF="(.+?).mp3">(.+?)<\/A>.+?', re.IGNORECASE)
    #regexfiles = re.compile('.+?<A.+?HREF="(.+?).mp3">(.+?)<\/A>.+?', re.IGNORECASE)
    regexfiles = re.compile("href=\"(.+?)\.mp3\">", re.IGNORECASE)
    allfiles = regexfiles.findall(sourceURL)
    if len(allfiles):
        for i in range(len(allfiles)):
            linearray = {}
            linearray[0] = url + str(allfiles[i]) + ".mp3"
            linearray[1] = urllib.unquote_plus(allfiles[i])
            filearray.insert(i, linearray)
    return filearray
    

    
def SEARCH(url, searchq = ""):

    url = "https://www.google.com/search?q=intitle:index.of+mp3+-html+-htm+-php+-asp+-txt+-pls+"
    if searchq == None:
        keyboard = xbmc.Keyboard('', __language__(70002))
        keyboard.doModal()
        if keyboard.isConfirmed():
            searchq = keyboard.getText().replace(' ','+')            
            if searchq == None:
                return False
    
    url = url + searchq.lower() + "+"
   
    allLinks =  getLinksFromGoogle(url)
    counter = 1
    print allLinks
    if len(allLinks):
        for i in range(len(allLinks)):
            
            try:
                #print str(allLinks[i])
                addDir(__language__(70003) + " " + str(counter), str(allLinks[i]), "getMP3sPerLink", "", searchq)
                counter = counter + 1;
            except:
                pass
    
def PLAYMP3(name,url):
    
    listitem = xbmcgui.ListItem(name)
    listitem.setInfo('audio', {'Title': name})
    if xbmc.Player().isPlayingAudio() == False:
        playlist.clear()
        playlist.add(url, listitem)
        xbmc.Player().play(playlist)
    else:
        playlist.add(url, listitem)

def LISTFILES(url):

    allLinks = getMp3sFromUrl(url)
    print allLinks
    if len(allLinks):
        for i in range(len(allLinks)):
            addDir(allLinks[i][1], allLinks[i][0], "playMP3", "", "", 0)
            
def get_params():
        param=[]
        try:
                paramstring=sys.argv[2]
                if len(paramstring)>=2:
                        params=sys.argv[2]
                        cleanedparams=params.replace('?','')
                        if (params[len(params)-1]=='/'):
                                params=params[0:len(params)-2]
                        pairsofparams=cleanedparams.split('&')
                        param={}
                        for i in range(len(pairsofparams)):
                                splitparams={}
                                splitparams=pairsofparams[i].split('=')
                                if (len(splitparams))==2:
                                        param[splitparams[0]]=splitparams[1]
        except:
                pass
#        print param
        return param

def addDir(name,url,mode,iconimage,query,isfolder=True):

        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+"&name="+urllib.quote_plus(name)+"&query="+str(query)
        
        ok=True
        name = name.replace("\\", "")
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="music", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image', art('fanart'))
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isfolder)
        return ok


def MODESWITCHER():

    params =    get_params()
    url =       None
    name =      None
    mode =      None
    query =     None

    # Populate url, name & mode vars, if not, take default "None"
    try:
            url=urllib.unquote_plus(params["url"])
    except:
            pass
    try:
            name=urllib.unquote_plus(params["name"])
    except:
            pass
    try:
            mode=urllib.unquote_plus(params["mode"])
    except:
            pass
    try:
            query=urllib.unquote_plus(params["query"])
    except:
            pass

    print "Mode: "  +str(mode)
    print "URL: "   +str(url)
    print "Name: "  +str(name)
    print "Query: " +str(query)


    for case in switch(mode):
        if case(None):
            buggalo.trackUserFlow('None mode selected')
            HOME()
            break
        if case('searchMP3'):
            buggalo.trackUserFlow('Search: ' + str(mode))
            SEARCH(url, query)
            break
        if case('getMP3sPerLink'):
            buggalo.trackUserFlow(str(url))
            LISTFILES(url)
            break
        if case('playMP3'):
            buggalo.trackUserFlow(str(name) + " - " + str(url))
            PLAYMP3(name,url)
            break
        if case():
            buggalo.trackUserFlow('Default mode')
            HOME()
            break

MODESWITCHER()


xbmcplugin.endOfDirectory(int(sys.argv[1]))