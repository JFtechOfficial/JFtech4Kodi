
import xbmcgui
import xbmcplugin
import xbmcaddon
import simplejson as json
import hyperion_client
import pyxbmct
import socket
import routing

ADDON = xbmcaddon.Addon()
#ADDONNAME = ADDON.getAddonInfo('id')

plugin = routing.Plugin()

xbmcplugin.setContent(plugin.handle, 'files')

#path = os.path.dirname(os.path.realpath(__file__))
#color_path = os.path.join(xbmc.translatePath(path), "colors.json")
color_path = xbmc.translatePath(
    'special://home/addons/plugin.program.hyperion-controller/colors.json')
ip = str(ADDON.getSetting('ip'))
port = ADDON.getSetting('port')
apriority = ADDON.getSetting('priority')
h = hyperion_client.hyperion_client(ip, port)
debug = ADDON.getSetting('debug')
if debug:
    pass


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
        self.slider_valueR = pyxbmct.Label(
            '[COLOR FFFF0000]' + str(SLIDER_INIT_VALUE) + '[/COLOR]', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.slider_valueR, 0, 1)
        #
        slider_caption = pyxbmct.Label(translate(30007), alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(slider_caption, 0, 0)
        # Slider
        self.sliderR = pyxbmct.Slider()
        self.placeControl(self.sliderR, 0, 2, pad_y=10, columnspan=2)
        # self.slider.setPercent(SLIDER_INIT_VALUE)
        self.sliderR.setInt(SLIDER_INIT_VALUE, -10, 5, 255)

    def set_sliderG(self):
        # Slider value label
        SLIDER_INIT_VALUE = self.active_RGB[1]
        self.slider_valueG = pyxbmct.Label(
            '[COLOR FF00FF00]' + str(SLIDER_INIT_VALUE) + '[/COLOR]', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.slider_valueG, 1, 1)
        #
        slider_caption = pyxbmct.Label(translate(30008), alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(slider_caption, 1, 0)
        # Slider
        self.sliderG = pyxbmct.Slider()
        self.placeControl(self.sliderG, 1, 2, pad_y=10, columnspan=2)
        # self.slider.setPercent(SLIDER_INIT_VALUE)
        self.sliderG.setInt(SLIDER_INIT_VALUE, -10, 5, 255)

    def set_sliderB(self):
        # Slider value label
        SLIDER_INIT_VALUE = self.active_RGB[2]
        self.slider_valueB = pyxbmct.Label(
            '[COLOR FF0000FF]' + str(SLIDER_INIT_VALUE) + '[/COLOR]', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.slider_valueB, 2, 1)
        #
        slider_caption = pyxbmct.Label(translate(30009), alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(slider_caption, 2, 0)
        # Slider
        self.sliderB = pyxbmct.Slider()
        self.placeControl(self.sliderB, 2, 2, pad_y=10, columnspan=2)
        # self.slider.setPercent(SLIDER_INIT_VALUE)
        self.sliderB.setInt(SLIDER_INIT_VALUE, -10, 5, 255)

    def launch(self):
        red = self.sliderR.getInt()
        green = self.sliderG.getInt()
        blue = self.sliderB.getInt()
        try:
            global h
            h.set_RGBcolor(red=red, green=green, blue=blue, priority=apriority)
            line = translate(30010) + str(red) + ', ' + str(green) + \
                ', ' + str(blue) + ' on Hyperion ' + ip
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
    # 'http://www.weareclear.co.uk/wp-content/uploads/2017/12/logo.png'
    image = 'https://i.imgur.com/WowKBZT.png'
    li.setArt({'thumb': image,
               'icon': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(
        clear), listitem=li, isFolder=False)

    li = xbmcgui.ListItem(translate(30001))
    # 'https://teetribe.eu/wp-content/uploads/2018/05/RGB-Red-Green-Blue.png'
    image = 'https://imgur.com/2k0E5R1.png'
    li.setArt({'thumb': image,
               'icon': image,
               'fanart': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(colors),
                                listitem=li, isFolder=True)

    li = xbmcgui.ListItem(translate(30002))
    image = 'https://png.icons8.com/color/1600/color-wheel-2.png'
    li.setArt({'thumb': image,
               'icon': image,
               'fanart': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(effects),
                                listitem=li, isFolder=True)

    li = xbmcgui.ListItem(translate(30003))
    image = 'https://imgur.com/DdRsSe9.png'
    # 'https://sites.google.com/site/makecolorsimages/sliders-RGB_512x512.png'
    li.setArt({'thumb': image,
               'icon': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(RGB_sliders), listitem=li)

    li = xbmcgui.ListItem(translate(30004))
    image = 'https://cdn4.iconfinder.com/data/icons/meBaze-Freebies/512/setting.png'
    li.setArt({'thumb': image,
               'icon': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(
        settings), listitem=li, isFolder=False)

    li = xbmcgui.ListItem(translate(30005))
    image = 'https://chart.googleapis.com/chart?cht=qr&chl=https%3A%2F%2Fko-fi.com%2FY8Y0FW3V&chs=180x180&choe=UTF-8&chld=L|2'
    li.setArt({'thumb': image,
               'icon': image})
    xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(
        donate), listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/clear')
def clear():
    try:
        h.clear_all()
        xbmcgui.Dialog().notification(translate(30000), translate(30006))
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
        xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(
            color_launcher, color), listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/colors/<color>')
def color_launcher(color):
    with open(color_path) as f:
        colornames = json.load(f)
    try:
        h.set_RGBcolor(red=colornames[color][0], green=colornames[color]
                       [1], blue=colornames[color][2], priority=apriority)
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
            li = xbmcgui.ListItem(effect)
            xbmcplugin.addDirectoryItem(handle=plugin.handle, url=plugin.url_for(effect_launcher, effect), listitem=li)
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
