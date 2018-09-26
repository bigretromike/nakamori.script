# -*- coding: utf-8 -*-

import xbmcgui
import xbmc
import xbmcaddon

import lib.nakamoritools as nt

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


class Wizard2(xbmcgui.WindowXML):
    def __init__(self, xmlFile, resourcePath, skin, skinRes):
        self.window_type = "window"
        self.ip = None
        self.port = None
        self.login = ''
        self.password = ''
        self.apikey = ''
        # additional variables
        self.setup_ok = False
        self._address = None
        self._port = None
        self._login = None
        self._password = None
        self._button_test = None
        self._button_save = None
        self._label_address = None
        self._label_port = None
        self._label_login = None
        self._label_password = None

    def onInit(self):
        self.setProperty('script.module.nakamori.running', 'true')
        # bind controls & set default
        self._address = self.getControl(IP_ADDRESS)
        self._port = self.getControl(PORT_NUMBER)
        self._login = self.getControl(LOGIN)
        self._password = self.getControl(PASSWORD)
        self._button_test = self.getControl(TEST_BUTTON)
        self._button_save = self.getControl(SAVE_BUTTON)
        self._label_address = self.getControl(LABEL_IP_ADDRESS)
        self._label_port = self.getControl(LABEL_PORT_NUMBER)
        self._label_login = self.getControl(LABEL_LOGIN)
        self._label_password = self.getControl(LABEL_PASSWORD)
        # navigation
        self._address.setNavigation(self._password, self._port, self._address, self._button_test)  # up, down, left, right
        self._port.setNavigation(self._address, self._login, self._port, self._button_test)
        self._login.setNavigation(self._port, self._password, self._login, self._button_test)
        self._password.setNavigation(self._login, self._address, self._password, self._button_test)
        self._button_test.setNavigation(self._button_save, self._button_save, self._login, self._button_test)
        self._button_save.setNavigation(self._button_test, self._button_test, self._password, self._button_save)
        # get current settings
        self.ip = nt.addon.getSetting("ipaddress")
        self.port = nt.addon.getSetting("port")
        self.login = nt.addon.getSetting("login")
        self.password = nt.addon.getSetting("password")
        self.apikey = nt.addon.getSetting("apikey")
        # populate controls
        self._address.setText(self.ip)
        self._port.setText(self.port)
        # self._password.setType(xbmcgui.INPUT_TYPE_PASSWORD, '')  # k18
        self._login.setText(self.login)
        self._password.setText(self.password)
        cansave = self.apikey != '' and nt.addon.getSetting('good_ip') == self.ip and nt.addon.getSetting('good_ip') != ''
        self._button_save.setEnabled(cansave)
        # set focus
        # self.setFocus(self._address)

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.setProperty('script.module.nakamori.running', 'false')
            if nt.addon.getSetting('apikey') != '':
                nt.addon.setSetting('wizard', '1')
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
            if nt.addon.getSetting("apikey") != "":
                self.setProperty('script.module.nakamori.running', 'false')
                self.close()
                xbmc.executebuiltin('RunPlugin(plugin.video.nakamori)')
            else:
                if xbmcgui.Dialog().yesno(nt.addon.getLocalizedString(30079),
                                          nt.addon.getLocalizedString(30080),
                                          nt.addon.getLocalizedString(30081)):
                    self.setup_ok = False
                    self.setProperty('script.module.nakamori.running', 'false')
                    self.close()

    # custom functions
    def _test_connection(self):
        # edits
        # self._address = self.getControl(IP_ADDRESS).getText()
        # self._port = self.getControl(PORT_NUMBER).getText()
        # self._label_address = self.getControl(LABEL_IP_ADDRESS)
        # self._label_port = self.getControl(LABEL_PORT_NUMBER)
        # buttons
        # self._button_save = self.getControl(SAVE_BUTTON)

        if nt.get_server_status(ip=str(self._address), port=str(self._port)):
            # save good address + port
            nt.addon.setSetting(id='good_ip', value=str(self._address))
            nt.addon.setSetting(id='good_port', value=str(self._port))
            nt.addon.setSetting(id='ipaddress', value=str(self._address))
            nt.addon.setSetting(id='port', value=str(self._port))
            self._label_address.setLabel(label="IP Address", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
            self._label_port.setLabel(label="Port", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
            # self.text_login = self._login.getText()
            # self.text_password = self._password.getText()
            # self._label_login = self.getControl(LABEL_LOGIN)
            # self._label_password = self.getControl(LABEL_PASSWORD)
            # self._test_button = self.getControl(TEST_BUTTON)
            # populate info from edits
            nt.addon.setSetting(id="login", value=str(self._login.getText()))
            nt.addon.setSetting(id="password", value=str(self._password.getText()))
            # check auth
            b, a = nt.valid_user()
            if b:
                self._button_test.setLabel(label='OK', textColor='0xff7aad5c', focusedColor='0xff7aad5c')
                self._label_login.setLabel(label="Login", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
                self._label_password.setLabel(label="Password", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
                self._button_save.setLabel(label='Save', textColor='0xAAFFFFFF', focusedColor='0xFFFFFFFF')
                self._button_save.setEnabled(True)
                self.setup_ok = True
                nt.addon.setSetting(id='login', value='')
                nt.addon.setSetting(id='password', value='')
                nt.addon.setSetting(id='apikey', value=a)
            else:
                self._button_test.setLabel(label='Test', textColor='0xFFDF1818', focusedColor='0xFFDF1818')
                self._label_login.setLabel(label="Login", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
                self._label_password.setLabel(label="Password", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
                self._button_save.setEnabled(False)
                self.setup_ok = False
        else:
            self._label_address.setLabel(label="IP Address", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
            self._label_port.setLabel(label="Port", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
            self._button_save.setEnabled(False)
            self.setup_ok = False
        xbmc.log('--- wizard.py = %s' % self.setup_ok, xbmc.LOGWARNING)
        if self.setup_ok:
            nt.addon.setSetting(id='wizard', value="1")
        else:
            nt.addon.setSetting(id='wizard', value="0")


def open_wizard():
    ui = Wizard2('wizard.xml', CWD, 'Default', '1080i')
    ui.doModal()
    del ui
