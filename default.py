import sys
import xbmc
import xbmcaddon
import lib.windows.calendar as calendar
import lib.windows.wizard as wizard


class Main:
    def __init__(self):
        self._parse_argv()

        if not self.infos:
            pass
        else:
            if 'calendar' in self.infos:
                calendar.open_calendar()
            elif 'wizard' in self.infos:
                wizard.open_wizard()

    def _parse_argv(self):
        self.infos = []
        self.params = {"handle": None}
        for arg in sys.argv:
            if arg.startswith('?info='):
                self.infos.append(arg[6:])


if __name__ == "__main__":
    Main()
