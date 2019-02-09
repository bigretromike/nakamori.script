# -*- coding: utf-8 -*-
import os
import time
import json
import datetime

import xbmcgui
import xbmc
import xbmcaddon

import nakamoritools as nt

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
        self.serie_processed = int(item_number)

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
            0: ADDON.getLocalizedString(30010),
            1: ADDON.getLocalizedString(30011),
            2: ADDON.getLocalizedString(30012),
            3: ADDON.getLocalizedString(30013),
            4: ADDON.getLocalizedString(30014),
            5: ADDON.getLocalizedString(30015),
            6: ADDON.getLocalizedString(30016)
        }

        if self.day_count >= len(self.date_label):
            pass
        else:
            busy = xbmcgui.DialogProgress()
            busy.create(ADDON.getLocalizedString(30017), ADDON.getLocalizedString(30018))
            for gui in self.calendar_collection.values():
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
            if _count == _size:
                self.getControl(2).setVisible(False)
                self.getControl(2).setEnable(False)
            self.setFocus(self.getControl(901))

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_NAV_BACK:
            self.close()
        if action == xbmcgui.ACTION_MOVE_RIGHT:
            if self.getFocus().getId() != 2:
                self.list_update_right()
            else:
                xbmc.executebuiltin('RunScript(script.module.nakamori,?info=calendar&date=0&page=%s)'
                                    % self.serie_processed, True)
        if action == xbmcgui.ACTION_MOVE_LEFT:
            if self.getFocus().getId() != 1:
                self.list_update_left()
            else:
                xbmc.executebuiltin('Action(Back)')
        if action == xbmcgui.ACTION_MOUSE_RIGHT_CLICK:
            # dont force it on right click;
            pass
        if action == xbmcgui.ACTION_CONTEXT_MENU:
            control_id = self.getFocus().getId()
            aid = self.getControl(control_id).getSelectedItem().getProperty("aid")
            content_menu = [
                '- aid = ' + str(aid) + '-',
                ADDON.getLocalizedString(30037),
                ADDON.getLocalizedString(30038),
                ADDON.getLocalizedString(30039),
                ADDON.getLocalizedString(30040)
            ]
            if xbmcgui.Dialog().contextmenu(content_menu) != -1:
                xbmcgui.Dialog().ok('soon', 'comming soon')
        if action == xbmcgui.ACTION_SELECT_ITEM:
            xbmcgui.Dialog().ok('soon', 'show soon')

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
        new_image_url = os.path.join(profileDir, 'titles', color, font_ttf + '-' + font_size, str(aid) + '.png')
        if not os.path.exists(new_image_url):
            this_path = os.path.join(font_path, font_ttf)
            font = ImageFont.truetype(this_path, int(font_size), encoding="unic")
            text_width, text_height = font.getsize(title)
            text_lenght_till_split = 30
            if text_width + 5 > 250:
                char_width = text_width/float(len(title))
                chars_width = 0
                char_count = 0
                while chars_width < 250:
                    chars_width += char_width
                    char_count += 1
                chars_width -= char_width
                char_count -= 1
                text_lenght_till_split = char_count
                xbmc.log('--> we found that text_lenght_till_split is not correct, so we calculate %s'
                         % text_lenght_till_split, xbmc.LOGWARNING)
            list_of_lines = textwrap.wrap(title, width=int(text_lenght_till_split))
            three_line_support = 1
            for line in list_of_lines[:3]:
                temp_text_width, temp_text_height = font.getsize(line)
                three_line_support += temp_text_height
            if three_line_support < 70:
                three_line_support = 70
            image = Image.new('RGBA', (250, three_line_support), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            line_x = 3
            if len(list_of_lines) > 1:
                for line in reversed(list_of_lines):
                    temp_text_width, temp_text_height = font.getsize(line)
                    three_line_support -= temp_text_height
                    draw.text((line_x, three_line_support), line, font=font, fill=color)
            else:
                draw.text((line_x, 70 - text_height), title, font=font, fill=color)
            image.save(new_image_url, 'PNG')

        series_listitem = xbmcgui.ListItem(label=title)
        series_listitem.setArt({'thumb': fanart, 'poster': new_image_url, 'fanart': fanart})
        # series_listitem.setUniqueIDs({'anidb': aid}, "anidb")
        series_listitem.setInfo('video', {'title': title, 'aired': air_date})
        series_listitem.setProperty('aid', str(aid))
        self.calendar_collection[self.day_count].addItem(series_listitem)
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


def open_calendar(date=0, starting_item=0):
    url = "http://%s:%s/api/serie/soon?level=2&limit=0&offset=%s&d=%s" % (nt.addon.getSetting("ipaddress"),
                                                                          nt.addon.getSetting("port"),
                                                                          starting_item, date)
    body = nt.get_json(url)
    ui = Calendar2('calendar.xml', CWD, 'Default', '1080i', data=body, item_number=starting_item)
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

