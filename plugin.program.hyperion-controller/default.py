import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import urllib
import urlparse
import json
import hyperion_client
import pyxbmct
import os
import socket
import routing

#base_url = sys.argv[0]
#addon_handle = int(sys.argv[1])
#args = urlparse.parse_qs(sys.argv[2][1:])


ADDON = xbmcaddon.Addon()
#ADDONNAME = ADDON.getAddonInfo('id')

##mode = args.get('mode', None)
##divider = '-'

plugin = routing.Plugin()

xbmcplugin.setContent(plugin.handle, 'files')

color_path = xbmc.translatePath('special://home/addons/plugin.program.hyperion-controller/colors.json')
ip = str(ADDON.getSetting('ip'))
port = ADDON.getSetting('port')
apriority = ADDON.getSetting('priority') 
h = hyperion_client.hyperion_client(ip, port)

        
def translate(text):
    return ADDON.getLocalizedString(text).encode("utf-8")

##################################
    
class MyAddon(pyxbmct.AddonDialogWindow):

    def __init__(self, title=''):
        super(MyAddon, self).__init__(title)
        self.setGeometry(400, 240, 4, 4)
        self.active_RGB = [0, 0, 0]
        try:
            active = h.active_color("RGB")
            if len(active) == 3:
                self.active_RGB = active
        except socket.error:
            pass
        self.set_sliderR()
        self.set_sliderG()
        self.set_sliderB()
        # Connect key and mouse events for slider update feedback.
        self.connectEventList([pyxbmct.ACTION_MOVE_LEFT,
                               pyxbmct.ACTION_MOVE_RIGHT,
                               pyxbmct.ACTION_MOUSE_DRAG,
                               pyxbmct.ACTION_MOUSE_LEFT_CLICK],
                              self.slider_update)
        
        self.okButton = pyxbmct.Button('Ok')
        self.placeControl(self.okButton, 3, 2)
        self.connect(self.okButton, self.launch)
        self.closeButton = pyxbmct.Button(translate(30014))
        self.placeControl(self.closeButton, 3, 1)
        self.connect(self.closeButton, self.close)
        self.set_navigation()
        # Connect a key action (Backspace) to close the window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_sliderR(self):
        # Slider value label
        SLIDER_INIT_VALUE = self.active_RGB[0]
        self.slider_valueR = pyxbmct.Label('[COLOR FFFF0000]' + str(SLIDER_INIT_VALUE) + '[/COLOR]', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.slider_valueR, 0, 1)
        #
        slider_caption = pyxbmct.Label(translate(30007), alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(slider_caption, 0, 0)
        # Slider
        self.sliderR = pyxbmct.Slider()
        self.placeControl(self.sliderR, 0, 2, pad_y=10, columnspan=2)
        #self.slider.setPercent(SLIDER_INIT_VALUE)
        self.sliderR.setInt(SLIDER_INIT_VALUE, -10, 5, 255)


    def set_sliderG(self):
        # Slider value label
        SLIDER_INIT_VALUE = self.active_RGB[1]
        self.slider_valueG = pyxbmct.Label('[COLOR FF00FF00]' + str(SLIDER_INIT_VALUE) + '[/COLOR]', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.slider_valueG, 1, 1)
        #
        slider_caption = pyxbmct.Label(translate(30008), alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(slider_caption, 1, 0)
        # Slider
        self.sliderG = pyxbmct.Slider()
        self.placeControl(self.sliderG, 1, 2, pad_y=10, columnspan=2)
        #self.slider.setPercent(SLIDER_INIT_VALUE)
        self.sliderG.setInt(SLIDER_INIT_VALUE, -10, 5, 255)


    def set_sliderB(self):
        # Slider value label
        SLIDER_INIT_VALUE = self.active_RGB[2]
        self.slider_valueB = pyxbmct.Label('[COLOR FF0000FF]' + str(SLIDER_INIT_VALUE) + '[/COLOR]', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.slider_valueB, 2, 1)
        #
        slider_caption = pyxbmct.Label(translate(30009), alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(slider_caption, 2, 0)
        # Slider
        self.sliderB = pyxbmct.Slider()
        self.placeControl(self.sliderB, 2, 2, pad_y=10, columnspan=2)
        #self.slider.setPercent(SLIDER_INIT_VALUE)
        self.sliderB.setInt(SLIDER_INIT_VALUE, -10, 5, 255)
    

    def launch(self):
        red = self.sliderR.getInt()
        green = self.sliderG.getInt()
        blue = self.sliderB.getInt()
        try:
            global h
            h.set_RGBcolor(red=red, green=green, blue=blue, priority=apriority)
            line = translate(30010) + str(red) + ', ' + str(green) + ', ' + str(blue) + ' on Hyperion ' + ip
            xbmcgui.Dialog().notification(translate(30003), line)
            h.close_connection()
        except socket.error:
            xbmcgui.Dialog().notification(translate(30012), translate(30013), xbmcgui.NOTIFICATION_ERROR)
        self.close()


    def set_navigation(self):
        # Set navigation between controls
        self.sliderG.controlUp(self.sliderR)
        self.sliderR.controlDown(self.sliderG)
        self.sliderB.controlUp(self.sliderG)
        self.sliderG.controlDown(self.sliderB)
        self.okButton.controlDown(self.sliderB)
        self.sliderB.controlDown(self.okButton)
        self.okButton.controlUp(self.sliderB)
        self.okButton.controlLeft(self.closeButton)
        self.closeButton.controlRight(self.okButton)
        # Set initial focus
        self.setFocus(self.sliderR)

    def slider_update(self):
        # Update slider value label when the slider nib moves
        try:
            if self.getFocus() == self.sliderR:
                n = self.sliderR.getInt()
                if n < 0:
                    n = 0
                self.slider_valueR.setLabel('[COLOR FFFF0000]' + str(n) + '[/COLOR]')
            elif self.getFocus() == self.sliderG:
                n = self.sliderG.getInt()
                if n < 0:
                    n = 0
                self.slider_valueG.setLabel('[COLOR FF00FF00]' + str(n) + '[/COLOR]')
            elif self.getFocus() == self.sliderB:
                n = self.sliderB.getInt()
                if n < 0:
                    n = 0
                self.slider_valueB.setLabel('[COLOR FF0000FF]' + str(n) + '[/COLOR]')
        except (RuntimeError, SystemError):
            pass


    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=200',),
                                ('WindowClose', 'effect=fade start=100 end=0 time=200',)])

##################################


@plugin.route('/')
def index():
    li = xbmcgui.ListItem(translate(30000))
    image='https://i.imgur.com/WowKBZT.png'#'http://www.weareclear.co.uk/wp-content/uploads/2017/12/logo.png'
    li.setArt({'thumb': image,
                'icon': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(clear), listitem=li, isFolder=False)

    li = xbmcgui.ListItem(translate(30001))
    image='https://imgur.com/2k0E5R1.png'#'https://teetribe.eu/wp-content/uploads/2018/05/RGB-Red-Green-Blue.png'
    li.setArt({'thumb': image,
                'icon': image,
              'fanart': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(colors),
                                listitem=li, isFolder=True)

    li = xbmcgui.ListItem(translate(30002))
    image='https://png.icons8.com/color/1600/color-wheel-2.png'
    li.setArt({'thumb': image,
                'icon': image,
              'fanart': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(effects),
                                listitem=li, isFolder=True)

    li = xbmcgui.ListItem(translate(30003))
    image='https://imgur.com/DdRsSe9.png'#'https://imgur.com/2HxFrHl.png'
    #'https://sites.google.com/site/makecolorsimages/sliders-RGB_512x512.png'
    li.setArt({'thumb': image,
                'icon': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(RGB_sliders), listitem=li)

    li = xbmcgui.ListItem(translate(30004))
    image='https://cdn4.iconfinder.com/data/icons/meBaze-Freebies/512/setting.png'
    li.setArt({'thumb': image,
                'icon': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(settings), listitem=li, isFolder=False)
 
    li = xbmcgui.ListItem(translate(30005))
    image='https://chart.googleapis.com/chart?cht=qr&chl=https%3A%2F%2Fko-fi.com%2FY8Y0FW3V&chs=180x180&choe=UTF-8&chld=L|2'
    li.setArt({'thumb': image,
                'icon': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(donate), listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/clear')
def clear():
    try:
        h.clear_all()
        xbmcgui.Dialog().notification(translate(30000), translate(30005))
        h.close_connection()
    except socket.error:
        xbmcgui.Dialog().notification(translate(30012), translate(30013), xbmcgui.NOTIFICATION_ERROR)


@plugin.route('/colors')
def colors():
    with open(color_path) as f:
        colornames = json.load(f)            
    for color in colornames:
        hexColor = '%02x%02x%02x' % tuple(colornames[color])
        img = 'https://dummyimage.com/100x100/' + hexColor + '/' + hexColor + '.jpg'
        li = xbmcgui.ListItem(color)
        li.setArt({'thumb': img,
                    'icon': img,
                    'fanart': img})       
        xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(color_launcher, color), listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/colors/<color>')
def color_launcher(color):
    with open(color_path) as f:
        colornames = json.load(f)
    try:
        h.set_RGBcolor(red=colornames[color][0],green=colornames[color][1],blue=colornames[color][2], priority=apriority)
        line = translate(30010) + color + translate(30011) + ip
        xbmcgui.Dialog().notification(translate(30001), line)
        h.close_connection()
    except socket.error:
        xbmcgui.Dialog().notification(translate(30012), translate(30013), xbmcgui.NOTIFICATION_ERROR)


@plugin.route('/effects')
def effects():
    try:
        effectnames = h.effects_names()
        for effect in effectnames:
            #url = 'http://www.vidsplay.com/wp-content/uploads/2017/04/alligator.mp4'
            li = xbmcgui.ListItem(effect)
            xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(effect_launcher, effects), listitem=li)
    except socket.error:
        xbmcgui.Dialog().notification(translate(30012), translate(30013), xbmcgui.NOTIFICATION_ERROR)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/effects/<effect>')
def effect_launcher(effect):
    try:
        h.set_effect(effectName=effect, priority=apriority)
        line = translate(30010) + effect + translate(30011) + ip
        xbmcgui.Dialog().notification(translate(30002), line)
        h.close_connection()
    except socket.error:
        xbmcgui.Dialog().notification(translate(30012), translate(30013), xbmcgui.NOTIFICATION_ERROR)


@plugin.route('/RGB_sliders')
def RGB_sliders():
    window = MyAddon(translate(30003))
    window.doModal()
    # Destroy the instance explicitly because
    # underlying xbmcgui classes are not garbage-collected on exit.
    del window


@plugin.route('/settings')
def settings():
    ADDON.openSettings()


@plugin.route('/donate')
def donate():
    pass


if __name__ == '__main__':
    plugin.run()

"""

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


def launching(foldersplit):
    if len(foldersplit) == 2:
        name = foldersplit[1]
    else:
        name1 = ''
        for i in range(1,len(foldersplit)):
            name1 += foldersplit[i] + divider
        name = name1[:-1]
    return name


if mode is None:
    url = build_url({'mode': 'folder', 'foldername': 'Clear All'})
    li = xbmcgui.ListItem('Clear all effects/color')
    image='https://i.imgur.com/WowKBZT.png'#'http://www.weareclear.co.uk/wp-content/uploads/2017/12/logo.png'
    li.setArt({'thumb': image,
                'icon': image})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    
    url = build_url({'mode': 'folder', 'foldername': 'Color'})
    li = xbmcgui.ListItem('Color')
    image='https://imgur.com/2k0E5R1.png'#'https://teetribe.eu/wp-content/uploads/2018/05/RGB-Red-Green-Blue.png'
    li.setArt({'thumb': image,
                'icon': image,
              'fanart': image})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'folder', 'foldername': 'Effects'})
    li = xbmcgui.ListItem('Effects')
    image='https://png.icons8.com/color/1600/color-wheel-2.png'
    li.setArt({'thumb': image,
                'icon': image,
              'fanart': image})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)
    sliders = 'RGB Sliders'
    url = build_url({'mode': 'folder', 'foldername': sliders})
    li = xbmcgui.ListItem(sliders)
    image='https://imgur.com/2HxFrHl.png'#'https://sites.google.com/site/makecolorsimages/sliders-RGB_512x512.png'
    li.setArt({'thumb': image,
                'icon': image})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    
    Settings = 'Settings'
    url = build_url({'mode': 'folder', 'foldername': Settings})
    li = xbmcgui.ListItem(Settings)
    image='https://cdn4.iconfinder.com/data/icons/meBaze-Freebies/512/setting.png'
    li.setArt({'thumb': image,
                'icon': image})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

    Donate = 'Support me here: https://ko-fi.com/Y8Y0FW3V '
    url = build_url({'mode': 'folder', 'foldername': Donate})
    li = xbmcgui.ListItem(Donate)
    image='https://chart.googleapis.com/chart?cht=qr&chl=https%3A%2F%2Fko-fi.com%2FY8Y0FW3V&chs=180x180&choe=UTF-8&chld=L|2'
    li.setArt({'thumb': image,
                'icon': image})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    
    #xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'folder':
    foldername = args['foldername'][0]

    if foldername == 'Clear All':
        try:
            h.clear_all()
            line = 'clearing...'
            xbmcgui.Dialog().notification(foldername, line)
            h.close_connection()
        except socket.error:
            xbmcgui.Dialog().notification(translate(30012), translate(30013), xbmcgui.NOTIFICATION_ERROR)

    
    foldersplit = foldername.split(divider)
    if foldersplit[0] == 'Effects':
        if foldername == 'Effects':
            try:
                effectnames =  h.effects_names()#['Snake', 'Rainbow swirl fast']
                for e in effectnames:
                    #url = 'http://www.vidsplay.com/wp-content/uploads/2017/04/alligator.mp4'
                    url = build_url({'mode': 'folder', 'foldername': foldername + divider + e })
                    li = xbmcgui.ListItem(e)
                    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
            except socket.error:
                xbmcgui.Dialog().notification(translate(30012), translate(30013), xbmcgui.NOTIFICATION_ERROR)


        elif len(foldersplit) > 1:
            nome = launching(foldersplit)
            try:
                h.set_effect(effectName=nome, priority=apriority)
                line = translate(30010) + nome + translate(30011) + ip
                xbmcgui.Dialog().notification(foldersplit[0], line)
                h.close_connection()
            except socket.timeout:
                xbmcgui.Dialog().notification(translate(30012), translate(30013), xbmcgui.NOTIFICATION_ERROR)

    elif foldersplit[0] == 'Color':
        with open(color_path) as f:
            colornames = json.load(f)
        
        if foldername == 'Color':            
            for c in colornames:
                url = build_url({'mode': 'folder', 'foldername': foldername + divider + c})
                hexColor = '%02x%02x%02x' % tuple(colornames[c])
                img = 'https://dummyimage.com/100x100/' + hexColor + '/' + hexColor + '.jpg'
                li = xbmcgui.ListItem(c)
                li.setArt({'thumb': img,
                            'icon': img,
                            'fanart': img})       
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
            #xbmcplugin.endOfDirectory(addon_handle)

        elif len(foldersplit) > 1:
            nome = launching(foldersplit)
            try:
                h.set_RGBcolor(red=colornames[nome][0],green=colornames[nome][1],blue=colornames[nome][2], priority=apriority)
                line = translate(30010) + nome + translate(30011) + ip
                xbmcgui.Dialog().notification(foldersplit[0], line)
                h.close_connection()
            except socket.error:
                xbmcgui.Dialog().notification(translate(30012), translate(30013), xbmcgui.NOTIFICATION_ERROR)

    elif foldername == 'RGB Sliders':
        #xbmcgui.Dialog().ok(foldername, 'apre un control panel con 3 sliders')
        window = MyAddon(foldername)
        window.doModal()
        # Destroy the instance explicitly because
        # underlying xbmcgui classes are not garbage-collected on exit.
        del window

    elif foldername == 'Settings':
        ADDON.openSettings()
    
xbmcplugin.endOfDirectory(addon_handle)
"""
