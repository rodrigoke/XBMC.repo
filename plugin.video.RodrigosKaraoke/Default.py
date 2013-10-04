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


#    xbmc.Player(xbmc.PLAYER_CORE_PAPLAYER).play(ContentPath)
import re
import os
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import buggalo
import urllib
import shutil
import zipfile
import urlresolver

# Official XBMC error report generator (won't send data without user confirmation)
buggalo.SUBMIT_URL = 'http://buggalo.rodrigo.be/submit.php'

# initialization
ADDON_NAME = 'plugin.video.RodrigosKaraoke'
ADDON_READABLENAME = 'Rodrigo\'s Karaoke Addon'
addon = xbmcaddon.Addon(ADDON_NAME)
PATH = xbmc.translatePath(addon.getAddonInfo('path')).decode('utf-8')
#TEMP_PATH = 'special://temp\\' + ADDON_NAME
#TEMP_PATH = 'special://temp'
TEMP_DL_DIR =  'tempdl'
url = None

#baseurl = 'http://partyanimals.be/karaoke/'
#filename = 'SFPL001-02 - All Saints - Never Ever.zip'
baseurl = 'http://www48.zippyshare.com/d/69120851/68924/'
filename = 'SFPL024-12 - Sham 69 - If The Kids Are United.zip'



print('KARAOKE')
print( xbmc.getCondVisibility('system.getbool(karaoke.enabled)'))

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
    # Progress bar hook
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        #print percent
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        print "DOWNLOAD CANCELLED" # need to get this part working        
        raise Exception("Canceled")

def getunzipped(theurl, thedir, thename):
    name = os.path.join(thedir, thename)
    try:
        if not os.path.exists(thedir):
            os.makedirs(thedir)
    except Exception:
        buggalo.onExceptionRaised()
        print "can't create directory"
        return
    try:
        if urlresolver.HostedMediaFile(theurl).valid_url():
            resolvedurl = urlresolver.resolve(theurl)
            dp = xbmcgui.DialogProgress()
            dp.create(ADDON_READABLENAME,"Downloading clip data", thename)
            name, hdrs = urllib.urlretrieve(resolvedurl, name,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
    except IOError, e:
        buggalo.onExceptionRaised()
        print "Can't retrieve %r to %r: %s" % (resolvedurl, thedir, e)
        return
    # Python unzip is rubbish!!! gave me corrupted unzips every time
    xbmc.executebuiltin('xbmc.extract(' + name + ')', True)
    
    # Remove the zip file
    os.unlink(name)

    
def deletedir(dirname):
    try:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
    except:
        buggalo.onExceptionRaised()
        print "can't delete directory"
        
try:
    fullURL = baseurl + urllib.quote(filename).encode('utf8')
    fullDir = os.path.join(PATH, TEMP_DL_DIR)
    
    #delete directory
    deletedir(fullDir)
 
    #download new file
    getunzipped(fullURL, fullDir, filename)

    fullFilePath = os.path.splitext(os.path.join(fullDir, filename))[0]
    fullFilePath = fullFilePath + '.mp3'
    

    xbmc.Player().play(fullFilePath)
    
except Exception as e:
    buggalo.onExceptionRaised()
    print (e)

    
#xbmcplugin.endOfDirectory(int(sys.argv[1]))
