#!/usr/bin/env python
# -*- coding: utf-8 -*-
import debug
import json
import nakamori_player
import search
import favorite
import xbmcgui
import xbmc

import routing
from error_handler import spam, ErrorPriority, try_function, show_messages
from nakamori_utils import kodi_utils, shoko_utils, eigakan_utils
from proxy.python_version_proxy import python_proxy as pyproxy
from proxy.python_version_proxy import http_error as http_error

from nakamori_utils.globalvars import *
import lib.windows.calendar as _calendar
import lib.windows.ac_calendar as _ac_calendar
import lib.windows.cohesion as _cohesion
import lib.windows.information as _information
import lib.windows.wizard as _wizard
import lib.windows.series_info as _series_info

script = routing.Script(base_url=os.path.split(__file__)[-1], convert_args=True)
clientid = kodi_utils.get_device_id()

@script.route('/')
def root():
    items = [
        (script_addon.getLocalizedString(30025), (wizard_connection, [])),
        (script_addon.getLocalizedString(30043), (wizard_login, [])),
        (script_addon.getLocalizedString(30028), (calendar, ['0', '0'])),
        (script_addon.getLocalizedString(30044), (calendar, ['0', '14'])),
        (script_addon.getLocalizedString(30028), (cr_calendar, ['0', '0', False])),
        (script_addon.getLocalizedString(30045), (cr_calendar, ['0', '0', True])),
        (script_addon.getLocalizedString(30028), (ac_calendar, ['0', '0', False])),
        (script_addon.getLocalizedString(30045), (ac_calendar, ['0', '0', True])),
        (script_addon.getLocalizedString(30046), (whats_new, [])),
        (script_addon.getLocalizedString(30033), (clearcache, [])),
        (script_addon.getLocalizedString(30047), (cohesion, [])),
        (script_addon.getLocalizedString(30048), (settings, [])),
        ('detect eigakan', (eigakan_detect, []))
    ]

    options = []
    for item in items:
        options.append(item[0])

    result = xbmcgui.Dialog().contextmenu(options)
    if result >= 0:
        action, args = items[result][1]
        action(*args)


@script.route('/seriesinfo/aid/<aid>/')
def series_info(aid=0):
    _series_info.open_seriesinfo(aid=aid)


@script.route('/seriesinfo/<aid>/')
def series_info(id=0):
    _series_info.open_seriesinfo(id=id)


@script.route('/calendar/<when>/<page>/')
def calendar(when=0, page=1, force_external=False):
    if script_addon.getSetting('calendar_mode') == 'crunchyroll':
        cr_calendar(when, page, force_external)
    else:
        ac_calendar(when, page, force_external)


@script.route('/cr_calendar/<when>/<page>/')
def cr_calendar(when=0, page=0, force_external=False):
    if script_addon.getSetting('custom_source') == 'true' or force_external:
        if when == '0' and page == '0':
            import datetime
            when = datetime.datetime.now().strftime('%Y%m%d')
        from lib.external_calendar import return_only_few
        body = return_only_few(when=when, offset=page, url=str(script_addon.getSetting('custom_url')))
        _calendar.open_calendar(date=when, starting_item=page, json_respons=body)
    else:
        _calendar.open_calendar(date=when, starting_item=page)


@script.route('/ac_calendar/<when>/<page>/')
def ac_calendar(when=0, page=1, force_external=False):
    if script_addon.getSetting('custom_source') == 'true' or force_external:
        if when == '0' and page == '0':
            import datetime
            when = datetime.datetime.now().strftime('%Y%m%d')
        from lib.external_calendar import return_only_few
        body = return_only_few(when=when, offset=page, url=str(script_addon.getSetting('custom_url')))
        _ac_calendar.open_calendar(date=when, starting_item=page, json_respons=body)
    else:
        _ac_calendar.open_calendar(date=when, starting_item=page)


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


@script.route('/dialog/script_settings')
@try_function(ErrorPriority.BLOCKING)
def settings():
    script_addon.openSettings()


@script.route('/dialog/shoko')
@try_function(ErrorPriority.BLOCKING)
def shoko_menu():
    # TODO add things
    # Remove Missing
    # Import Folders?
    # various other actions
    items = [
        (script_addon.getLocalizedString(30049), (shoko_utils.run_import, [])),
        (script_addon.getLocalizedString(30042), (shoko_utils.remove_missing_files, []))
    ]

    options = []
    for item in items:
        options.append(item[0])

    result = xbmcgui.Dialog().contextmenu(options)
    if result >= 0:
        action, args = items[result][1]
        action(*args)


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


@script.route('/dialog/vote_series/<series_id>/')
@try_function(ErrorPriority.BLOCKING)
def show_series_vote_dialog(series_id):
    # TODO something ?
    pass


@script.route('/dialog/vote_episode/<ep_id>/')
@try_function(ErrorPriority.BLOCKING)
def show_episode_vote_dialog(ep_id):
    # TODO something ?
    pass


@script.route('/series/<series_id>/vote')
@try_function(ErrorPriority.BLOCKING)
def vote_for_series(series_id):
    from shoko_models.v2 import Series
    series = Series(series_id)
    suggest_rating = ''
    if plugin_addon.getSetting('suggest_series_vote') == 'true':
        if plugin_addon.getSetting('suggest_series_vote_all_eps') == 'true':
            if not series.did_you_rate_every_episode:
                xbmcgui.Dialog().ok(script_addon.getLocalizedString(30053))
                return
        suggest_rating = ' [ %s ]' % series.suggest_rating_based_on_episode_rating

    vote_list = ['Don\'t Vote' + suggest_rating, '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    my_vote = xbmcgui.Dialog().select(plugin_addon.getLocalizedString(30023), vote_list)
    if my_vote < 1:
        return
    my_vote = pyproxy.safe_int(vote_list[my_vote])
    if my_vote < 1:
        return
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


@script.route('/file/<file_id>/probe')
def probe_file(file_id, second_try=True):
    from shoko_models.v2 import File
    f = File(file_id, build_full_object=True)
    content = '"file":"%s","remote":"%s"' % (f.url_for_player, f.remote_url_for_player )
    url = 'http://%s:%s/api/probe/%s/%s' % (plugin_addon.getSetting('ipEigakan'), plugin_addon.getSetting('portEigakan'), clientid, file_id)

    if kodi_utils.check_eigakan():
        busy = xbmcgui.DialogProgress()
        busy.create(plugin_addon.getLocalizedString(30160), plugin_addon.getLocalizedString(30177))
        data = ''
        try:
            data = pyproxy.post_json(url, content)
            busy.close()
            xbmcgui.Dialog().ok(plugin_addon.getLocalizedString(30207), '%s' % data)
        except http_error as err:
            busy.close()
            if err.code == 503:
                kodi_utils.send_profile()
                if not second_try:
                    probe_file(file_id, second_try=True)
        except:
            busy.close()
    else:
        # TODO lang fix
        xbmcgui.Dialog().ok('Try later', 'Eigakan is offline')


@script.route('/episode/<file_id>/probe')
@try_function(ErrorPriority.BLOCKING)
def probe_episode(ep_id):
    from shoko_models.v2 import Episode
    ep = Episode(ep_id, build_full_object=True)
    items = [(x.name, x.id) for x in ep]
    selected_id = kodi_utils.show_file_list(items)
    file_id = self.get_file_with_id(selected_id)
    if file_id > 0:
        probe_file(file_id)


@script.route('/file/<file_id>/transcode')
@try_function(ErrorPriority.BLOCKING)
def transcode_file(file_id):
    from shoko_models.v2 import File
    f = File(file_id, build_full_object=True)
    content = '"file":"%s","remote":"%s"' % (f.url_for_player, f.remote_url_for_player)
    audio_stream, subs_streams = eigakan_utils.probe_file(file_id, f.remote_url_for_player)
    a_index, s_index, sub_type = eigakan_utils.pick_best_streams(audio_stream, subs_streams)
    if int(a_index) > -1:
        content += ',"audio":"%s"' % a_index
    if int(s_index) > -1:
        content += ',"subtitles":"%s"' % s_index
    url = 'http://%s:%s/api/transcode/%s/%s' % (plugin_addon.getSetting('ipEigakan'), plugin_addon.getSetting('portEigakan'), clientid, file_id)

    busy = xbmcgui.DialogProgress()
    busy.create(plugin_addon.getLocalizedString(30160), plugin_addon.getLocalizedString(30177))
    try:
        pyproxy.post_json(url, content, custom_timeout=0.1)
        try_count = 5
        xbmc.sleep(1000)
        while True:
            if busy.iscanceled():
                break
            if eigakan_utils.is_fileid_added_to_transcoder(file_id):
                break
            try_count += 1
            busy.update(try_count)
            xbmc.sleep(1000)
    finally:
        busy.close()


@script.route('/episode/<file_id>/transcode')
@try_function(ErrorPriority.BLOCKING)
def transcode_episode(ep_id):
    from shoko_models.v2 import Episode
    ep = Episode(ep_id, build_full_object=True)
    items = [(x.name, x.id) for x in ep]
    selected_id = kodi_utils.show_file_list(items)
    file_id = self.get_file_with_id(selected_id)
    if file_id > 0:
        transcode_file(file_id)


@script.route('/episode/<ep_id>/set_watched/<watched>')
@try_function(ErrorPriority.HIGH, 'Error Setting Watched Status')
def set_episode_watched_status(ep_id, watched, do_refresh=True):
    from shoko_models.v2 import Episode
    ep = Episode(ep_id)
    ep.set_watched_status(watched)
    if plugin_addon.getSetting('sync_to_library') == 'true':
        playcount = '1' if watched else '0'
        # lastplayed = 'string'
        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"playcount": ' + playcount + ' , "episodeid": ' + ep_id + '}, "id": 1 }')
    if do_refresh:
        kodi_utils.refresh()


@script.route('/series/<series_id>/set_watched/<watched>')
@try_function(ErrorPriority.HIGH, 'Error Setting Watched Status')
def set_series_watched_status(series_id, watched, do_refresh=True):
    from shoko_models.v2 import Series
    series = Series(series_id)
    series.set_watched_status(watched)
    if do_refresh:
        kodi_utils.refresh()


@script.route('/group/<group_id>/set_watched/<watched>')
def set_group_watched_status(group_id, watched):
    from shoko_models.v2 import Group
    group = Group(group_id)
    group.set_watched_status(watched)
    kodi_utils.refresh()


@script.route('/menu/episode/move_to_item/<index>/')
def move_to_index(index):
    kodi_utils.move_to_index(index)


@script.route('/eigakan/clear')
def clear_eigakan_remote_profile():
    plugin_addon.setSetting('eigakan_handshake', 'false')
    kodi_utils.send_profile()


@script.route('/eigakan/requirement')
def eigakan_requirements():
    try:
        # if the addon if disabled (but installed) this will also raise error
        import xbmcaddon
        xbmcaddon.Addon('inputstream.adaptive').openSettings()
    except Exception as ex:
        # in this point we dont know if its installed but disabled or not installed
        if not kodi_utils.is_addon_enabled():
            if not kodi_utils.is_addon_installed():
                if xbmcgui.Dialog().yesno('inputstream.adaptive', plugin_addon.getLocalizedString(30210)):
                    xbmc.executebuiltin('InstallAddon(inputstream.adaptive)')
                else:
                    xbmcgui.Dialog().ok('inputstream.adaptive', plugin_addon.getLocalizedString(30208))
            else:
                if xbmcgui.Dialog().yesno('inputstream.adaptive', plugin_addon.getLocalizedString(30209)):
                    kodi_utils.enable_addon()


@script.route('/eigakan/detect')
def eigakan_detect():
    import socket
    import struct

    # TODO LANG FIX
    if xbmcgui.Dialog().yesno('Detect', 'Eigakan?'):
        try:
            MCAST_GRP = '224.1.1.1'
            MCAST_PORT = 5007
            IS_ALL_GROUPS = True

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if IS_ALL_GROUPS:
                # on this port, receives ALL multicast groups
                sock.bind(('', MCAST_PORT))
            else:
                # on this port, listen ONLY to MCAST_GRP
                sock.bind((MCAST_GRP, MCAST_PORT))
            mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            while True:
                x, y = sock.recvfrom(10240)
                if x.startswith('eigakanserver'):
                    port = x.split('|')[1]
                    version = x.split('|')[2]
                    address, _port = y
                    # TODO LANG FIX
                    if xbmcgui.Dialog().yesno('Setup Eigakan as:', 'ip: %s port: %s' % (address, port), 'version: %s' % version):
                        plugin_addon.setSetting('ipEigakan', str(address))
                        plugin_addon.setSetting('portEigakan', str(port))
                        break
                    else:
                        # TODO LANG FIX
                        if xbmcgui.Dialog().yesno('Do you want to stop?', 'Stop scanning?'):
                            break

        except Exception as ex:
            xbmc.log('E -------- %s --------' % ex, xbmc.LOGNOTICE)


@script.route('/favorite/<sid>/add')
def favorite_add(sid):
    favorite.add_favorite(sid)

@script.route('/favorite/<sid>/remove')
def favorite_remove(sid):
    favorite.remove_favorite(sid)
    refresh()

@script.route('/favorite/clear')
def favorite_clear():
    favorite.clear_favorite()
    refresh()


if __name__ == '__main__':
    debug.debug_init()
    try_function(ErrorPriority.BLOCKING)(script.run)()
    show_messages()
