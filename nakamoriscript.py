#!/usr/bin/env python
# -*- coding: utf-8 -*-
import debug
import xbmcgui

import routing
from error_handler import ErrorPriority, try_function, show_messages
from nakamori_utils import kodi_utils
from proxy.python_version_proxy import python_proxy as pyproxy

from nakamori_utils.globalvars import *
import lib.windows.calendar as _calendar
import lib.windows.cohesion as _cohesion
import lib.windows.information as _information
import lib.windows.wizard as _wizard

script = routing.Script(base_url=os.path.split(__file__)[-1])

# TODO Now that we have routing.Script, we can use this


@script.route('/')
def root():
    items = [
        ('Wizard', (wizard, [])),
        ('Calendar', (calendar, ['0', '0'])),
        ('Calendar (Add 14 Days)', (calendar, ['0', '14'])),
        ('Information', (whats_new, [])),
        ('Clear-cache', (clearcache, [])),
        ('Installation Integrity', (cohesion, [])),
        ('Settings', (settings, []))
    ]

    options = []
    for item in items:
        options.append(item[0])

    result = xbmcgui.Dialog().select('Nakamori Script', options)
    if result >= 0:
        action, args = items[result][1]
        action(*args)


@script.route('/calendar/<when>/<page>/')
def calendar(when=0, page=1):
    _calendar.open_calendar(date=when, starting_item=page)


@script.route('/dialog/wizard')
def wizard():
    _wizard.open_wizard()


@script.route('/calendar/clear_cache')
def clearcache():
    _calendar.clear_cache()


@script.route('/dialog/whats_new')
def whats_new():
    # TODO redo the what's new version checking and only display if it's new, thereby replacing the setting
    _information.open_information()


@script.route('/dialog/settings')
@try_function(ErrorPriority.BLOCKING)
def settings():
    plugin_addon.openSettings()


@script.route('/cohesion')
def cohesion():
    _cohesion.check_cohesion()


@script.route('/dialog/vote_series/<series_id>')
@try_function(ErrorPriority.BLOCKING)
def show_series_vote_dialog(series_id):
    pass


@script.route('/dialog/vote_episode/<ep_id>')
@try_function(ErrorPriority.BLOCKING)
def show_episode_vote_dialog(ep_id):
    pass


@script.route('/series/<series_id>/vote')
@try_function(ErrorPriority.BLOCKING)
def vote_for_series(series_id):
    from shoko_models.v2 import Series
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    my_vote = xbmcgui.Dialog().select(plugin_addon.getLocalizedString(30023), vote_list)
    if my_vote < 1:
        return
    my_vote = pyproxy.safe_int(vote_list[my_vote])
    if my_vote < 1:
        return
    series = Series(series_id)
    series.vote(my_vote)


@script.route('/episode/<ep_id>/vote')
@try_function(ErrorPriority.BLOCKING)
def vote_for_episode(ep_id):
    from shoko_models.v2 import Episode
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    my_vote = xbmcgui.Dialog().select(plugin_addon.getLocalizedString(30023), vote_list)
    if my_vote < 1:
        return
    my_vote = pyproxy.safe_int(vote_list[my_vote])
    if my_vote < 1:
        return
    ep = Episode(ep_id)
    ep.vote(my_vote)


@script.route('/file/<file_id>/rescan')
@try_function(ErrorPriority.BLOCKING)
def rescan_file(file_id):
    from shoko_models.v2 import File
    f = File(file_id)
    f.rescan()


@script.route('/file/<file_id>/rehash')
@try_function(ErrorPriority.BLOCKING)
def rehash_file(file_id):
    from shoko_models.v2 import File
    f = File(file_id)
    f.rehash()


@script.route('/episode/<ep_id>/set_watched/<watched>')
@try_function(ErrorPriority.HIGH, 'Error Setting Watched Status')
def set_episode_watched_status(ep_id, watched):
    from shoko_models.v2 import Episode
    ep = Episode(ep_id)
    ep.set_watched_status(watched)
    kodi_utils.refresh()


@script.route('/series/<series_id>/set_watched/<watched>')
@try_function(ErrorPriority.HIGH, 'Error Setting Watched Status')
def set_series_watched_status(series_id, watched):
    from shoko_models.v2 import Series
    series = Series(series_id)
    series.set_watched_status(watched)
    kodi_utils.refresh()


@script.route('/group/<group_id>/set_watched/<watched>')
def set_group_watched_status(group_id, watched):
    from shoko_models.v2 import Group
    group = Group(group_id)
    group.set_watched_status(watched)
    kodi_utils.refresh()


if __name__ == '__main__':
    debug.debug_init()
    try_function(ErrorPriority.BLOCKING)(script.run)()
    show_messages()
