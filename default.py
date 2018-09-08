import sys

import lib.windows.calendar as calendar
import lib.windows.wizard as wizard
import lib.nakamoritools as nt

import xbmc
import xbmcaddon


class Main:
    def __init__(self):
        if len(sys.argv) > 1:
            self.params = nt.parse_parameters(sys.argv[1])
            if not self.params:
                pass
            else:
                if self.params['info'] == 'calendar':
                    calendar.open_calendar(date=self.params.get('date', 0), starting_item=self.params.get('page', 0))
                elif self.params['info'] == 'wizard':
                    wizard.open_wizard()
                elif self.params['info'] == 'clearcache':
                    calendar.clear_cache()
                elif self.params['info'] == 'settings':
                    xbmcaddon.Addon(id='script.module.nakamori').openSettings()


if __name__ == "__main__":
    xbmc.log('--- default.py : start', xbmc.LOGWARNING)
    Main()
    xbmc.log('--- default.py : stop', xbmc.LOGWARNING)
