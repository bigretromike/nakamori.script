import sys
import xbmc
import xbmcaddon
import lib.windows.calendar as calendar
import lib.windows.wizard as wizard


class Main:
    def __init__(self):
        self._parse_argv()

        if not self.infos:
            xbmc.log('---> default.py infos=None', xbmc.LOGERROR)
        else:
            xbmc.log('---> default.py infos=calendar START', xbmc.LOGERROR)
            if 'calendar' in self.infos:
                calendar.open_calendar()
            elif 'wizard' in self.infos:
                wizard.open_wizard()

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
