import sys

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import routing
from kodi65 import addon


handle = int(sys.argv[1])

plugin = routing.Plugin()


class Main:
    def __init__(self):
        addon.set_global("nakamori_running", "true")
        self._parse_argv()
        for info in self.infos:
            xbmc.log('---- info in infos: %s' % info, xbmc.LOGERROR)
            if info == "calendar":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=calendar)')
        else:
            xbmc.log('----plugin.run', xbmc.LOGERROR)
            plugin.run()
        addon.clear_global("nakamori_running")

    def _parse_argv(self):
        args = sys.argv[2][1:]
        for arg in sys.argv:
            xbmc.log('-+-' + str(arg), xbmc.LOGERROR)
        self.infos = []
        self.params = {"handle": plugin.handle}
        delimiter = "&"
        for arg in args.split(delimiter):
            if arg.startswith('info='):
                self.infos.append(arg[5:])


@plugin.route('/')
def root():
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
    items = [
        ("calendar", "plugin-calendar", plugin.url_for(calendar, what="now")),
        ("wizard", "plugin-wizard", plugin.url_for(wizard))
    ]
    for key, value, key in items:
        li = xbmcgui.ListItem(label=value, thumbnailImage="DefaultFolder.png")
        xbmc.log('url created is %s' % key, xbmc.LOGERROR)
        xbmcplugin.addDirectoryItem(handle=plugin.handle, url=key, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(handle)


@plugin.route('/calendar/<what>')
def calendar(what):
    xbmc.executebuiltin('RunScript(script.module.nakamori,?info=calendar)')
    pass


@plugin.route('/wizard')
def wizard():
    xbmc.executebuiltin('RunScript(script.module.nakamori,?info=wizard)')
    pass


xbmc.log('---> plugin.py started', xbmc.LOGERROR)
if __name__ == "__main__":
    Main()
xbmc.log('---> plugin.py stopped', xbmc.LOGERROR)
