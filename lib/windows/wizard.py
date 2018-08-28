#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmcgui
import xbmc
import xbmcaddon

import lib.nakamoritools as nt

ADDON = xbmcaddon.Addon(id='script.module.nakamori')
CWD = ADDON.getAddonInfo('path').decode('utf-8')

_addon = xbmcaddon.Addon(id='plugin.video.nakamori')

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
        _addon.getSetting("ipaddress")

    def onInit(self):
        self.setProperty('script.module.nakamori.running', 'true')
        # bind controls & set default
        _address = self.getControl(IP_ADDRESS)
        _port = self.getControl(PORT_NUMBER)
        _login = self.getControl(LOGIN)
        _password = self.getControl(PASSWORD)
        _button_test = self.getControl(TEST_BUTTON)
        _button_save = self.getControl(SAVE_BUTTON)
        # navigation
        _address.setNavigation(_password, _port, _address, _button_test)  # up, down, left, right
        _port.setNavigation(_address, _login, _port, _button_test)
        _login.setNavigation(_port, _password, _login, _button_test)
        _password.setNavigation(_login, _address, _password, _button_test)
        _button_test.setNavigation(_button_save, _button_save, _login, _button_test)
        _button_save.setNavigation(_button_test, _button_test, _password, _button_save)
        # get current settings
        self.ip = _addon.getSetting("ipaddress")
        self.port = _addon.getSetting("port")
        self.login = _addon.getSetting("login")
        self.password = _addon.getSetting("password")
        self.apikey = _addon.getSetting("apikey")
        # populate controls
        _address.setText(self.ip)
        _port.setText(self.port)
        # _password.setType(xbmcgui.INPUT_TYPE_PASSWORD, '')  # k18
        _login.setText(self.login)
        _password.setText(self.password)
        _button_save.setEnabled(False)
        # set focus
        self.setFocus(_address)

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK:
            self.setProperty('script.module.nakamori.running', 'false')
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
            if _addon.getSetting("apikey") != "":
                self.setProperty('script.module.nakamori.running', 'false')
                self.close()
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
        _address = self.getControl(IP_ADDRESS).getText()
        _port = self.getControl(PORT_NUMBER).getText()
        _label_address = self.getControl(LABEL_IP_ADDRESS)
        _label_port = self.getControl(LABEL_PORT_NUMBER)
        # buttons
        _button_save = self.getControl(SAVE_BUTTON)

        if nt.get_server_status(ip=str(_address), port=str(_port), force=True):
            # save good address + port
            _addon.setSetting(id='good_ip', value=str(_address))
            _addon.setSetting(id='good_port', value=str(_port))
            _addon.setSetting(id='ipaddress', value=str(_address))
            _addon.setSetting(id='port', value=str(_port))
            _label_address.setLabel(label="IP Address", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
            _label_port.setLabel(label="Port", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
            _login = self.getControl(LOGIN).getText()
            _password = self.getControl(PASSWORD).getText()
            _label_login = self.getControl(LABEL_LOGIN)
            _label_password = self.getControl(LABEL_PASSWORD)
            _test_button = self.getControl(TEST_BUTTON)
            # populate info from edits
            nt.addon.setSetting(id="login", value=str(_login))
            nt.addon.setSetting(id="password", value=str(_password))
            # check auth
            b, a = nt.valid_user()
            if b:
                _test_button.setLabel(label='OK', textColor='0xff7aad5c', focusedColor='0xff7aad5c')
                _label_login.setLabel(label="Login", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
                _label_password.setLabel(label="Password", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
                _button_save.setEnabled(True)
                self.setup_ok = True
                _addon.setSetting(id='login', value='')
                _addon.setSetting(id='password', value='')
                _addon.setSetting(id='apikey', value=a)
            else:
                _test_button.setLabel(label='Test', textColor='0xFFDF1818', focusedColor='0xFFDF1818')
                _label_login.setLabel(label="Login", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
                _label_password.setLabel(label="Password", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
                _button_save.setEnabled(False)
                self.setup_ok = False
        else:
            _label_address.setLabel(label="IP Address", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
            _label_port.setLabel(label="Port", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
            _button_save.setEnabled(False)
            self.setup_ok = False
        xbmc.log('--- wizard.py = %s' % self.setup_ok, xbmc.LOGWARNING)
        if self.setup_ok:
            _addon.setSetting(id='wizard', value="1")
        else:
            _addon.setSetting(id='wizard', value="0")


def open_wizard():
    # xbmc.log('--- open_wizard : start', xbmc.LOGWARNING)
    ui = Wizard2('wizard.xml', CWD, 'default', '1080i')
    ui.doModal()
    del ui
    # xbmc.log('--- open_wizard : stop', xbmc.LOGWARNING)
