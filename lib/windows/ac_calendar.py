# -*- coding: utf-8 -*-
import time
import json
import datetime
import re

from nakamori_utils import script_utils
from nakamori_utils import model_utils
from proxy.python_version_proxy import python_proxy as pyproxy
import xbmcgui

from nakamori_utils.globalvars import *

# noinspection PyUnresolvedReferences
from PIL import ImageFont, ImageDraw, Image
import textwrap

ADDON = xbmcaddon.Addon('script.module.nakamori')
CWD = ADDON.getAddonInfo('path').decode('utf-8')

ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

# lists
FIRST_DAY = 55

img = os.path.join(xbmcaddon.Addon('resource.images.nakamori').getAddonInfo('path'), 'resources', 'media')
font_path = os.path.join(xbmcaddon.Addon('script.module.nakamori').getAddonInfo('path'), 'fonts')

# noinspection PyTypeChecker
profileDir = ADDON.getAddonInfo('profile')
profileDir = xbmc.translatePath(profileDir)

color = ADDON.getSetting('color')
font_ttf = ADDON.getSetting('font')
font_size = ADDON.getSetting('size')

# create profile dirs
if not os.path.exists(profileDir):
    os.makedirs(profileDir)
if not os.path.exists(os.path.join(profileDir, 'titles')):
    os.makedirs(os.path.join(profileDir, 'titles'))
if not os.path.exists(os.path.join(profileDir, 'titles', color)):
    os.makedirs(os.path.join(profileDir, 'titles', color))
if not os.path.exists(os.path.join(profileDir, 'titles', color, font_ttf + '-' + font_size)):
    os.makedirs(os.path.join(profileDir, 'titles', color, font_ttf + '-' + font_size))
if not os.path.exists(os.path.join(profileDir, 'json')):
    os.makedirs(os.path.join(profileDir, 'json'))


class Calendar2(xbmcgui.WindowXML):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback, data, item_number=0, start_date=datetime.datetime.now().strftime('%Y%m%d'), fake_data=False):
        self.window_type = 'window'
        self.json_data = data
        self._start_item = 0
        try:
            self._start_item = int(item_number)
        except:
            xbmc.log('E --->' + str(item_number), xbmc.LOGERROR)
        self.calendar_collection = {}
        self.day_of_week = {}
        self.used_dates = []
        self.day_count = 0
        self.serie_processed = int(item_number)
        self.last_processed_date = start_date
        self.fake_data = fake_data

    def onInit(self):
        self.calendar_collection = {
            1: self.getControl(FIRST_DAY),
        }

        self.day_of_week = {
            0: ADDON.getLocalizedString(30010),
            1: ADDON.getLocalizedString(30011),
            2: ADDON.getLocalizedString(30012),
            3: ADDON.getLocalizedString(30013),
            4: ADDON.getLocalizedString(30014),
            5: ADDON.getLocalizedString(30015),
            6: ADDON.getLocalizedString(30016)

        }

        if self.day_count >= 3:
            pass
        else:
            busy = xbmcgui.DialogProgress()
            busy.create(ADDON.getLocalizedString(30017), ADDON.getLocalizedString(30018))
            for gui in self.calendar_collection.values():
                assert isinstance(gui, xbmcgui.ControlList)
                gui.reset()
            _json = json.loads(self.json_data)
            _size = _json.get('size', 0)
            _count = 0

            if _size > 0:
                for series in _json['series']:
                    busy.update(_count/_size)
                    if self.process_series(series):
                        _count += 1
                        pass
                    else:
                        break
            busy.close()
            #if _count == _size:
            #    self.getControl(2).setVisible(False)
            #    self.getControl(2).setEnabled(False)
            self.setFocus(self.getControl(901))

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        elif action == ACTION_NAV_BACK:
            self.close()
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            if self.getFocus().getId() != 2:
                self.list_update_right()
            else:
                if self.fake_data:
                    try:
                        # xbmc.log('---------> I GET 1: self.last_processed_date: %s and %s' % (self.last_processed_date, self.serie_processed), xbmc.LOGNOTICE)
                        xbmc.executebuiltin(script_utils.calendar3(self.last_processed_date, self.serie_processed), True)
                    except Exception as exx:
                        xbmc.log(str(exx), xbmc.LOGNOTICE)
                else:
                    xbmc.executebuiltin(script_utils.calendar(0, self.serie_processed), True)
        elif action == xbmcgui.ACTION_MOVE_LEFT:
            if self.getFocus().getId() != 1:
                self.list_update_left()
            else:
                xbmc.executebuiltin('Action(Back)')
        elif action == xbmcgui.ACTION_MOUSE_RIGHT_CLICK:
            # dont force it on right click;
            pass
        elif action == xbmcgui.ACTION_CONTEXT_MENU:
            control_id = self.getFocus().getId()
            con = self.getControl(control_id)
            assert isinstance(con, xbmcgui.ControlList)
            aid = con.getSelectedItem().getProperty('aid')
            content_menu = [
                '- aid = ' + str(aid) + '-',
                ADDON.getLocalizedString(30037),
                ADDON.getLocalizedString(30038),
                ADDON.getLocalizedString(30039),
                ADDON.getLocalizedString(30040)
            ]
            if xbmcgui.Dialog().contextmenu(content_menu) != -1:
                xbmcgui.Dialog().ok('soon', 'comming soon')
        elif action == xbmcgui.ACTION_SELECT_ITEM:
            xbmcgui.Dialog().ok('soon', 'show soon')
        elif action == xbmcgui.ACTION_MOUSE_LEFT_CLICK:
            if self.getFocus().getId() == 1:
                xbmc.executebuiltin('Action(Back)')
            elif self.getFocus().getId() == 2:
                if self.fake_data:
                    try:
                        # xbmc.log('---------> I GET 2: self.last_processed_date: %s and %s' % (self.last_processed_date, self.serie_processed), xbmc.LOGNOTICE)
                        xbmc.executebuiltin(script_utils.calendar3(self.last_processed_date, self.serie_processed), True)
                    except Exception as exx:
                        xbmc.log(str(exx), xbmc.LOGNOTICE)
                else:
                    xbmc.executebuiltin(script_utils.calendar(0, self.serie_processed), True)

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def process_series(self, series):
        air_date = series.get('air', '')
        if air_date not in self.used_dates:
            self.used_dates.append(air_date)
            self.day_count += 1
            xbmc.log('---------> I SET check %s > len(%s)' % (self.day_count, len(self.calendar_collection)), xbmc.LOGNOTICE)
            if self.serie_processed > 60:
            #if self.day_count > len(self.calendar_collection):  # limit counter
                return False
            air_date = series.get('air', '')

            try:  # python bug workaround
                day_date = datetime.datetime.strptime(air_date, '%Y-%m-%d')
            except TypeError:
                # often this (always)
                day_date = datetime.datetime(*(time.strptime(air_date, '%Y-%m-%d')[0:6]))

            string_day = day_date.strftime('%d/%m')
            name_of_day = day_date.weekday()

            self.last_processed_date = day_date.strftime('%Y%m%d')
            xbmc.log('---------> I SET self.last_processed_date: %s' % self.last_processed_date, xbmc.LOGNOTICE)

        fanart = os.path.join(img, 'icons', 'new-search.png')
        if len(series['art']['thumb']) > 0:
            fanart = series['art']['thumb'][0]['url']
            if fanart is not None and ':' not in fanart:
                fanart = server + fanart
        title = series['titles'][0]['Title']  # support better format here, until then this is ok
        aid = series.get('aid', 0)
        is_movie = series.get('ismovie', 0)
        summary = model_utils.make_text_nice(series.get('summary', ''))
        ep = 0
        if ' - ep' in title:
            search = re.search(r'( \- ep )(\d*)', title)
            ep = search.group(2)
            title = title.replace(search.group(1) + ep, '')

        series_listitem = xbmcgui.ListItem(label=title)
        series_listitem.setArt({'thumb': fanart, 'fanart': fanart})
        # series_listitem.setUniqueIDs({'anidb': aid}')
        series_listitem.setInfo('video', {'title': title, 'aired': air_date, 'plot': summary})
        series_listitem.setProperty('title', title)
        series_listitem.setProperty('aired', str(air_date))
        series_listitem.setProperty('aid', str(aid))
        series_listitem.setProperty('ep', str(ep))
        # 0 = self.day_count
        self.calendar_collection[1].addItem(series_listitem)
        self.serie_processed += 1
        return True

    def list_update_right(self):
        try:
            if self.getFocus().getId > -1:
                # position = self.getControl(self.getFocus().getId()).getSelectedPosition()  # absolute
                _id = self.getFocus().getId()
                position = xbmc.getInfoLabel('Container(%s).Position' % _id)
                move_id = _id + 1
                if move_id <= SEVENTH_DAY:
                    xbmc.executebuiltin('Control.SetFocus(' + str(move_id) + ',' + str(position) + ')')
        except (RuntimeError, SystemError):
            pass

    def list_update_left(self):
        try:
            if self.getFocus().getId > -1:
                # position = self.getControl(self.getFocus().getId()).getSelectedPosition()  # absolute
                _id = self.getFocus().getId()
                position = xbmc.getInfoLabel('Container(%s).Position' % _id)
                move_id = _id - 1
                if move_id >= FIRST_DAY:
                    xbmc.executebuiltin('Control.SetFocus(' + str(move_id) + ',' + str(position) + ')')
        except (RuntimeError, SystemError):
            pass


def open_calendar(date=0, starting_item=0, json_respons=''):
    fake_data = False if json_respons == '' else True
    if not fake_data:
        url = '%s/api/serie/soon?level=2&limit=0&offset=%s&d=%s' % (server, starting_item, date)
        body = pyproxy.get_json(url)
    else:
        body = json_respons
    ui = Calendar2('ac_calendar.xml', CWD, 'Default', '1080i', data=body, item_number=starting_item, fake_data=fake_data)
    ui.doModal()
    del ui


def clear_cache():
    if os.path.exists(os.path.join(profileDir, 'titles')):
        clear = xbmcgui.Dialog().yesno(ADDON.getLocalizedString(30019), ADDON.getLocalizedString(30020))
        if clear:
            files_to_delete = [os.path.join(path, file)
                               for (path, dirs, files) in os.walk(os.path.join(profileDir, 'titles'))
                               for file in files]
            for f in files_to_delete:
                os.remove(f)
                xbmc.log('clear-cache deleted: ' + str(f), xbmc.LOGINFO)
    if os.path.exists(os.path.join(profileDir, 'json')):
        clear = xbmcgui.Dialog().yesno(ADDON.getLocalizedString(30019), ADDON.getLocalizedString(30020))
        if clear:
            files_to_delete = [os.path.join(path, file)
                               for (path, dirs, files) in os.walk(os.path.join(profileDir, 'json'))
                               for file in files]
            for f in files_to_delete:
                os.remove(f)
                xbmc.log('clear-cache deleted: ' + str(f), xbmc.LOGINFO)

