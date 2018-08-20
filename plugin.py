import sys

import xbmc
import xbmcgui
import xbmcplugin

import routing

plugin = routing.Plugin(base_url='plugin://script.module.nakamori')


class Main:
    def __init__(self):
        self._parse_argv()
        for info in self.infos:
            if info == "calendar":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=calendar)')
            elif info == "wizard":
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=wizard)')
        else:
            plugin.run()

    def _parse_argv(self):
        args = sys.argv[2][1:]
        self.infos = []
        self.params = {"handle": plugin.handle}
        delimiter = "&"
        for arg in args.split(delimiter):
            if arg.startswith('info='):
                self.infos.append(arg[5:])


@plugin.route('/')
def root():
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    items = [
        ("calendar", "plugin-calendar", plugin.url_for(calendar, what="now")),
        ("wizard", "plugin-wizard", plugin.url_for(wizard))
    ]
    for key, value, key in items:
        li = xbmcgui.ListItem(label=value, thumbnailImage="DefaultFolder.png")
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=plugin.handle, url=key, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/calendar/<what>')
def calendar(what):
    xbmc.executebuiltin('RunScript(script.module.nakamori,?info=calendar)')
    pass


@plugin.route('/wizard')
def wizard():
    xbmc.executebuiltin('RunScript(script.module.nakamori,?info=wizard)')
    pass


if __name__ == "__main__":
    Main()
