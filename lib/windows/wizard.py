# -*- coding: utf-8 -*-

import xbmcgui

from nakamori_utils import nakamoritools as nt
from nakamori_utils.globalvars import *

ADDON = xbmcaddon.Addon(id='script.module.nakamori')
CWD = ADDON.getAddonInfo('path').decode('utf-8')

TEST_BUTTON = 201
SAVE_BUTTON = 202
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
IP_ADDRESS = 203
PORT_NUMBER = 204
LOGIN = 205
LABEL_PASSWORD = 306
LABEL_IP_ADDRESS = 303
LABEL_PORT_NUMBER = 304
LABEL_LOGIN = 305
PASSWORD = 206
CENTER_Y = 6
CENTER_X = 2

# resources
RSC_IP = ADDON.getLocalizedString(30002)
RSC_PORT = ADDON.getLocalizedString(30003)
RSC_USERNAME = ADDON.getLocalizedString(30004)
RSC_PASSWORD = ADDON.getLocalizedString(30005)
RSC_TEST = ADDON.getLocalizedString(30006)
RSC_SAVE = ADDON.getLocalizedString(30007)

COLOR_RED = '0xFFDF1818'
COLOR_RED_FOCUSED = '0xFFFF1010'
COLOR_WHITE = '0xAAFFFFFF'
COLOR_WHITE_FOCUSED = '0xFFFFFFFF'
COLOR_GREEN = '0xFF18DD18'
COLOR_GREEN_FOCUSED = '0xFF10FF10'


class Wizard2(xbmcgui.WindowXML):
    def __init__(self, xmlFile, resourcePath, skin, skinRes):
        self.window_type = 'window'
        self.ip = None
        self.port = None
        self.login = ''
        self.password = ''
        self.apikey = ''
        # additional variables
        self.setup_ok = False
        self._button_test = None
        self._button_save = None
        self._label_address = None
        self._label_port = None
        self._label_login = None
        self._label_password = None

    def onInit(self):
        self.setProperty('script.module.nakamori.running', 'true')
        # static bind
        self._button_test = self.getControl(TEST_BUTTON)
        self._button_save = self.getControl(SAVE_BUTTON)
        self._label_address = self.getControl(LABEL_IP_ADDRESS)
        self._label_port = self.getControl(LABEL_PORT_NUMBER)
        self._label_login = self.getControl(LABEL_LOGIN)
        self._label_password = self.getControl(LABEL_PASSWORD)
        # navigation
        self.getControl(IP_ADDRESS).setNavigation(self.getControl(PASSWORD), self.getControl(PORT_NUMBER), self.getControl(IP_ADDRESS), self._button_test)  # up, down, left, right
        self.getControl(PORT_NUMBER).setNavigation(self.getControl(IP_ADDRESS), self.getControl(LOGIN), self.getControl(PORT_NUMBER), self._button_test)
        self.getControl(LOGIN).setNavigation(self.getControl(PORT_NUMBER), self.getControl(PASSWORD), self.getControl(LOGIN), self._button_test)
        self.getControl(PASSWORD).setNavigation(self.getControl(LOGIN), self.getControl(IP_ADDRESS), self.getControl(PASSWORD), self._button_test)
        self._button_test.setNavigation(self._button_save, self._button_save, self.getControl(LOGIN), self._button_test)
        self._button_save.setNavigation(self._button_test, self._button_test, self.getControl(PASSWORD), self._button_save)
        # get current settings
        self.ip = plugin_addon.getSetting('ipaddress')
        self.port = plugin_addon.getSetting('port')
        self.login = plugin_addon.getSetting('login')
        self.password = plugin_addon.getSetting('password')
        self.apikey = plugin_addon.getSetting('apikey')
        # populate controls
        self.getControl(IP_ADDRESS).setText(self.ip)
        self.getControl(PORT_NUMBER).setText(self.port)
        # self.getControl(PASSWORD).setType(xbmcgui.INPUT_TYPE_PASSWORD, '')  # k18
        self.getControl(LOGIN).setText(self.login)
        self.getControl(PASSWORD).setText(self.password)

        self._button_test.setLabel(label=RSC_TEST, textColor=COLOR_WHITE, focusedColor=COLOR_WHITE_FOCUSED)

        cansave = self.apikey != '' and plugin_addon.getSetting('good_ip') == self.ip and plugin_addon.getSetting('good_ip') != ''
        self._button_save.setEnabled(cansave)
        if cansave:
            self._button_save.setLabel(label=RSC_SAVE, textColor=COLOR_WHITE, focusedColor=COLOR_WHITE_FOCUSED)
        else:
            self._button_save.setLabel(label=RSC_SAVE, textColor=COLOR_RED, focusedColor=COLOR_RED_FOCUSED)
        # set focus
        self.setFocus(self.getControl(IP_ADDRESS))

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.setProperty('script.module.nakamori.running', 'false')
            if plugin_addon.getSetting('apikey') != '':
                plugin_addon.setSetting('wizard', '1')
            self.close()
        if action == ACTION_NAV_BACK:
            xbmc.log('click close X', xbmc.LOGWARNING)
            self.close()

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def onClick(self, control):
        if control == TEST_BUTTON:
            self._test_connection()
            pass

        if control == SAVE_BUTTON:
            if plugin_addon.getSetting('apikey') != '':
                self.setProperty('script.module.nakamori.running', 'false')
                self.close()
                xbmc.executebuiltin('RunPlugin(plugin.video.nakamori)')
            else:
                if xbmcgui.Dialog().yesno(ADDON.getLocalizedString(30034),
                                          ADDON.getLocalizedString(30035),
                                          ADDON.getLocalizedString(30036)):
                    self.setup_ok = False
                    self.setProperty('script.module.nakamori.running', 'false')
                    self.close()

    # custom functions
    def _test_connection(self):
        if nt.get_server_status(ip=str(self.getControl(IP_ADDRESS).getText()), port=str(self.getControl(PORT_NUMBER).getText())):
            # save good address + port
            plugin_addon.setSetting(id='good_ip', value=str(self.getControl(IP_ADDRESS).getText()))
            plugin_addon.setSetting(id='good_port', value=str(self.getControl(PORT_NUMBER).getText()))
            plugin_addon.setSetting(id='ipaddress', value=str(self.getControl(IP_ADDRESS).getText()))
            plugin_addon.setSetting(id='port', value=str(self.getControl(PORT_NUMBER).getText()))
            self._label_address.setLabel(label=RSC_IP, textColor=COLOR_GREEN, focusedColor=COLOR_WHITE_FOCUSED)
            self._label_port.setLabel(label=RSC_PORT, textColor=COLOR_GREEN, focusedColor=COLOR_WHITE_FOCUSED)
            # populate info from edits
            plugin_addon.setSetting(id='login', value=str(self.getControl(LOGIN).getText()))
            plugin_addon.setSetting(id='password', value=str(self.getControl(PASSWORD).getText()))
            # check auth
            b, a = nt.valid_user()
            if b:
                self._button_test.setLabel(label=RSC_TEST, textColor=COLOR_GREEN, focusedColor=COLOR_WHITE_FOCUSED)
                self._label_login.setLabel(label=RSC_USERNAME, textColor=COLOR_GREEN, focusedColor=COLOR_WHITE_FOCUSED)
                self._label_password.setLabel(label=RSC_PASSWORD, textColor=COLOR_GREEN, focusedColor=COLOR_WHITE_FOCUSED)
                self._button_save.setLabel(label=RSC_SAVE, textColor=COLOR_GREEN, focusedColor=COLOR_WHITE_FOCUSED)
                self._button_save.setEnabled(True)
                self.setup_ok = True
                plugin_addon.setSetting(id='login', value='')
                plugin_addon.setSetting(id='password', value='')
                plugin_addon.setSetting(id='apikey', value=a)
            else:
                self._button_test.setLabel(label=RSC_TEST, textColor=COLOR_RED, focusedColor=COLOR_RED_FOCUSED)
                self._label_login.setLabel(label=RSC_USERNAME, textColor=COLOR_RED, focusedColor=COLOR_RED_FOCUSED)
                self._label_password.setLabel(label=RSC_PASSWORD, textColor=COLOR_RED, focusedColor=COLOR_RED_FOCUSED)
                self._button_save.setEnabled(False)
                self.setup_ok = False
        else:
            self._label_address.setLabel(label=RSC_IP, textColor=COLOR_RED, focusedColor=COLOR_RED_FOCUSED)
            self._label_port.setLabel(label=RSC_PORT, textColor=COLOR_RED, focusedColor=COLOR_RED_FOCUSED)
            self._button_save.setEnabled(False)
            self.setup_ok = False
        xbmc.log('--- wizard.py = %s' % self.setup_ok, xbmc.LOGWARNING)
        if self.setup_ok:
            plugin_addon.setSetting(id='wizard', value='1')
        else:
            plugin_addon.setSetting(id='wizard', value='0')


def open_wizard():
    ui = Wizard2('wizard.xml', CWD, 'Default', '1080i')
    ui.doModal()
    del ui
