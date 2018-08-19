import sys
import xbmc
import xbmcaddon
import lib.windows.calendar as calendar

from kodi65 import addon


class Main:
    def __init__(self):
        addon.set_global("nakamori_running", "true")
        self._parse_argv()

        if not self.infos:
            xbmc.log('---> default.py infos=None', xbmc.LOGERROR)
            #calendar.open_calendar()
        else:
            xbmc.log('---> default.py infos=calendar START', xbmc.LOGERROR)
            if 'calendar' in self.infos:
                addon.set_global('nakamori.active', "true")
                calendar.open_calendar()
                addon.clear_global('nakamori.active')
                xbmc.log('---> default.py infos=calendar END', xbmc.LOGERROR)
        addon.clear_global("nakamori_running")

    def _parse_argv(self):
        self.infos = []
        for arg in sys.argv:
            xbmc.log('---[ arg ]: %s' % arg, xbmc.LOGERROR)
        self.params = {"handle": None}
        for arg in sys.argv:
            xbmc.log('??? [ arg ]: %s' % arg, xbmc.LOGERROR)
            if arg.startswith('?info='):
                self.infos.append(arg[6:])
                xbmc.log('++-[ params ]: %s' % arg[6:], xbmc.LOGERROR)


xbmc.log('---> default.py starting', xbmc.LOGERROR)
if __name__ == "__main__":
    Main()
xbmc.log('---> default.py stopped', xbmc.LOGERROR)
