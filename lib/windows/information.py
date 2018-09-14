# -*- coding: utf-8 -*-
import os

import xbmcgui
import xbmcaddon
import xml.etree.ElementTree as ET

ADDON = xbmcaddon.Addon(id='script.module.nakamori')
CWD = ADDON.getAddonInfo('path').decode('utf-8')

ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

CONTENT_TEXTBOX = 303


class Information(xbmcgui.WindowXMLDialog):
    def __init__(self, xmlFile, resourcePath, skin, skinRes):
        self.window_type = "window"

    def onInit(self):       
        _textbox = self.getControl(CONTENT_TEXTBOX)
        tree = ET.parse(os.path.join(xbmcaddon.Addon(id='plugin.video.nakamori').getAddonInfo('path').decode('utf-8'),
                                     'addon.xml'))
        root = tree.getroot()
        news = root.findall(".//*[@point='xbmc.addon.metadata']/news")
        _textbox.setText(news[0].text)
        self.setFocus(_textbox)

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK:
            self.close()

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def onClick(self, control):
        pass


def open_information():
    ui = Information('information.xml', CWD, 'default', '1080i')
    ui.doModal()
    del ui
