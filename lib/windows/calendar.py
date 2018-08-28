# -*- coding: utf-8 -*-
import os
import time
import json
import datetime

import xbmcgui
import xbmc
import xbmcaddon

import lib.nakamoritools as nt

from PIL import ImageFont, ImageDraw, Image
import textwrap

ADDON = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')

ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
# labels
LABEL_FIRST_DAY = 91
LABEL_FIRST_DAY_DAY = 92
LABEL_SECOND_DAY = 93
LABEL_SECOND_DAY_DAY = 94
LABEL_THIRD_DAY = 95
LABEL_THIRD_DAY_DAY = 96
LABEL_FORTH_DAY = 97
LABEL_FORTH_DAY_DAY = 98
LABEL_FIFTH_DAY = 99
LABEL_FIFTH_DAY_DAY = 100
LABEL_SIXTH_DAY = 101
LABEL_SIXTH_DAY_DAY = 102
LABEL_SEVENTH_DAY = 103
LABEL_SEVENTH_DAY_DAY = 104
# lists
FIRST_DAY = 55
SECOND_DAY = 56
THIRD_DAY = 57
FORTH_DAY = 58
FIFTH_DAY = 59
SIXTH_DAY = 60
SEVENTH_DAY = 61
# buttons
PREV_BUTTON = 1
NEXT_BUTTON = 2

img = os.path.join(xbmcaddon.Addon('resource.images.nakamori').getAddonInfo('path'), 'resources', 'media')
font_path = os.path.join(xbmcaddon.Addon('script.module.nakamori').getAddonInfo('path'), 'fonts')

# noinspection PyTypeChecker
profileDir = ADDON.getAddonInfo('profile')
profileDir = xbmc.translatePath(profileDir)

color = '#ffffff'  # TODO settings later

# create profile dirs
if not os.path.exists(profileDir):
    os.makedirs(profileDir)
if not os.path.exists(os.path.join(profileDir, 'titles')):
    os.makedirs(os.path.join(profileDir, 'titles'))
if not os.path.exists(os.path.join(profileDir, 'titles', color)):
    os.makedirs(os.path.join(profileDir, 'titles', color))


class Calendar2(xbmcgui.WindowXML):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback, data, item_number=0):
        self.window_type = "window"
        self.json_data = data
        self._start_item = 0
        try:
            self._start_item = int(item_number)
        except:
            xbmc.log('E --->' + str(item_number), xbmc.LOGERROR)
        self.calendar_collection = {}
        self.date_label = {}
        self.day_label = {}
        self.day_of_week = {}
        self.used_dates = []
        self.day_count = 0
        self.serie_processed = 0

    def onInit(self):
        self.calendar_collection = {
            1: self.getControl(FIRST_DAY),
            2: self.getControl(SECOND_DAY),
            3: self.getControl(THIRD_DAY),
            4: self.getControl(FORTH_DAY),
            5: self.getControl(FIFTH_DAY),
            6: self.getControl(SIXTH_DAY),
            7: self.getControl(SEVENTH_DAY)
        }

        self.date_label = {
            1: self.getControl(LABEL_FIRST_DAY),
            2: self.getControl(LABEL_SECOND_DAY),
            3: self.getControl(LABEL_THIRD_DAY),
            4: self.getControl(LABEL_FORTH_DAY),
            5: self.getControl(LABEL_FIFTH_DAY),
            6: self.getControl(LABEL_SIXTH_DAY),
            7: self.getControl(LABEL_SEVENTH_DAY)
        }

        self.day_label = {
            1: self.getControl(LABEL_FIRST_DAY_DAY),
            2: self.getControl(LABEL_SECOND_DAY_DAY),
            3: self.getControl(LABEL_THIRD_DAY_DAY),
            4: self.getControl(LABEL_FORTH_DAY_DAY),
            5: self.getControl(LABEL_FIFTH_DAY_DAY),
            6: self.getControl(LABEL_SIXTH_DAY_DAY),
            7: self.getControl(LABEL_SEVENTH_DAY_DAY)
        }

        self.day_of_week = {
            0: 'MON',
            1: 'TUE',
            2: 'WED',
            3: 'THU',
            4: 'FRI',
            5: 'SAT',
            6: 'SUN'
        }

        if self.day_count >= len(self.date_label):
            pass
        else:
            for gui in self.calendar_collection.values():
                gui.reset()

            _json = json.loads(self.json_data)
            _size = _json.get('size', 0)

            if _size > 0:
                for series in _json['series']:
                    if self.process_series(series):
                        pass
                    else:
                        break
            if self.serie_processed == _size:
                self.getControl(2).setVisible(False)
            self.setFocus(self.getControl(901))

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_NAV_BACK:
            self.close()
        if action == xbmcgui.ACTION_MOVE_RIGHT and self.getFocus().getId() != 2:
            self.list_update_right()
        if action == xbmcgui.ACTION_MOVE_LEFT and self.getFocus().getId() != 1:
            self.list_update_left()
        if action == xbmcgui.ACTION_MOVE_RIGHT and self.getFocus().getId() == 2:
            xbmc.executebuiltin('RunScript(script.module.nakamori,?info=calendar&date=0&page='
                                + str(self.serie_processed) + ')', True)
        if action == xbmcgui.ACTION_MOVE_LEFT and self.getFocus().getId() == 1:
            xbmc.executebuiltin('Action(Back)')

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def process_series(self, series):
        air_date = series.get('air', '')
        if air_date not in self.used_dates:
            self.used_dates.append(air_date)
            self.day_count += 1
            if self.day_count > len(self.calendar_collection):  # limit counter
                return False
            air_date = series.get('air', '')

            try:  # python bug workaround
                day_date = datetime.datetime.strptime(air_date, '%Y-%m-%d')
            except TypeError:
                # often this (always)
                day_date = datetime.datetime(*(time.strptime(air_date, '%Y-%m-%d')[0:6]))

            string_day = day_date.strftime('%d/%m')
            name_of_day = day_date.weekday()

            self.day_label[self.day_count].setLabel(self.day_of_week[name_of_day])
            self.date_label[self.day_count].setLabel(string_day)

        fanart = os.path.join(img, 'icons', 'new-search.jpg')
        if len(series["art"]["thumb"]) > 0:
            fanart = series["art"]["thumb"][0]["url"]
            if fanart is not None and ":" not in fanart:
                fanart = nt.server + fanart
        title = series["titles"][0]["Title"]  # support better format here, until then this is ok
        aid = series.get('aid', 0)
        is_movie = series.get('ismovie', 0)
        summary = series.get('summary', '')
        # TODO Window with information
        # TODO on image info about episode when shoko will have it
        # make image title because Kodi refuse to work with smaller/custom font
        new_image_url = os.path.join(profileDir, 'titles', color, str(aid) + '.png')
        if not os.path.exists(new_image_url):
            this_path = os.path.join(font_path, 'UbuntuMono-Bold.ttf')
            font = ImageFont.truetype(this_path, 15, encoding="unic")
            # text_width, text_height = font.getsize(title)  # if we need to calculate something in future
            list_of_lines = textwrap.wrap(title, width=30)
            image = Image.new('RGBA', (250, 50), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            line_x = 5
            line_y = 5
            if len(list_of_lines) > 1:
                for line in list_of_lines:
                    draw.text((line_x, line_y), line, font=font, fill=color)
                    line_y += 20
            else:
                draw.text((line_x, line_y + 20), title, font=font, fill=color)
            image.save(new_image_url, 'PNG')

        series_listitem = xbmcgui.ListItem(label=title)
        series_listitem.setArt({'thumb': fanart, 'poster': new_image_url, 'fanart': fanart})
        # series_listitem.setUniqueIDs({'anidb': aid}, "anidb")
        series_listitem.setInfo('video', {'title': title, 'aired': air_date})
        self.calendar_collection[self.day_count].addItem(series_listitem)
        self.serie_processed += 1
        return True

    def list_update_right(self):
        try:
            if self.getFocus().getId > -1:
                position = self.getControl(self.getFocus().getId()).getSelectedPosition()
                id = self.getFocus().getId()
                move_id = id + 1
                if move_id <= SEVENTH_DAY:
                    xbmc.executebuiltin('Control.SetFocus(' + str(move_id) + ',' + str(position) + ')')
        except (RuntimeError, SystemError):
            pass

    def list_update_left(self):
        try:
            if self.getFocus().getId > -1:
                position = self.getControl(self.getFocus().getId()).getSelectedPosition()
                id = self.getFocus().getId()
                move_id = id - 1
                if move_id >= FIRST_DAY:
                    xbmc.executebuiltin('Control.SetFocus(' + str(move_id) + ',' + str(position) + ')')
        except (RuntimeError, SystemError):
            pass


def open_calendar(date=0, starting_item=0):
    url = "http://%s:%s/api/serie/soon?level=2&limit=0&offset=%s&d=%s" % (nt.addon.getSetting("ipaddress"),
                                                                     nt.addon.getSetting("port"), starting_item, date)
    body = nt.get_json(url)
    ui = Calendar2('calendar.xml', CWD, 'default', '1080i', data=body, item_number=starting_item)
    ui.doModal()
    del ui
