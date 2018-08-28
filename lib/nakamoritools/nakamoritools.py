#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import sys
import traceback
import os
import json
import time
import gzip
import collections
import re

from distutils.version import LooseVersion

if sys.version_info < (3, 0):
    from urllib2 import urlopen
    from urllib import quote, quote_plus, unquote, unquote_plus, urlencode
    from urllib2 import Request
    from urllib2 import HTTPError, URLError
    from StringIO import StringIO
else:
    # For Python 3.0 and later
    # noinspection PyUnresolvedReferences
    from urllib.request import urlopen
    # noinspection PyUnresolvedReferences
    from urllib.parse import quote, quote_plus, unquote, unquote_plus, urlencode
    # noinspection PyUnresolvedReferences
    from urllib.request import Request
    # noinspection PyUnresolvedReferences
    from urllib.error import HTTPError, URLError
    from io import StringIO, BytesIO


# __ is public, _ is protected
global addon
global addonversion
global addonid
global addonname
global icon
global localize
global server
global home
global python_two

# noinspection PyRedeclaration
addon = xbmcaddon.Addon('plugin.video.nakamori')
# noinspection PyRedeclaration
addonversion = addon.getAddonInfo('version')
# noinspection PyRedeclaration
addonid = addon.getAddonInfo('id')
# noinspection PyRedeclaration
addonname = addon.getAddonInfo('name')
# noinspection PyRedeclaration
icon = addon.getAddonInfo('icon')
# noinspection PyRedeclaration
localize = addon.getLocalizedString
# noinspection PyRedeclaration
server = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port")
# noinspection PyRedeclaration
python_two = sys.version_info < (3, 0)

try:
    # kodi 17+
    UA = xbmc.getUserAgent()
except:
    # kodi < 17
    UA = 'Mozilla/6.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.5) Gecko/2008092417 Firefox/3.0.3'
pDialog = ''


def search_box():
    """
    Shows a keyboard, and returns the text entered
    :return: the text that was entered
    """
    keyb = xbmc.Keyboard('', 'Enter search text')
    keyb.doModal()
    search_text = ''

    if keyb.isConfirmed():
        search_text = keyb.getText()
    return search_text


def get_kodi_setting_bool(setting):
    try:
        parent_setting = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params":' +
            '{"setting": "' + setting + '"}, "id": 1}')
        # {"id":1,"jsonrpc":"2.0","result":{"value":false}} or true if ".." is displayed on list

        result = json.loads(parent_setting)
        if "result" in result:
            if "value" in result["result"]:
                return result["result"]["value"]
    except Exception as exc:
        error("jsonrpc_error: " + str(exc))
    return False


def get_kodi_setting_int(setting):
    try:
        parent_setting = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params":' +
            '{"setting": "' + setting + '"}, "id": 1}')
        # {"id":1,"jsonrpc":"2.0","result":{"value":false}} or true if ".." is displayed on list

        result = json.loads(parent_setting)
        if "result" in result:
            if "value" in result["result"]:
                return int(result["result"]["value"])
    except Exception as exc:
        error("jsonrpc_error: " + str(exc))
    return -1


def move_position_on_list(control_list, position=0, force=False):
    """
    Move to the position in a list - use episode number for position
    Args:
        control_list: the list control
        position: the index of the item not including settings
        force: bypass setting and set position directly
    """
    if not force:
        if position < 0:
            position = 0
        if addon.getSetting('show_continue') == 'true':
            position = int(position + 1)

        if get_kodi_setting_bool("filelists.showparentdiritems"):
            position = int(position + 1)

    try:
        control_list.selectItem(position)
    except:
        try:
            control_list.selectItem(position - 1)
        except Exception as e:
            error('Unable to reselect item', str(e))
            xbmc.log('control_list: ' + str(control_list.getId()), xbmc.LOGWARNING)
            xbmc.log('position: ' + str(position), xbmc.LOGWARNING)


def remove_anidb_links(data=""):
    """
    Remove anidb links from descriptions
    Args:
        data: the strong to remove links from

    Returns: new string without links

    """
    # search for string with 1 to 3 letters and 1 to 7 numbers
    p = re.compile('http://anidb.net/[a-z]{1,3}[0-9]{1,7}[ ]')
    data2 = p.sub('', data)
    # remove '[' and ']' that included link to anidb.net
    # was ('(\[|\])')
    p = re.compile('[\[\]]')
    return p.sub('', data2)


def safe_int(object_body):
    """
    safe convert type to int to avoid NoneType
    :param object_body:
    :return: int
    """
    try:
        if object_body is not None and object_body != '':
            return int(object_body)
        else:
            return 0
    except:
        return 0


def trakt_scrobble(ep_id, status, progress, movie, notification):
    note_text = ''
    if status == 1:
        # start
        progress = 0
        note_text = 'Starting Scrobble'
    elif status == 2:
        # pause
        note_text = 'Paused Scrobble'
    elif status == 3:
        # finish
        progress = 100
        note_text = 'Stopping Scrobble'

    if notification:
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % ('Trakt.tv', note_text, '',
                                                                        addon.getAddonInfo('icon')))

    get_json(server + "/api/ep/scrobble?id=" + str(ep_id) + "&ismovie=" + str(movie) +
             "&status=" + str(status) + "&progress=" + str(progress))


def sync_offset(file_id, current_time):
    """
    sync offset of played file
    :param file_id: id
    :param current_time: current time in seconds
    """

    offset_url = server + "/api/file/offset"
    offset_body = '"id":' + str(file_id) + ',"offset":' + str(current_time * 1000)
    try:
        post_json(offset_url, offset_body)
    except:
        error('error Scrobbling', '', True)


def mark_watch_status(params):
    """
    Marks an episode, series, or group as either watched (offset = 0) or unwatched
    :params: must contain either an episode, series, or group id, and a watched value to mark
    """
    episode_id = params.get('ep_id', '')
    anime_id = params.get('serie_id', '')
    group_id = params.get('group_id', '')
    file_id = params.get('file_id', 0)
    watched = bool(params['watched'])
    key = server + "/api"

    if watched is True:
        watched_msg = "watched"
        if episode_id != '':
            key += "/ep/watch"
        elif anime_id != '':
            key += "/serie/watch"
        elif group_id != '':
            key += "/group/watch"
    else:
        watched_msg = "unwatched"
        if episode_id != '':
            key += "/ep/unwatch"
        elif anime_id != '':
            key += "/serie/unwatch"
        elif group_id != '':
            key += "/group/unwatch"

    if file_id != 0:
        sync_offset(file_id, 0)

    if addon.getSetting('log_spam') == 'true':
        xbmc.log('file_d: ' + str(file_id), xbmc.LOGWARNING)
        xbmc.log('epid: ' + str(episode_id), xbmc.LOGWARNING)
        xbmc.log('anime_id: ' + str(anime_id), xbmc.LOGWARNING)
        xbmc.log('group_id: ' + str(group_id), xbmc.LOGWARNING)
        xbmc.log('key: ' + key, xbmc.LOGWARNING)

    # sync mark flags
    sync = addon.getSetting("syncwatched")
    if sync == "true":
        if episode_id != '':
            body = '?id=' + episode_id
            get_json(key + body)
        elif anime_id != '':
            body = '?id=' + anime_id
            get_json(key + body)
        elif group_id != '':
            body = '?id=' + group_id
            get_json(key + body)
    else:
        xbmc.executebuiltin('XBMC.Action(ToggleWatched)')

    box = addon.getSetting("watchedbox")
    if box == "true":
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 2000, %s)" % (addon.getLocalizedString(30187),
                                                                        addon.getLocalizedString(30188),
                                                                        watched_msg,
                                                                        addon.getAddonInfo('icon')))
    refresh()


def refresh():
    """
    Refresh and re-request data from server
    refresh watch status as we now mark episode and refresh list so it show real status not kodi_cached
    Allow time for the ui to reload
    """
    xbmc.executebuiltin('Container.Refresh')
    xbmc.sleep(int(addon.getSetting('refresh_wait')))


def set_sort_method(int_of_sort_method=0):
    """
    Ser given sort method
    :param int_of_sort_method: int parameter of sort method
    :return: set sort method
    """
    # xbmc.log('-> trying to set \'%s\' sorting' % int_of_sort_method, xbmc.LOGWARNING)
    xbmc.executebuiltin('Container.SetSortMethod(' + str(int_of_sort_method) + ')')


def set_user_sort_method(place):
    """
    Set user define type of sort method.
    For more check:
    https://codedocs.xyz/AlwinEsch/kodi/group___list__of__sort__methods.html
    https://github.com/xbmc/xbmc/blob/master/xbmc/utils/SortUtils.cpp#L529-L577
    """
    sort_method = {
        'Server': 0,
        'Title': 7,
        'Episode': 23,
        'Date': 2,
        'Rating': 17
    }

    place_setting = {
        'filter': addon.getSetting("default_sort_filter"),
        'group': addon.getSetting("default_sort_group_series"),
        'episode': addon.getSetting("default_sort_episodes")
    }

    user_sort_method = place_setting.get(place, 'Server')
    method_for_sorting = sort_method.get(user_sort_method, 0)
    set_sort_method(method_for_sorting)


def vote_series(series_id):
    """
    Marks a rating for a series
    Args:
        series_id: serie id

    """
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    my_vote = xbmcgui.Dialog().select(addon.getLocalizedString(30184), vote_list)
    if my_vote == -1:
        return
    elif my_vote != 0:
        vote_value = str(vote_list[my_vote])
        body = '?id=' + series_id + '&score=' + vote_value
        get_json(server + "/api/serie/vote" + body)
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (addon.getLocalizedString(30184),
                                                                        addon.getLocalizedString(30185),
                                                                        vote_value, addon.getAddonInfo('icon')))


def vote_episode(ep_id):
    """
    Marks a rating for an episode
    Args:
        ep_id: episode id

    """
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    my_vote = xbmcgui.Dialog().select(addon.getLocalizedString(30186), vote_list)
    if my_vote == -1:
        return
    elif my_vote != 0:
        vote_value = str(vote_list[my_vote])
        body = '?id=' + ep_id + '&score=' + vote_value
        get_json(server + "/api/ep/vote" + body)
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (addon.getLocalizedString(30186),
                                                                        addon.getLocalizedString(30185),
                                                                        vote_value, addon.getAddonInfo('icon')))


def get_data(url_in, referer, data_type):
    """
    Send a message to the server and wait for a response
    Args:
        url_in: the URL to get data from
        referer: currently not used always should be None
        data_type: extension for url (.json or .xml) to force return type

    Returns: The response from the server in forced type (.json or .xml)
    """
    try:
        if data_type != "json":
            data_type = "xml"

        url = url_in

        req = Request(encode(url))
        req.add_header('Accept', 'application/' + data_type)
        req.add_header('apikey', addon.getSetting("apikey"))

        if referer is not None:
            referer = quote(encode(referer)).replace("%3A", ":")
            if len(referer) > 1:
                req.add_header('Referer', referer)
        use_gzip = addon.getSetting("use_gzip")
        if "127.0.0.1" not in url and "localhost" not in url:
            if use_gzip == "true":
                req.add_header('Accept-encoding', 'gzip')
        data = None
        try:
            response = urlopen(req, timeout=int(addon.getSetting('timeout')))
            if response.info().get('Content-Encoding') == 'gzip':
                try:
                    if python_two:
                        buf = StringIO(response.read())
                    else:
                        buf = BytesIO(response.read())
                    f = gzip.GzipFile(fileobj=buf)
                    data = f.read()
                except Exception as ex:
                    error('Decompresing gzip respond failed: ' + str(ex))
            else:
                data = response.read()
            response.close()
        except URLError as url_error:
            xbmc.log('Error in urlopen: %s' % url_error, xbmc.LOGERROR)
            # error('Connection Failed', str(url_error))
            data = None
        except Exception as ex:
            xbmc.log("url: " + str(url) + " error: " + ex.message, xbmc.LOGERROR)
            error('Connection Failed', str(ex))
            data = None
    except Exception as ex:
        error('Get_Data Error', str(ex))
        data = None

    if data is not None and data != '':
        parse_possible_error(data, data_type)
    return data


def parse_possible_error(data, data_type):
    if data_type == 'json':
        stream = json.loads(data)
        if "StatusCode" in stream:
            code = stream.get('StatusCode')
            if code != '200':
                error_msg = code
                if code == '500':
                    error_msg = 'Server Error'
                elif code == '404':
                    error_msg = 'Invalid URL: Endpoint not Found in Server'
                elif code == '503':
                    error_msg = 'Service Unavailable: Check netsh http'
                elif code == '401' or code == '403':
                    error_msg = 'The was refused as unauthorized'
                error(error_msg, error_type='Network Error: ' + code)
                if stream.get('Details', '') != '':
                    xbmc.log(encode(stream.get('Details')), xbmc.LOGERROR)


def get_json(url_in, direct=False):
    """
    use 'get' to return json body as string
    :param url_in:
    :param direct: force to bypass cache
    :return:
    """
    if direct:
        body = get_data(url_in, None, "json")
    else:
        if (addon.getSetting("enableCache") == "true") and ("file?id" not in url_in):
            import Cache as cache  # import only if cache is enabled
            db_row = cache.check_in_database(url_in)
            if db_row is None:
                db_row = 0
            if db_row > 0:
                expire_second = time.time() - float(db_row)
                if expire_second > int(addon.getSetting("expireCache")):
                    # expire, get new date
                    body = get_data(url_in, None, "json")
                    params = {'extras': 'single-delete', 'name': url_in}
                    cache.remove_cache(params)
                    cache.add_cache(url_in, json.dumps(body))
                else:
                    body = cache.get_data_from_cache(url_in)
            else:
                body = get_data(url_in, None, "json")
                cache.add_cache(url_in, json.dumps(body))
        else:
            body = get_data(url_in, None, "json")
    return body


def post_json(url_in, body):
    """
    Push data to server using 'POST' method
    :param url_in:
    :param body:
    :return:
    """
    if len(body) > 3:
        proper_body = '{' + body + '}'
        return post_data(url_in, proper_body)
    else:
        return None


def post_data(url, data_in):
    """
    Send a message to the server and wait for a response
    Args:
        url: the URL to send the data to
        data_in: the message to send (in json)

    Returns: The response from the server
    """
    if data_in is not None:
        req = Request(encode(url), encode(data_in), {'Content-Type': 'application/json'})
        req.add_header('apikey', addon.getSetting("apikey"))
        req.add_header('Accept', 'application/json')
        data_out = None
        try:
            response = urlopen(req, timeout=int(addon.getSetting('timeout')))
            data_out = response.read()
            response.close()
        except Exception as ex:
            error('url:' + str(url))
            error('Connection Failed in post_data', str(ex))
        return data_out
    else:
        error('post_data body is None')
        return None


def error(msg, error_type='Error', silent=False):
    """
    Log and notify the user of an error
    Args:
        msg: the message to print to log and user notification
        error_type: Type of Error
        silent: disable visual notification
    """
    xbmc.log("Nakamori " + str(addonversion) + " id: " + str(addonid), xbmc.LOGERROR)
    xbmc.log('---' + msg + '---', xbmc.LOGERROR)
    key = sys.argv[0]
    if len(sys.argv) > 2 and sys.argv[2] != '':
        key += sys.argv[2]
    xbmc.log('On url: ' + unquote(key), xbmc.LOGERROR)
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        if exc_type is not None and exc_obj is not None and exc_tb is not None:
            xbmc.log(str(exc_type) + " at line " + str(exc_tb.tb_lineno) + " in file " + str(
                os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]), xbmc.LOGERROR)
            traceback.print_exc()
    except Exception as e:
        xbmc.log("There was an error catching the error. WTF.", xbmc.LOGERROR)
        xbmc.log("The error message: " + str(e), xbmc.LOGERROR)
        traceback.print_exc()
    if not silent:
        xbmc.executebuiltin('XBMC.Notification(%s, %s %s, 2000, %s)' % (error_type, ' ', msg,
                                                                        addon.getAddonInfo('icon')))


def encode(i=''):
    """
    encode a string from UTF-8 to bytes or safe string
    Args:
        i: string to encode

    Returns: encoded string

    """

    if python_two:
        try:
            if isinstance(i, str):
                return i
            elif isinstance(i, unicode):
                return i.encode('utf-8')
        except:
            error("Unicode Error", error_type='Unicode Error')
            return ''
    else:
        try:
            if isinstance(i, bytes):
                return i
            elif isinstance(i, str):
                return i.encode('utf-8')
        except:
            error("Unicode Error", error_type='Unicode Error')
            return ''


# noinspection PyRedeclaration
def get_kodi_setting_int(setting):
    try:
        parent_setting = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params":' +
            '{"setting": "' + setting + '"}, "id": 1}')
        # {"id":1,"jsonrpc":"2.0","result":{"value":false}} or true if ".." is displayed on list

        result = json.loads(parent_setting)
        if "result" in result:
            if "value" in result["result"]:
                return int(result["result"]["value"])
    except Exception as exc:
        error("jsonrpc_error: " + str(exc))
    return -1


def decode(i=''):
    """
    decode a string to UTF-8
    Args:
        i: string to decode

    Returns: decoded string

    """
    if python_two:
        try:
            if isinstance(i, str):
                return i.decode("utf-8")
            elif isinstance(i, unicode):
                return i
        except:
            error("Unicode Error", error_type='Unicode Error')
            return ''
    else:
        try:
            if isinstance(i, bytes):
                return i.decode("utf-8")
            elif isinstance(i, str):
                return i
        except:
            error("Unicode Error", error_type='Unicode Error')
            return ''


home = decode(xbmc.translatePath(addon.getAddonInfo('path')))


def valid_user():
    """
    Logs into the server and stores the apikey, then checks if the userid is valid
    :return: bool True if all completes successfully
    """

    if addon.getSetting("apikey") != "" and addon.getSetting("login") == "":
        return (True, addon.getSetting("apikey"))
    else:
        xbmc.log('-- apikey empty --', xbmc.LOGWARNING)
        try:
            if addon.getSetting("login") != "" and addon.getSetting("device") != "":
                _server = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port")
                body = '{"user":"' + addon.getSetting("login") + '",' + \
                       '"device":"' + addon.getSetting("device") + '",' + \
                       '"pass":"' + addon.getSetting("password") + '"}'
                post_body = post_data(_server + "/api/auth", body)
                auth = json.loads(post_body)
                if "apikey" in auth:
                    apikey_found_in_auth = str(auth['apikey'])
                    addon.setSetting(id='login', value='')
                    addon.setSetting(id='password', value='')
                    # xbmcaddon.Addon('plugin.video.nakamori').setSetting(id='login', value='LOGIN')
                    addon.setSetting(id='apikey', value=apikey_found_in_auth)
                    xbmc.log('-- save apikey: %s' % apikey_found_in_auth, xbmc.LOGWARNING)
                    return (True, apikey_found_in_auth)
                else:
                    raise Exception('Error Getting apikey')
                    return (False, '')
            else:
                xbmc.log('-- Login and Device Empty --', xbmc.LOGERROR)
                return (False, '')
        except Exception as exc:
            error('Error in Valid_User', str(exc))
            return (False, '')


def dump_dictionary(details, name):
    if addon.getSetting("spamLog") == 'true':
        if details is not None:
            xbmc.log("---- " + name + ' ----', xbmc.LOGWARNING)

            for i in details:
                if isinstance(details, dict):
                    a = details.get(decode(i))
                    if a is None:
                        temp_log = "\'unset\'"
                    elif isinstance(a, collections.Iterable):
                        # easier for recursion and pretty
                        temp_log = json.dumps(a, sort_keys=True, indent=4, separators=(',', ': '))
                    else:
                        temp_log = str(a)
                    xbmc.log("-" + str(i) + "- " + temp_log, xbmc.LOGWARNING)
                elif isinstance(details, collections.Iterable):
                    temp_log = json.dumps(i, sort_keys=True, indent=4, separators=(',', ': '))
                    xbmc.log("-" + temp_log, xbmc.LOGWARNING)


def post(url, data, headers=None):
    if headers is None:
        headers = {}
    postdata = urlencode(data)
    req = Request(url, postdata, headers)
    req.add_header('User-Agent', UA)
    response = urlopen(req)
    data = response.read()
    response.close()
    return data


def get_shoko_status(force=False):
    return get_server_status(ip=addon.getSetting('ipaddress'), port=addon.getSetting('port'), force=force)


def get_server_status(ip, port, force=False):
    """
    Try to query server for version, if kodi get version respond then shoko server is running
    :return: bool
    """
    try:
        if get_version(ip, port, force) != LooseVersion('0.0'):
            return True
        else:
            return False
    except:
        return False


def get_version(ip, port, force=False):
    legacy = ''
    version = ''
    try:
        _shoko_version = addon.getSetting('good_version')
        _good_ip = addon.getSetting('good_ip')
        if not force:
            if _shoko_version != LooseVersion('0.1') and _good_ip == ip:
                return _shoko_version
        legacy = LooseVersion('0.0')
        json_file = get_json("http://" + str(ip) + ":" + str(port) + "/api/version", direct=True)
        if json_file is None:
            return legacy
        try:
            data = json.loads(json_file)
        except:
            return legacy

        for module in data:
            if module["name"] == "server":
                version = module["version"]
                break

        addon.setSetting(id='good_ip', value=ip)

        if version != '':
            try:
                _shoko_version = LooseVersion(version)
                addon.setSetting(id='good_version', value=str(_shoko_version))
            except:
                return legacy
            return _shoko_version
    except:
        pass
    return legacy


def parse_parameters(input_string):
    """Parses a parameter string starting at the first ? found in inputString

    Argument:
    input_string: the string to be parsed, sys.argv[2] by default

    Returns a dictionary with parameter names as keys and parameter values as values
    """
    parameters = {}
    p1 = input_string.find('?')
    if p1 >= 0:
        split_parameters = input_string[p1 + 1:].split('&')
        for name_value_pair in split_parameters:
            # xbmc.log("parseParameter detected Value: " + str(name_value_pair))
            if (len(name_value_pair) > 0) & ("=" in name_value_pair):
                pair = name_value_pair.split('=')
                key = pair[0]
                value = decode(unquote_plus(pair[1]))
                parameters[key] = value
    return parameters


def post_dict(url, body):
    json_body = ''
    try:
        json_body = json.dumps(body)
    except:
        error('Failed to send data')
    post_data(url, json_body)


def head(url_in):
    try:
        urlopen(url_in)
        return True
    except HTTPError, e:
        # error('HTTPError', e.code)
        return False
    except URLError, e:
        # error('URLError', str(e.args))
        return False
    except Exception, e:
        # error('Exceptions', str(e.args))
        return False


def set_parameter(url, parameter, value):
    value = str(value)
    if value is None or value == '':
        if '?' not in url:
            return url
        array1 = url.split('?')
        if (parameter+'=') not in array1[1]:
            return url
        url = array1[0] + '?'
        array2 = array1[1].split('&')
        for key in array2:
            array3 = key.split('=')
            if array3[0] == parameter:
                continue
            url += array3[0] + '=' + array3[1] + '&'
        return url[:-1]
    value = quote_plus(value)
    if '?' not in url:
        return url + '?' + parameter + '=' + value

    array1 = url.split('?')
    if (parameter+'=') not in array1[1]:
        return url + "&" + parameter + '=' + value

    url = array1[0] + '?'
    array2 = array1[1].split('&')
    for key in array2:
        array3 = key.split('=')
        if array3[0] == parameter:
            array3[1] = value
        url += array3[0] + '=' + array3[1] + '&'
    return url[:-1]


def add_dir(name, url, mode, iconimage='DefaultTVShows.png', plot="", poster="DefaultVideo.png", filename="none",
           offset=''):
    # u=sys.argv[0]+"?url="+url+"&mode="+str(mode)+"&name="+quote_plus(name)+"&poster_file="+quote_plus(poster)+"&filename="+quote_plus(filename)
    u = sys.argv[0]
    if mode is not '':
        u = set_parameter(u, 'mode', str(mode))
    if name is not '':
        u = set_parameter(u, 'name', quote_plus(name))
    u = set_parameter(u, 'poster_file', quote_plus(poster))
    u = set_parameter(u, 'filename', quote_plus(filename))
    if offset is not '':
        u = set_parameter(u, 'offset', offset)
    if url is not '':
        u = set_parameter(u, 'url', url)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
    liz.setProperty("Poster_Image", iconimage)
    if mode is not '':
        if mode == 7:
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
        else:
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    else:
        # should this even possible ? as failsafe I leave it.
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

# not sure if needed


def get_kodi_version():
    """
    This returns a LooseVersion instance containing the kodi version (16.0, 16.1, 17.0, etc)
    """
    version_string = xbmc.getInfoLabel('System.BuildVersion')
    version_string = version_string.split(' ')[0]
    return LooseVersion(version_string)


def kodi_jsonrpc(request):
    try:
        return_data = xbmc.executeJSONRPC(request)
        result = json.loads(return_data)
        return result
    except Exception as exc:
        error("jsonrpc_error: " + str(exc))
