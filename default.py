import sys

import lib.windows.calendar as calendar
import lib.windows.information as information
import lib.windows.wizard as wizard
import lib.nakamoritools as nt

from xbmcaddon import Addon
from xbmcgui import Dialog


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
                elif self.params['info'] == 'information':
                    information.open_information()
                elif self.params['info'] == 'settings':
                    Addon(id='script.module.nakamori').openSettings()
        else:
            Dialog().ok('Nakamori script', 'Baka!')


if __name__ == "__main__":
    Main()
