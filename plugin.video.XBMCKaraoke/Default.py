#    Copyright (C) 2016 Rodrigo
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


#    xbmc.Player(xbmc.PLAYER_CORE_PAPLAYER).play(ContentPath)

#### Imports
import os, re, shutil, urllib, urllib2, pickle, time, glob                      # Import python function
import xbmc, xbmcaddon, xbmcgui, xbmcplugin                                     # Import XBMC plugins
import buggalo, urlresolver                                                     # Import 3rd party addons
try:
        from addon.common.addon import Addon
except:
        from t0mm0.common.addon import Addon

#http://t0mm0.github.io/xbmc-urlresolver/modules/t0mm0.common/addon.html
#from common import functions

## XBMC workaround
import _json
if not 'load' in dir(_json):
    import simplejson as _json
    
    
from library import utils


#### Constants & initialization
buggalo.SUBMIT_URL = 'http://buggalo.tvaddons.ag/submit.php'                    # Official XBMC error report generator
ADDON_NAME = 'plugin.video.XBMCKaraoke'                                         # Addon namespace
__addon__ = xbmcaddon.Addon(ADDON_NAME)                                         # Initializing addon properties
__t0mm0addon__ = Addon(ADDON_NAME, sys.argv)                                    # Initializing addon properties
__language__ = __addon__.getLocalizedString


__addonname__   = __addon__.getAddonInfo('name')                                # Humanly readable addon name
PATH = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')       # Path where the addon resides (needs absolute paths)
TEMP_DL_DIR =  'tempdl'                                                         # Temp download directory. No write permissions in special://temp so using folder inside the addon
jsonurl = 'http://api.xbmckaraoke.com/'                                         # PHP JSON website (database)
url = None                                                                      # Standard value
donotloaddir = 0                                                                # Standard value

THEME = __t0mm0addon__.get_setting('theme')                                     # Theme settings
THEME_PATH = os.path.join(PATH, 'art', 'themes', THEME)                         # Theme dir





def getConfigInfo():
    try:
        _json = utils.loadJsonFromUrl(jsonurl + "config.php?version=" + __addon__.getAddonInfo('version'))
        if _json == None:
            xbmcgui.Dialog().ok(__addonname__, ' ', __language__(70111))
            return
        filename = _json[0]['full_file_name']
        urlname = _json[0]['url_name']
        
        print filename
        print urlname
        
        if filename == None and urlname == None:
            xbmcgui.Dialog().ok(__addonname__, ' ', __language__(70117))
            donotloaddir = 1
            return

        line1 = "This is a simple example of OK dialog"
        line2 = "Showing this message using"
        line3 = "XBMC python modules"

        xbmcgui.Dialog().ok(__addonname__, line1, line2, line3)

    except Exception as e:
        buggalo.onExceptionRaised()
        print (e)

def getStartupDialog():
	print "blaat"

def art(name):
    if '#' in name: name=name.replace('#','0');
    art_img = os.path.join(THEME_PATH, name + ".jpg")
    return art_img
    
def _pbhook(numblocks, blocksize, filesize, dlg, start_time):
    try:
        percent = min(numblocks * blocksize * 100 / filesize, 100)
        currently_downloaded = float(numblocks) * blocksize / (1024 * 1024)
        kbps_speed = numblocks * blocksize / (time.time() - start_time)
        if kbps_speed > 0:
            eta = (filesize - numblocks * blocksize) / kbps_speed
        else:
            eta = 0
        kbps_speed /= 1024
        total = float(filesize) / (1024 * 1024)
        #mbs = '%.02f MB ' + __language__(70133) + ' %.02f MB' % (currently_downloaded, total)
        mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
        est = __language__(70131) + ': %.02f Kb/s ' % kbps_speed
        est += __language__(70132) + ': %02d:%02d' % divmod(eta, 60)
        dlg.update(percent, mbs, est)

    except:
        percent = 100
        dlg.update(percent)
    if dlg.iscanceled():
        dlg.close()
        raise utils.StopDownloading('Stopped Downloading')

def download_karaoke_file(url, dest, displayname=False):
    print 'Downloading karaoke file'
    print 'URL: %s' % url
    print 'Destination: %s' % dest
    if not displayname:
        displayname = url
    dlg = xbmcgui.DialogProgress()
    dlg.create(__addonname__,__language__(70130), displayname)
    start_time = time.time()
    if os.path.isfile(dest):
        print 'File to be downloaded already esists'
        return True
    try:
        urllib.urlretrieve(url, dest, lambda nb, bs, fs: _pbhook(nb, bs, fs, dlg, start_time))
    except:
        #only handle StopDownloading (from cancel),
        #ContentTooShort (from urlretrieve), and OS (from the race condition);
        #let other exceptions bubble 
        if sys.exc_info()[0] in (urllib.ContentTooShortError, utils.StopDownloading, OSError):
            return False
        else:
            buggalo.onExceptionRaised()
            #buggalo.onExceptionRaised(url + " - " + dest)
    return True

def getUnzipped(theurl, thedir, thename, generalid):
    """Args:
    * theurl: The URL where the zip can be downloaded
    * thedir: The directory where the zipfile should be saved into
    * thename: The complete filename of the zipfile
    
    Function:
        Retrieves the zipfile from the URL location given, using urlresolver.
        The function then unzips the file.

    WORKAROUND INCLUDED:
        xbmc.extract can't handle a comma in the filename ( up to v12: Frodo)
        The script will remove any comma's in the name of the filename
    """
    theoldname = thename
    name = os.path.join(thedir, thename)
    try:
        if not os.path.exists(thedir):
            os.makedirs(thedir)
    except Exception:
        buggalo.onExceptionRaised()
        #buggalo.onExceptionRaised(thedir)
        print 'can\'t create directory (' + thedir + ')'
        return
    #try:
    print theurl[0:25]
    if urlresolver.HostedMediaFile(theurl).valid_url() or theurl[0:25] == "http://www.mediafire.com/":
    
        try:
            if theurl[0:25] == "http://www.mediafire.com/":
                url = theurl
            else:
                url = urlresolver.resolve(theurl)
            print 'translated link: ' + url
            if download_karaoke_file(url, name, name):
                # Code to circumvent a bug in URIUtils::HasExtension
                thenewname = theoldname.replace(",", "")
                if thenewname != theoldname:
                    newname = os.path.join(thedir, thenewname)
                    os.rename(name, newname)
                    name = newname

                # Python unzip is rubbish!!! gave me corrupted unzips every time
                xbmc.executebuiltin('xbmc.extract(' + name + ')', True)

                # Remove the zip file
                os.unlink(name)
                return 1
            else:
                reportFile('brokenlink', generalid, thename, theurl);
                xbmcgui.Dialog().ok(__addonname__, __language__(70120), __language__(70121), '')
                return 0
        except:
            xbmcgui.Dialog().ok(__addonname__, __language__(70126), __language__(70127), __language__(70121))
            return 0
    else:
        reportFile('brokenlink', generalid, thename, theurl);
        xbmcgui.Dialog().ok(__addonname__, __language__(70122), __language__(70121), '')
        return 0
    return 0

def checkKaraokeSetting():
    """Verifies if the Karaoke setting is enabled in XBMC
    If not, an OK dialog is shown and the script is terminated"""
    if xbmc.getCondVisibility('system.getbool(karaoke.enabled)') != 1:

        xbmcgui.Dialog().ok(__addonname__, __language__(70114), ' ', __language__(70115))
        raise SystemExit
    
def deleteDir(dirname):
    """Deletes the directory (dirname) and everything in it"""
    try:
        dirname2 = os.path.dirname(dirname)
        for file in os.listdir(dirname2):
            print file
            if file.startswith(TEMP_DL_DIR):
                dirname3 = os.path.join(dirname2, file)
                print dirname3
                shutil.rmtree(dirname3)
    except:
        #buggalo.onExceptionRaised(dirname)
        print "can't delete directory (" + dirname3 + ")"
  


def reportFile(reporttype, generalid, filename, urlname):
    url = 'report.php?type=' + reporttype
    url = url + '&id=' + generalid
    url = url + '&filename=' + urllib.quote_plus(filename)
    url = url + '&url=' + urllib.quote_plus(urlname)
    
    print jsonurl + url
    
    req = urllib2.Request(jsonurl + url)
    req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    req.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) XBMCKARAOKEADDON/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
    u = urllib2.urlopen(req)
    #u.read()
    u.close()
    
def getJSONData(serviceUrl, data):
    for attempt in range(0, 3):
        try:
            json = simplejson.dumps(data)
            req = urllib2.Request(serviceUrl, json)
            req.add_header('Content-Type', 'text/json')
            u = urllib2.urlopen(req)
            u.read()
            u.close()
            break  # success; no further attempts
        except Exception:
            pass # probably timeout; retry
    
def TEST(url, mode):
    window = QRWindow()
    window.doModal() 
    
def KARAOKELINKS(url, id, tempkey):

    if tempkey == 'session':
        url = url + '?generalid='+ __addon__.getSetting('session_key')
    else:
        url = url + '?generalid='+ str(id)
    url = url + '&tempkey='+ str(tempkey)
    print jsonurl + url

    try:
    
        _json = utils.loadJsonFromUrl(jsonurl + url)

        filename = _json[0]['full_file_name']
        urlname = _json[0]['url_name']
        
        print filename
        print urlname
        
        if filename == None and urlname == None:
            xbmcgui.Dialog().ok(__addonname__, ' ', __language__(70117))
            donotloaddir = 1
            return
        
        timestr = time.strftime("%Y%m%d%H%M%S")
        fullDir = os.path.join(PATH, TEMP_DL_DIR + timestr)
        
        #delete directory
        deleteDir(fullDir)
        
        print 'Directory'
        print fullDir
     
        #download new file
        

        #fullFilePath = os.path.splitext(os.path.join(fullDir, filename))[0]
        #fullFilePath = fullFilePath + '.mp3'

        if getUnzipped(urlname, fullDir, filename, id) == 1:
            os.chdir(fullDir)
            i = 1
            for files in glob.glob("*.mp3"):
                if i == 1:
                    i = 2
                    xbmc.Player().play(os.path.join(fullDir, files))

            if len(glob.glob("*.mp3")) < 1:
                reportFile('badzip', id, filename, urlname);
                xbmcgui.Dialog().ok(__addonname__, __language__(70123), __language__(70124),  __language__(70125))
                    
            #xbmcplugin.endOfDirectory(int(sys.argv[1]))
            #while xbmc.Player().isPlaying():
            #    print 'sleeping...'
            #    xbmc.sleep(1000)
            
            
            #def addDir(name,url,mode,iconimage,page, id, param1, param2="", isfolder=True):
            
            liz=xbmcgui.ListItem('', '', iconImage='DefaultAlbumCover.png', thumbnailImage='')
            #liz.setInfo( type='music', infoLabels={ 'Title': name, 'count': id} )
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url='',listitem=liz,isFolder=0)


    except Exception as e:
        buggalo.onExceptionRaised()
        print (e)

def getAllTheLetters(begin='A', end='Z'):
    beginNum = ord(begin)
    endNum = ord(end)
    for number in xrange(beginNum, endNum+1):
        yield chr(number)

def getNextLetter(letter):
    if letter == 'Z':
        return '#'
    letterNum = ord(letter)
    return chr(letterNum+1)
    
def BROWSEARTISTSLISTSUB():
    letter = 'A'
    for count in range(1,28):
        addDir(letter, 'search.php', 'browseArtists',    art('BrowseAllArtists' + letter), '0','0', letter)
        letter = getNextLetter(letter)
    if count % 10 == 0:
        print 'did ten'
        
def BROWSESONGSLISTSUB():
    letter = 'A'
    for count in range(1,28):
        addDir(letter, 'search.php', 'browseSongs',    art('BrowseAllSongs' + letter), '0','0', letter)
        letter = getNextLetter(letter)
    if count % 10 == 0:
        print 'did ten'
    
def SEARCH(url, mode, pageid, searchq = ""):

    if searchq == None:
        if mode == 'searchArtists':
            keyboard = xbmc.Keyboard('', __language__(70000))
        if mode == 'searchSongs':
            keyboard = xbmc.Keyboard('', __language__(70001))
        if mode == 'searchIDs':
            keyboard = xbmc.Keyboard('', __language__(70002))
        keyboard.doModal()
        if keyboard.isConfirmed():
            searchq = keyboard.getText().replace(' ','%20')            
            if searchq == None:
                return False
            if not re.match('[A-Za-z0-9 ]', searchq):     # this part doesn't work for some reason...
                d = xbmcgui.Dialog()
                d.ok(__addonname__, __language__(70104))  
                HOME()
                return False

    url = url + '?type='+mode.lower()
    url = url + '&pageid='+ str(pageid)
    url = url + '&extra='+ str(searchq)
    print jsonurl + url

    if str(searchq) != 'None':
        pageid = int(pageid) + 1
        _json = utils.loadJsonFromUrl(jsonurl + url)
        if (_json):
            count = 0
            if mode == 'searchArtists':
                for items in _json:
                    count = count + 1
                    items["sd_id"] = str(items["sd_id"])
                    addDir(items['artist_name'], 'search.php', 'getSongsByArtist', '', '0',items['artist_id'], items['sd_id'])
                if count == 30:
                    addDir(__language__(70100), 'search.php', 'searchArtists',         '', str(pageid),'', searchq)
            if mode == 'searchSongs':
                for items in _json:
                    count = count + 1
                    addDir(items['song_name'], 'getlink.php', 'getVideo',         '', '1',items['general_id'], items['temp_key'])
                if count == 30:
                    addDir(__language__(70100), 'search.php', 'searchSongs',         '', str(pageid),'', searchq)
            if mode == 'searchIDs':
                for items in _json:
    #                count = count + 1
                    addDir(items['song_name'], 'getlink.php', 'getVideo',         '', '1',items['general_id'], items['temp_key'])
    #            if count == 30:
    #                addDir(__language__(70100), 'search.php', 'searchSongs',         '', str(pageid),'', searchq)
                    
        else:
            xbmcgui.Dialog().ok(__addonname__, __language__(70111), __language__(70112), __language__(70113))
            HOME()
    else:
        HOME()

def GETLUCKY(url, mode):

    url = url + '?type='+mode.lower()
    print jsonurl + url

    _json = utils.loadJsonFromUrl(jsonurl + url)
    if (_json):
        addDir(_json[0]['song_name'], 'getlink.php', 'getVideo', '', '1',_json[0]['general_id'], _json[0]['temp_key'])
    else:
        xbmcgui.Dialog().ok(__addonname__, __language__(70101), __language__(70102), __language__(70103))

def GETPOPULAR(url, mode):

    url = url + '?type='+mode.lower()
    print jsonurl + url

    _json = utils.loadJsonFromUrl(jsonurl + url)
    if (_json):
        count = 0
        for items in _json:
            count = count + 1
            addDir(str(count).zfill(2) + '.' + items['song_name'], 'getlink.php', 'getVideo',         '', '1',items['general_id'], items['temp_key'])
    else:
        xbmcgui.Dialog().ok(__addonname__, __language__(70101), __language__(70102), __language__(70103))
        
def BROWSESONGS(url, mode, pageid, letter):

    url = url + '?type='+mode.lower()
    url = url + '&pageid='+ str(pageid)
    url = url + '&extra='+ str(letter)
    print jsonurl + url

    pageid = int(pageid) + 1
    _json = utils.loadJsonFromUrl(jsonurl + url)
    if (_json):
        count = 0
        for items in _json:
            count = count + 1
            addDir(items['song_name'], 'getlink.php', 'getVideo',         '', '1',items['general_id'], items['temp_key'])
        if count == 30:
            addDir(__language__(70100), 'search.php', 'browseSongs',         '', str(pageid),'', str(letter))
    else:
        xbmcgui.Dialog().ok(__addonname__, __language__(70101), __language__(70102), __language__(70103))

def BROWSESONGSFROMARTIST(url, mode, pageid, id):

    url = url + '?type='+mode.lower()
    url = url + '&pageid='+ str(pageid)
    url = url + '&id='+ str(id)
    print jsonurl + url

    pageid = int(pageid) + 1
    _json = utils.loadJsonFromUrl(jsonurl + url)
    if (_json):
        count = 0
        for items in _json:
            count = count + 1
            addDir(items['song_name'], 'getlink.php', 'getVideo',         '', '1',items['general_id'], items['temp_key'])
        if count == 30:
            addDir(__language__(70100), 'search.php', 'getSongsByArtist',         '', str(pageid),id, '')
    else:
        xbmcgui.Dialog().ok(__addonname__, __language__(70101), __language__(70102), __language__(70103))

def BROWSELATEST(url, mode, pageid):

    url = url + '?type='+mode.lower()
    url = url + '&pageid='+ str(pageid)
    print jsonurl + url

    pageid = int(pageid) + 1
    _json = utils.loadJsonFromUrl(jsonurl + url)
    if (_json):
        count = 0
        for items in _json:
            count = count + 1
            addDir(items['song_name'], 'getlink.php', 'getVideo',         '', '1',items['general_id'], items['temp_key'])
        if count == 30:
            addDir(__language__(70100), 'search.php', 'getLatest',         '', str(pageid),id, '')
    else:
        xbmcgui.Dialog().ok(__addonname__, __language__(70101), __language__(70102), __language__(70103))
        
def BROWSEARTISTS(url, mode, pageid, letter):

    url = url + '?type='+mode.lower()
    url = url + '&pageid='+ str(pageid)
    url = url + '&extra='+ str(letter)
    print jsonurl + url
    pageid = int(pageid) + 1
    _json = utils.loadJsonFromUrl(jsonurl + url)
    if (_json):
        count = 0
        for items in _json:
            count = count + 1
            items["sd_id"] = str(items["sd_id"])
            addDir(items['artist_name'], 'search.php', 'getSongsByArtist', '', '0',items['artist_id'], items['sd_id'])
            #addDir(name,                url,           mode,               iconimage,page, id, param1, param2="", isfolder=True):
            if count == 30:
                addDir(__language__(70100), 'search.php', 'browseArtists',         '', str(pageid),'', str(letter))
    else:
        xbmcgui.Dialog().ok(__addonname__, __language__(70101), __language__(70102), __language__(70103))

def GETQRCODE(url, mode):

    url = url + '?type='+mode.lower()
    print jsonurl + url
    _json = utils.loadJsonFromUrl(jsonurl + url)
    if (_json):
        __addon__.setSetting('session_key', _json[0]['unique_id'])
        # __addon__.setSetting('session_date', time.strftime("%Y%m%d%H%M%S"))
        __addon__.setSetting('session_date', str(time.time()+1800))
        window = utils.QRWindow()
        window.QRlink(_json[0]['QR_link'])
        window.show()
        window.doModal() 
        print 'session key: ' + __addon__.getSetting('session_key')
        print 'session unix timestamp: ' + __addon__.getSetting('session_date')
    else:
        xbmcgui.Dialog().ok(__addonname__, __language__(70101), __language__(70102), __language__(70103))
        
def get_params_v2():

    paramstring = sys.argv[2]
    print paramstring;
    if paramstring != '?content_type=video':
        params = pickle.loads(paramstring);
        param = {'url': params[0], 'mode': params[1], 'page': params[2], 'id': params[3], 'param1': params[4], 'param2': params[5] }
        return param
    
    return []
        
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

def addDir(name,url,mode,iconimage,page, id, param1, param2="", isfolder=True):

        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+"&name="+urllib.quote_plus(name)+"&page="+str(page)+"&id="+str(id)+"&param1="+urllib.quote_plus(param1)+"&param2="+urllib.quote_plus(param2)
        
        ok=True
        name = name.replace("\\", "")
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="music", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image', art('fanart'))
        
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isfolder)
        return ok

def addDir2(name,url,mode,iconimage,page, id, param1, param2=""):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&page="+str(page)+"&id="+urllib.quote_plus(id)+"&param1="+urllib.quote_plus(param1)+"&param2="+urllib.quote_plus(param2)
    ok=True
    name = name.replace("\\", "")
    

    #param = {'url': url, 'mode': mode, 'page': page, 'id': id, 'param1': param1, 'param2': param2 }
    #content = pickle.dumps(param)

    # The next dir is the direct link to the song, so add values
    if mode in ['searchSongs', 'searchIDs', 'browseSongs', 'getPopular', 'getLucky', 'getSongByArtist']:
    
        liz=xbmcgui.ListItem(name, content, iconImage='DefaultAlbumCover.png', thumbnailImage=iconimage)
        liz.setInfo( type='music', infoLabels={ 'Title': name, 'count': id, 'artist': param2} )
    
    elif mode in ['searchArtists', 'browseArtists']:
    
        liz=xbmcgui.ListItem(name, content, iconImage='DefaultAlbumCover.png', thumbnailImage=iconimage)
        liz.setInfo( type='music', infoLabels={ 'Title': name, 'count': id, 'artist': param2} )
    
    else:
    
        liz=xbmcgui.ListItem(name, content, iconImage='DefaultAlbumCover.png', thumbnailImage=iconimage)
        liz.setInfo( type='music', infoLabels={ 'Title': name, 'count': id} )
    
    
    
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=content,listitem=liz,isFolder=True)
    return ok

def HOME():
    currtime = int(time.time())
    print "Last run time: " + __addon__.getSetting('welcome_timer')
    print "Current Time: " + str(currtime)
    if __addon__.getSetting('welcome_timer') == '' or int(__addon__.getSetting('welcome_timer')) <= currtime-3600: #14400
        print "Showing Welcome message"
        utils.TextBox()
    __addon__.setSetting('welcome_timer', str(currtime))
    checkKaraokeSetting()
    #      name,                url,          mode,                     iconimage,               page, id, param1, param2=""):
    addDir(__language__(70000), 'search.php', 'searchArtists',          art('searchArtistName'), '0',0, '')
    addDir(__language__(70001), 'search.php', 'searchSongs',            art('SearchSongName'), '0',0, '')
    addDir(__language__(70002), 'search.php', 'searchIDs',              art('SearchListID'), '0',0, '')
    addDir(__language__(70003), 'search.php', 'browseArtistsListSub',   art('BrowseAllArtists'), '0',0, '')
    addDir(__language__(70004), 'search.php', 'browseSongsListSub',     art('BrowseAllSongs'), '0',0, '')
    addDir(__language__(70011), 'search.php', 'getLatest',              art('FeaturedLatestSongs'), '0',0, '')
    addDir(__language__(70005), 'search.php', 'getPopular',             art('FeaturedMostPopular'), '0',0, '')
    # addDir(__language__(70010), 'search.php', 'getPopularLast7',        art('FeaturedMostPopular'), '0',0, '')
    addDir(__language__(70006), 'search.php', 'getLucky',               art('FeaturedFeelingLucky'), '0',0, '')
    addDir(__language__(70008), 'search.php', 'getQRCode',       	    art('MobileScanQR'), '0',0, '', '' , 0)
    addDir(__language__(70009), 'getnext.php', 'getQueue',       	    art('MobilePlayQueue'), '1','0', 'session', '' , 0)


def MODESWITCHER():

    params =    get_params()
    url =       None
    name =      None
    mode =      None
    page =      0
    id =        0
    param1 =    None
    param2 =    None

    
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
            page=urllib.unquote_plus(params["page"])
    except:
            pass
    try:
            id=urllib.unquote_plus(params["id"])
    except:
            pass
    try:
            param1=urllib.unquote_plus(params["param1"])
    except:
            pass
    try:
            param2=urllib.unquote_plus(params["param2"])
    except:
            pass

    print "Mode: "  +str(mode)
    print "URL: "   +str(url)
    print "Name: "  +str(name)
    print "Page: "  +str(page)
    print "ID: "    +str(id)
    print "param1: "+str(param1)
    print "param2: "+str(param2)


    for case in utils.switch(mode):
        if case('A'): pass
        if case(None):
            buggalo.trackUserFlow('None mode selected')
            HOME()
            break
        if case('searchArtists'):
            pass
        if case('searchSongs'):
            pass
        if case('searchIDs'):
            buggalo.trackUserFlow('Search: ' + str(mode) + ' - query: ' + str(param1))
            SEARCH(url,mode,page,param1)
            break
        if case('getSongsByArtist'):
            buggalo.trackUserFlow(str(mode) + ' - ' + str(id))
            BROWSESONGSFROMARTIST(url,mode,page,id)
            break
        if case('getSongsByArtist'):
            buggalo.trackUserFlow(str(mode) + ' - ' + str(id))
            BROWSESONGSFROMARTIST(url,mode,page,id)
            break
        if case('browseArtists'):
            buggalo.trackUserFlow(str(mode) + ' - query: ' + str(param1))
            BROWSEARTISTS(url,mode,page, str(param1))
            break
        if case('browseSongs'):
            buggalo.trackUserFlow(str(mode) + ' - query: ' + str(param1))
            BROWSESONGS(url,mode,page, str(param1))
            break
        if case('getVideo'):
            buggalo.trackUserFlow(str(mode) + ' - ' + str(id))
            KARAOKELINKS(url,id,param1)
            break
        if case('getLatest'):
            buggalo.trackUserFlow(str(mode) + ' - ' + str(page))
            BROWSELATEST(url,mode,page)
            break
        if case('getPopularLast7'):
            buggalo.trackUserFlow(str(mode))
            GETPOPULAR(url,mode)
            break
        if case('getPopular'):
            buggalo.trackUserFlow(str(mode))
            GETPOPULAR(url,mode)
            break
        if case('getLucky'):
            buggalo.trackUserFlow(str(mode))
            GETLUCKY(url,mode)
            break
        if case('browseArtistsListSub'):
            buggalo.trackUserFlow(str(mode))
            BROWSEARTISTSLISTSUB()
            break
        if case('browseSongsListSub'):
            buggalo.trackUserFlow(str(mode))
            BROWSESONGSLISTSUB()
            break
        if case('getQRCode'):
            buggalo.trackUserFlow(str(mode))
            GETQRCODE(url,mode)
            break
        if case('getQueue'):
            buggalo.trackUserFlow(str(mode))
            KARAOKELINKS(url,id,param1)
            break
        if case('test'):
            buggalo.trackUserFlow(str(mode))
            TEST(url,mode)
            break
        if case():
            buggalo.trackUserFlow('Default mode')
            checkKaraokeSetting()
            HOME()
            break


# When entering menu, automatically stop playing (workaround XBMC crashing)
xbmc.Player().stop()
MODESWITCHER()

"""
frina =  xbmc.getInfoLabel('System.FriendlyName')
videncinf =  xbmc.getInfoLabel('System.VideoEncoderInfo')
buildver = xbmc.getInfoLabel('System.buildversion')
osver =  xbmc.getInfoLabel('System.osversioninfo')
macaddr = xbmc.getInfoLabel('Network.MacAddress')
ipaddr = xbmc.getInfoLabel('Network.IPAddress')
print frina
print videncinf
print buildver
print osver
print macaddr
print ipaddr
print xbmc.getInfoLabel('System.KernelVersion')
"""

if int(sys.argv[1]) != -1:
    xbmcplugin.endOfDirectory(int(sys.argv[1]))