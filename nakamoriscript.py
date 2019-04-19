#!/usr/bin/env python
# -*- coding: utf-8 -*-
import debug
import nakamori_player
import search
import xbmcgui

import routing
from error_handler import spam, ErrorPriority, try_function, show_messages
from nakamori_utils import kodi_utils, shoko_utils
from proxy.python_version_proxy import python_proxy as pyproxy

from nakamori_utils.globalvars import *
import lib.windows.calendar as _calendar
import lib.windows.cohesion as _cohesion
import lib.windows.information as _information
import lib.windows.wizard as _wizard

script = routing.Script(base_url=os.path.split(__file__)[-1], convert_args=True)

# TODO Now that we have routing.Script, we can use this
# TODO Localize the menus


@script.route('/')
def root():
    items = [
        ('Connection Wizard', (wizard_connection, [])),
        ('Login Wizard', (wizard_login, [])),
        ('Calendar', (calendar, ['0', '0'])),
        ('Calendar (Add 14 Days)', (calendar, ['0', '14'])),
        ('Calendar 3rd party', (calendar_3rd, ['0', '0'])),
        ('Information', (whats_new, [])),
        ('Clear-cache', (clearcache, [])),
        ('Installation Integrity', (cohesion, [])),
        ('Settings', (settings, []))
    ]

    options = []
    for item in items:
        options.append(item[0])

    result = xbmcgui.Dialog().contextmenu(options)
    if result >= 0:
        action, args = items[result][1]
        action(*args)


@script.route('/calendar/<when>/<page>')
def calendar(when=0, page=1):
    _calendar.open_calendar(date=when, starting_item=page)


@script.route('/calendar3/<when>/<page>')
def calendar_3rd(when=0, page=1):
    from lib.external_calendar import *
    when3 = return_only_few(when)
    _calendar.open_calendar(date=when3, starting_item=page)


@script.route('/arbiter/<wait>/<path:arg>')
@try_function(ErrorPriority.BLOCKING)
def arbiter(wait, arg):
    spam('arbiting', 'wait:', wait, 'arg:', arg)
    if wait is None or arg is None:
        raise RuntimeError('Arbiter received no parameters')
    xbmc.sleep(wait)
    xbmc.executebuiltin(arg)


@script.route('/dialog/wizard/connection')
def wizard_connection():
    _wizard.open_connection_wizard()


@script.route('/dialog/wizard/login')
def wizard_login():
    _wizard.open_login_wizard()


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


@script.route('/dialog/shoko')
@try_function(ErrorPriority.BLOCKING)
def shoko_menu():
    # TODO add things
    # Remove Missing
    # Run Import
    # Import Folders?
    # various other actions
    items = [
        ('Run Import', (shoko_utils.run_import, [])),
        ('Remove Missing Files', (shoko_utils.remove_missing_files, []))
    ]

    options = []
    for item in items:
        options.append(item[0])

    result = xbmcgui.Dialog().contextmenu(options)
    if result >= 0:
        action, args = items[result][1]
        action(*args)


@script.route('/dialog/search/<save>')
def new_search(save):
    query = kodi_utils.search_box()

    if save:
        if search.check_in_database(query):
            search.remove_search_history(query)
        search.add_search_history(query)

    # Apparently this is the only way that works if we want to RunPlugin with a path
    arbiter(0, 'ActivateWindow(10025, "plugin://plugin.video.nakamori/menu/search/%s")' %
            pyproxy.quote(pyproxy.quote(query)))


@script.route('/search/remove/<path:query>')
def remove_search_term(query):
    search.remove_search_history(query)
    refresh()


@script.route('/search/clear')
def clear_search():
    search.remove_search_history()
    refresh()


@script.route('/kodi/clear_image_cache')
def clear_image_cache():
    kodi_utils.clear_image_cache()


@script.route('/kodi/clear_listitem_cache')
def clear_listitem_cache():
    kodi_utils.clear_listitem_cache()


@script.route('/refresh')
def refresh():
    kodi_utils.refresh()


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


@script.route('/tvshows/<vote_type>/vote')
@try_function(ErrorPriority.BLOCKING)
def vote_for_tvshows(vote_type):
    from kodi_models import VideoLibraryItem
    vl_item = VideoLibraryItem()
    vl_item.vote(vote_type)


@script.route('/ep/<ep_id>/file_list')
@try_function(ErrorPriority.BLOCKING)
def file_list(ep_id):
    from shoko_models.v2 import Episode
    ep = Episode(ep_id, build_full_object=True)
    items = [(x.name, x.id) for x in ep]
    selected_id = kodi_utils.show_file_list(items)
    nakamori_player.play_video(selected_id, ep_id)


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
    if plugin_addon.getSetting('sync_to_library') is 'true':
        playcount = '1' if watched else '0'
        # lastplayed = 'string'
        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"playcount": ' + playcount + ' , "episodeid": ' + episode_id + '}, "id": 1 }')
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


@script.route('/menu/episode/move_to_item/<index>')
def move_to_index(index):
    kodi_utils.move_to_index(index)


if __name__ == '__main__':
    debug.debug_init()
    try_function(ErrorPriority.BLOCKING)(script.run)()
    show_messages()
