

#### Imports
import os, re, shutil, urllib, urllib2, pickle, time, glob                      # Import python function
import xbmc, xbmcaddon, xbmcgui, xbmcplugin                                     # Import XBMC plugins
import buggalo, urlresolver                                                     # Import 3rd party addons

try:
        from addon.common.addon import Addon
except:
        from t0mm0.common.addon import Addon 

## XBMC workaround
import _json
if not 'load' in dir(_json):
    import simplejson as _json

jsonurl = 'http://api.xbmckaraoke.com/'                                         # PHP JSON website (database)
#### Constants & initialization
buggalo.SUBMIT_URL = 'http://buggalo.tvaddons.ag/submit.php'                    # Official XBMC error report generator
ADDON_NAME = 'plugin.video.XBMCKaraoke'                                         # Addon namespace
__addon__ = xbmcaddon.Addon(ADDON_NAME)                                         # Initializing addon properties
__language__ = __addon__.getLocalizedString

class TextBox:
    # constants
    WINDOW = 10147
    CONTROL_LABEL = 1
    CONTROL_TEXTBOX = 5

    def __init__(self, *args, **kwargs):
        # activate the text viewer window
        xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW,))
        # get window
        self.win = xbmcgui.Window(self.WINDOW)
        # give window time to initialize
        xbmc.sleep(1000)
        self.setControls()

    def setControls(self):
        # set heading
        #heading = "PrimeWire v%s" % (_1CH.get_version())
		try:
			_json = loadJsonFromUrl(jsonurl + "search.php?type=getwelcome")
			if _json == None:
				xbmcgui.Dialog().ok(__addonname__, ' ', __language__(70111))
				return
			heading = _json[0]['welcome_header']
			text = _json[0]['welcome_content']
		except Exception as e:
			buggalo.onExceptionRaised()
			print (e)
			
		self.win.getControl(self.CONTROL_LABEL).setLabel(heading)
		self.win.getControl(self.CONTROL_TEXTBOX).setText(text)

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

class StopDownloading(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class QRWindow(xbmcgui.Window):
    
    def __init__(self):
        self.qrimg = ''
    
    def show(self):
        self.strActionInfo = xbmcgui.ControlLabel(300, 200, 600, 200, '', 'font14', '0xFFBBBBFF')
        self.addControl(self.strActionInfo)
        self.strActionInfo.setLabel(__language__(70105))
        
        # qrimg = 'http://api.xbmckaraoke.com/temp/qrcode.php.png'
        self.imgControl = xbmcgui.ControlImage(450,250,159,159, "")
        self.imgControl.setImage("")
        self.imgControl.setImage(self.qrimg)
        self.addControl(self.imgControl)
        self.button = xbmcgui.ControlButton(480, 420, 100, 35, 'OK', font='font14', alignment=2)
        self.addControl(self.button)
        # self.setFocus(self.button)

    def onControl(self, event):
        if event == self.button: 
            self.close()
            
    def QRlink(self, text):
        self.qrimg = text
		
		
def loadJsonFromUrl(url):
    data = None
    try:
        req = urllib2.Request(url)
        req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        req.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) XBMCKARAOKEADDON/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        response = urllib2.urlopen(req)
        data = _json.load(response)
    except Exception as ex:
        #print ex
        pass
    return data
	