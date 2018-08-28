import sys

import xbmc
import xbmcgui
import xbmcplugin

import routing

import lib.nakamoritools as nt

plugin = routing.Plugin(base_url='plugin://script.module.nakamori')


class Main:
    def __init__(self):
        self.params = nt.parse_parameters(sys.argv[2])
        if 'info' in self.params:
            if self.params['info'] == "calendar":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=calendar)')
            elif self.params['info'] == "wizard":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=wizard)')
        else:
            plugin.run()


@plugin.route('/')
def root():
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    items = [
        ("calendar", "plugin-calendar", plugin.url_for(calendar, when='0', page='0')),
        ("calendar", "plugin-calendar-14-days", plugin.url_for(calendar, when='0', page='14')),
        ("wizard", "plugin-wizard", plugin.url_for(wizard))
    ]
    for key, value, key in items:
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


if __name__ == "__main__":
    xbmc.log('--- plugin.py : start', xbmc.LOGWARNING)
    Main()
    xbmc.log('--- plugin.py : stop', xbmc.LOGWARNING)
