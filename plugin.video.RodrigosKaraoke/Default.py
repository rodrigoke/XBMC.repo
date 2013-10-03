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
import re, os
import xbmcplugin,xbmcgui

import xbmc
import xbmcaddon
import buggalo
import urllib
import urllib2
import shutil

# Official XBMC error report generator (won't send data without user confirmation)
buggalo.SUBMIT_URL = 'http://buggalo.rodrigo.be/submit.php'

addon = xbmcaddon.Addon('plugin.video.RodrigosKaraoke')

baseurl = 'http://partyanimals.be/karaoke/'
filename = 'SFPL001-04 - All Saints - Bootie Call.zip'


def dlfile(file_name,file_mode,base_url):
    from urllib2 import Request, urlopen, URLError, HTTPError

    #create the url and the request
    url = base_url + file_name + mid_url + file_name + end_url 
    req = Request(url)

    # Open the url
    try:
        f = urlopen(req)
        print "downloading " + url

        # Open our local file for writing
        local_file = open(file_name, "wb" + file_mode)
        #Write to our local file
        local_file.write(f.read())
        local_file.close()

    #handle errors
    except HTTPError, e:
        print "HTTP Error:",e.code , url
    except URLError, e:
        print "URL Error:",e.reason , url

try:
 
    print (xbmc.translatePath(addon.getAddonInfo('path')).decode('utf-8') )

    #dlfile(
    

    print (urllib.quote(filename).encode('utf8'))
    ContentPath = 'special://home/media/SFHH01-1/test.mp3'
    #xbmc.Playerd().play(ContentPath)
    
except Exception as e:
    buggalo.onExceptionRaised()
    print (e)

    
#xbmcplugin.endOfDirectory(int(sys.argv[1]))
