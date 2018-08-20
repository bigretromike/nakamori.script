#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmcgui
import xbmc
import xbmcaddon

import lib.nakamoritools as nt

ADDON = xbmcaddon.Addon()
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
        self.setup_ok = False
        self.apikey = ''

    def onInit(self):
        # bind controls
        _address = self.getControl(IP_ADDRESS)
        _port = self.getControl(PORT_NUMBER)
        _login = self.getControl(LOGIN)
        _password = self.getControl(PASSWORD)
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

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_NAV_BACK:
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
                self.close()
            else:
                if xbmcgui.Dialog().yesno(nt.addon.getLocalizedString(30079),
                                          nt.addon.getLocalizedString(30080),
                                          nt.addon.getLocalizedString(30081)):
                    self.setup_ok = False
                    self.close()

    # custom functions
    def _test_connection(self):
        _address = self.getControl(IP_ADDRESS).getText()
        _port = self.getControl(PORT_NUMBER).getText()
        _label_address = self.getControl(LABEL_IP_ADDRESS)
        _label_port = self.getControl(LABEL_PORT_NUMBER)
        if nt.get_server_status(ip=str(_address), port=str(_port), force=True):
            nt.addon.setSetting(id="ipaddress", value=str(_address))
            nt.addon.setSetting(id="port", value=str(_port))
            _label_address.setLabel(label="IP Address", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
            _label_port.setLabel(label="Port", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
            # check auth
            nt.addon.setSetting(id="apikey", value="")
            _login = self.getControl(LOGIN).getText()
            _password = self.getControl(PASSWORD).getText()
            _label_login = self.getControl(LABEL_LOGIN)
            _label_password = self.getControl(LABEL_PASSWORD)
            _test_button = self.getControl(TEST_BUTTON)
            nt.addon.setSetting(id="login", value=str(_login))
            nt.addon.setSetting(id="password", value=str(_password))
            if nt.valid_user():
                _test_button.setLabel(label='OK', textColor='0xff7aad5c', focusedColor='0xff7aad5c')
                _label_login.setLabel(label="Login", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
                _label_password.setLabel(label="Password", textColor='0xff7aad5c', focusedColor='0xff7aad5c')
                self.setup_ok = True
            else:
                _test_button.setLabel(label='Test', textColor='0xFFDF1818', focusedColor='0xFFDF1818')
                _label_login.setLabel(label="Login", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
                _label_password.setLabel(label="Password", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
                self.setup_ok = False
        else:
            _label_address.setLabel(label="IP Address", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
            _label_port.setLabel(label="Port", textColor='0xFFDF1818', focusedColor='0xFFDF1818')
            self.setup_ok = False


def open_wizard():
    ui = Wizard2('wizard.xml', CWD, 'default', '1080i')
    xbmc.log('---> main doModal before.....', xbmc.LOGERROR)
    ui.doModal()
    xbmc.log('---> main doModal after.....', xbmc.LOGERROR)
    del ui
