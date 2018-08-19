#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmcgui
import xbmc
import xbmcaddon

ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')

ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92


class Calendar(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        # super(Calendar, self).__init__()
        self.window_type = "window"
        self.data = kwargs['optional1']

    def onInit(self):
        # super(Calendar, self).onInit()
        self.window_id = xbmcgui.getCurrentWindowId()
        xbmc.executebuiltin('Container.SetViewMode(50)')
        
        listitems = []
        listitem1 = xbmcgui.ListItem('my first item')
        listitems.append(listitem1)
        listitem2 = xbmcgui.ListItem('my second item')
        listitems.append(listitem2)

        self.clearList()
        self.addItems(listitems)
        #xbmc.sleep(100)
        #self.setFocusId(self.getCurrentContainerId())
        xbmc.log('---> setFocus done.....', xbmc.LOGERROR)

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
            xbmc.log('---> onAction close.....', xbmc.LOGERROR)
        if action == ACTION_NAV_BACK:
            self.close()
            xbmc.log('---> onAction close.....', xbmc.LOGERROR)


def open_calendar():
    ui = Calendar('calendar.xml', CWD, 'default', '1080i', optional1='test')
    xbmc.log('---> main doModal before.....', xbmc.LOGERROR)
    ui.doModal()
    xbmc.log('---> main doModal after.....', xbmc.LOGERROR)
    del ui
