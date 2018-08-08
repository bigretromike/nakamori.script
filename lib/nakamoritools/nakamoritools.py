#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import xbmc
import xbmcaddon
import xbmcgui
import sys
import traceback
import os
import json
import Cache as cache
import time
import gzip
import xml
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
    from urllib.request import urlopen
    from urllib.parse import quote, quote_plus, unquote, unquote_plus, urlencode
    from urllib.request import Request
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


addon = xbmcaddon.Addon('plugin.video.nakamori')
addonversion = addon.getAddonInfo('version')
addonid = addon.getAddonInfo('id')
addonname = addon.getAddonInfo('name')
icon = addon.getAddonInfo('icon')
localize = addon.getLocalizedString
server = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port")
python_two = sys.version_info < (3, 0)

__shoko_version__ = LooseVersion('0.1')

try:
    # kodi 17+
    UA = xbmc.getUserAgent()
except:
    # kodi < 17
    UA = 'Mozilla/6.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.5) Gecko/2008092417 Firefox/3.0.3'
pDialog = ''


def searchBox():
    """
    Shows a keyboard, and returns the text entered
    :return: the text that was entered
    """
    keyb = xbmc.Keyboard('', 'Enter search text')
    keyb.doModal()
    searchText = ''

    if keyb.isConfirmed():
        searchText = keyb.getText()
    return searchText


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
    p = re.compile('(\[|\])')
    return p.sub('', data2)

def safeInt(object_body):
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
    elif data_type == 'xml':
        stream = xml(data)
        if stream.get('Code', '') != '':
            code = stream.get('Code')
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
                if stream.get('Message', '') != '':
                    xbmc.log(encode(stream.get('Message')), xbmc.LOGERROR)


def get_json(url_in, direct=False):
    body = ""
    if direct:
        body = get_data(url_in, None, "json")
    else:
        if (addon.getSetting("enableCache") == "true") and ("file?id" not in url_in):
            db_row = cache.check_in_database(url_in)
            if db_row is None:
                db_row = 0
            if db_row > 0:
                expire_second = time.time() - float(db_row)
                if expire_second > int(addon.getSetting("expireCache")):
                    # expire, get new date
                    body = get_data(url_in, None, "json")
                    params = {}
                    params['extras'] = 'single-delete'
                    params['name'] = url_in
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
        return True
    else:
        xbmc.log('-- apikey empty --')
        try:
            if addon.getSetting("login") != "" and addon.getSetting("device") != "":
                body = '{"user":"' + addon.getSetting("login") + '",' + \
                       '"device":"' + addon.getSetting("device") + '",' + \
                       '"pass":"' + addon.getSetting("password") + '"}'
                post_body = post_data(server + "/api/auth", body)
                auth = json.loads(post_body)
                if "apikey" in auth:
                    xbmc.log('-- save apikey and reset user credentials --')
                    addon.setSetting(id='apikey', value=str(auth["apikey"]))
                    addon.setSetting(id='login', value='')
                    addon.setSetting(id='password', value='')
                    return True
                else:
                    raise Exception('Error Getting apikey')
            else:
                xbmc.log('-- Login and Device Empty --')
                return False
        except Exception as exc:
            error('Error in Valid_User', str(exc))
            return False


def dump_dictionary(details, name):
    if addon.getSetting("spamLog") == 'true':
        if details is not None:
            xbmc.log("---- " + name + ' ----', xbmc.LOGWARNING)

            for i in details:
                temp_log = ""
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


def post(url, data, headers={}):
    postdata = urlencode(data)
    req = Request(url, postdata, headers)
    req.add_header('User-Agent', UA)
    response = urlopen(req)
    data = response.read()
    response.close()
    return data


def get_server_status(ip, port):
    """
    Try to query server for version, if kodi get version respond then shoko server is running
    :return: bool
    """
    try:
        if get_version(ip, port) != LooseVersion('0.0'):
            return True
        else:
            return False
    except:
        return False


def get_version(ip, port):
    legacy = ''
    version = ''
    try:
        global __shoko_version__
        if __shoko_version__ != LooseVersion('0.1'):
            return __shoko_version__
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

        if version != '':
            try:
                __shoko_version__ = LooseVersion(version)
            except:
                return legacy
            return __shoko_version__
    except:
        pass
    return legacy


# old
def debug(text):
    xbmc.log(str([text]), xbmc.LOGDEBUG)


def request(url, headers={}):
    debug('request: %s' % url)
    req = Request(url, headers=headers)
    req.add_header('User-Agent', UA)
    response = urlopen(req)
    data = response.read()
    response.close()
    debug('len(data) %s' % len(data))
    return data


def makeLink(params, baseUrl):
    """
    Build a link with the specified base URL and parameters

    Parameters:
    params: the params to be added to the URL
    BaseURL: the base URL, sys.argv[0] by default
    """
    return baseUrl + '?' + urlencode(
        dict([encode(k), encode(decode(v))] for k, v in params.items()))


def parseParameters(input_string):
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


def getURL(url, header):
    try:
        req = Request(url, headers=header)
        response = urlopen(req)
        if response and response.getcode() == 200:
            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(response.read())
                gzip_f = gzip.GzipFile(fileobj=buf)
                content = gzip_f.read()
            else:
                content = response.read()
            content = decode(content)
            return content
        return False
    except:
        xbmc.log('Error Loading URL (Error: ' + str(response.getcode()) +
                 ' Encoding:' + response.info().get('Content-Encoding') + '): ' + url, xbmc.LOGERROR)
        xbmc.log('Content: ' + response.read(), xbmc.LOGERROR)
        return False


def post_dict(url, body):
    json = ''
    try:
        json = json.dumps(body)
    except:
        error('Failed to send data')
    post_data(url, json)


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


import xml.etree.ElementTree as Tree


def xml(xml_string):
    """
    return an xml tree from string with error catching
    Args:
        xml_string: the string containing the xml data

    Returns: ElementTree equivalentof Tree.XML()

    """
    e = Tree.XML(xml_string)
    if e.get('ErrorString', '') != '':
        error(e.get('ErrorString'), 'JMM Error')
    return e


def safeName(name):
    return re.sub(r'[^a-zA-Z0-9 ]', '', name.lower()).replace(" ", "_")


def stripInvalid(name):
    return re.sub(r'[^a-zA-Z0-9 ]', ' ', name.lower())


def urlSafe(name):
    return re.sub(r'[^a-zA-Z0-9 ]', '', name.lower())
