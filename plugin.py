#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import xbmc
import xbmcgui
import xbmcplugin

import routing

from proxy.python_version_proxy import python_proxy as pyproxy

plugin = routing.Plugin(base_url='plugin://script.module.nakamori')


def main():
        params = pyproxy.parse_parameters(sys.argv[2])
        if 'info' in params:
            if params['info'] == "calendar":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=calendar)')
            elif params['info'] == "wizard":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=wizard)')
            elif params['info'] == "clearcache":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=clearcache)')
            elif params['info'] == "information":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=information)')
            elif params['info'] == "settings":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=settings)')
        else:
            plugin.run()


@plugin.route('/')
def root():
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    items = [
        ("calendar", "calendar", plugin.url_for(calendar, when='0', page='0')),
        ("calendar", "calendar-add-14-days", plugin.url_for(calendar, when='0', page='14')),
        ("information", "information", plugin.url_for(information)),
        ("wizard", "wizard", plugin.url_for(wizard)),
        ("clear-cache", "clear-cache", plugin.url_for(clearcache)),
        ("settings", "settings", plugin.url_for(settings))
    ]
    for name, value, key in items:
        li = xbmcgui.ListItem(label=value, thumbnailImage="DefaultFolder.png")
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=plugin.handle, url=key, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/calendar/<when>/<page>/')
def calendar(when, page):
    xbmc.executebuiltin('RunScript(script.module.nakamori,?info=calendar&date=' + when + '&page=' + page + ')', True)
    return True


@plugin.route('/wizard')
def wizard():
    xbmc.executebuiltin('RunScript(script.module.nakamori,?info=wizard)', True)
    pass


@plugin.route('/clearcache')
def clearcache():
    xbmc.executebuiltin('RunScript(script.module.nakamori,?info=clearcache)', True)
    pass


@plugin.route('/information')
def information():
    xbmc.executebuiltin('RunScript(script.module.nakamori,?info=information)', True)
    pass


@plugin.route('/settings')
def settings():
    xbmc.executebuiltin('RunScript(script.module.nakamori,?info=settings)', True)
    pass


if __name__ == "__main__":
    main()
