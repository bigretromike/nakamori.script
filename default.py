import sys

import lib.windows.calendar as _calendar
import lib.windows.cohesion as _cohesion
import lib.windows.information as _information
import lib.windows.wizard as _wizard
from proxy.python_version_proxy import python_proxy as pyproxy

import xbmc
import xbmcgui
from xbmcaddon import Addon

_addon = Addon(id='script.module.nakamori')


def main():
    if len(sys.argv) > 1:
        params = pyproxy.parse_parameters(sys.argv[1])
        if not params:
            return
        if params['info'] == 'calendar':
            # TODO please confirm this, because we didn't need it before. https://github.com/xbmc/xbmc/issues/15565
            xbmc.sleep(1000)  # TODO HACK: kodi18 fix for not showing calendar at all from nakamori menu
            _calendar.open_calendar(date=params.get('date', 0), starting_item=params.get('page', 0))
        elif params['info'] == 'wizard':
            _wizard.open_wizard()
        elif params['info'] == 'clearcache':
            _calendar.clear_cache()
        elif params['info'] == 'information':
            _information.open_information()
        elif params['info'] == 'settings':
            _addon.openSettings()
        elif params['info'] == 'cohesion':
            _cohesion.check_cohesion()
        else:
            root()
    else:
        root()
            

def root():
    items = [
        ("Wizard", (wizard, [])),
        ("Calendar", (calendar, ['0', '0'])),
        ("Calendar (Add 14 Days)", (calendar, ['0', '14'])),
        ("Information", (information, [])),
        ("Clear-cache", (clearcache, [])),
        ("Installation Integrity", (cohesion, [])),
        ("Settings", (settings, []))
    ]

    options = []
    for item in items:
        options.append(item[0])

    result = xbmcgui.Dialog().select('Nakamori Script', options)
    if result >= 0:
        action, args = items[result][1]
        action(*args)


def calendar(when, page):
    _calendar.open_calendar(date=when, starting_item=page)


def wizard():
    _wizard.open_wizard()


def clearcache():
    _calendar.clear_cache()


def information():
    _information.open_information()


def settings():
    _addon.openSettings()


def cohesion():
    _cohesion.check_cohesion()


if __name__ == "__main__":
    main()
