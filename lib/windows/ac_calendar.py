# -*- coding: utf-8 -*-
import time
import json
import datetime
import _strptime  # fix for import lockis held by another thread.
import re
import os

from nakamori_utils import script_utils
from nakamori_utils import model_utils
from proxy.python_version_proxy import python_proxy as pyproxy
import xbmcgui
import xbmc
import xbmcaddon

from nakamori_utils.globalvars import *

# noinspection PyUnresolvedReferences
try:
    from PIL import ImageFont, ImageDraw, Image
except ImportError:
    pass
import textwrap

ADDON = xbmcaddon.Addon('script.module.nakamori')
CWD = ADDON.getAddonInfo('path')  # .decode('utf-8')

ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

# lists
FIRST_DAY = 55

img = os.path.join(xbmcaddon.Addon('resource.images.nakamori').getAddonInfo('path'), 'resources', 'media')
font_path = os.path.join(xbmcaddon.Addon('script.module.nakamori').getAddonInfo('path'), 'fonts')

# noinspection PyTypeChecker
profileDir = ADDON.getAddonInfo('profile')
profileDir = xbmc.translatePath(profileDir)

color = ADDON.getSetting('ac_color')
font_ttf = ADDON.getSetting('ac_font')
font_size = ADDON.getSetting('ac_size')

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
        # xbmcgui.WindowXML.__init__(self)
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
        self.scroll_down_refresh = False
        self.calendar_end = False

    def AddSeriesToCalendar(self):
        if not self.calendar_end:
            busy = xbmcgui.DialogProgress()
            busy.create(ADDON.getLocalizedString(30017), ADDON.getLocalizedString(30018))

            if self.json_data != '' and self.fake_data and len(self.used_dates) > 0:
                try:
                    from lib.external_calendar import return_only_few
                    last_date = datetime.datetime(*(time.strptime(self.last_processed_date, '%Y%m%d')[0:6]))
                    last_date = last_date + datetime.timedelta(days=1)
                    self.last_processed_date = last_date.strftime('%Y%m%d')
                    when = self.last_processed_date
                    page = self._start_item
                    body = return_only_few(when=when, offset=page, url=str(script_addon.getSetting('custom_url')))
                    self.json_data = body
                except Exception as ex:
                    xbmcgui.Dialog().ok('error', str(ex))
                    self.json_data = ''
                    self.calendar_end = True

            _size = 0
            _json = None
            if self.json_data != '':
                _json = json.loads(self.json_data)
                _size = _json.get('size', 0)
            _count = 0

            if _size > 0:
                for series in _json['series']:
                    busy.update(int(_count / _size))
                    if self.process_series(series):
                        _count += 1
                        pass
                    else:
                        break

            busy.close()

    def onInit(self):
        self.calendar_collection = {
            1: self.getControl(FIRST_DAY),
        }

        if self.day_count >= 3:
            pass
        else:
            self.AddSeriesToCalendar()
            self.setFocus(self.getControl(901))

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        elif action == ACTION_NAV_BACK:
            self.close()
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            self.list_update_right()
        elif action == xbmcgui.ACTION_MOVE_LEFT:
            self.list_update_left()
        elif action == xbmcgui.ACTION_MOVE_DOWN:
            self.list_update_down()
        elif action == xbmcgui.ACTION_MOVE_UP:
            self.list_update_up()
        elif action == xbmcgui.ACTION_MOUSE_RIGHT_CLICK:
            pass
        elif action == xbmcgui.ACTION_CONTEXT_MENU:
            try:
                control_id = self.getFocus().getId()
                con = self.getControl(control_id)
                assert isinstance(con, xbmcgui.ControlList)
                aid = con.getSelectedItem().getProperty('aid')
                url = '%s/api/serie/fromaid?id=%s' % (server, aid)
                body = json.loads(pyproxy.get_json(url))
                if 'aid' not in body:
                    return

                content_menu = [
                    '- aid = ' + str(aid) + '-',
                    ADDON.getLocalizedString(30037),
                    ADDON.getLocalizedString(30038),
                    ADDON.getLocalizedString(30039),
                    ADDON.getLocalizedString(30040)
                ]
                my_pick = xbmcgui.Dialog().contextmenu(content_menu)
                if my_pick != -1:
                    if my_pick <= 1:
                        if body.get('id', -1) == -1:
                            xbmc.executebuiltin(script_utils.series_info(aid=aid), True)
                        else:
                            xbmc.executebuiltin(script_utils.series_info(id=id), True)
                    elif my_pick > 1:
                        xbmcgui.Dialog().ok('soon', 'comming soon')
            except:
                # in case 404 for that series - thats possible !
                pass
        elif action == xbmcgui.ACTION_SELECT_ITEM:
            xbmcgui.Dialog().ok('soon', 'show soon')
        elif action == xbmcgui.ACTION_MOUSE_LEFT_CLICK:
            if self.getFocus().getId() == 1:
                xbmc.executebuiltin('Action(Back)')
            elif self.getFocus().getId() == 2:
                if self.fake_data:
                    try:
                        xbmc.executebuiltin(script_utils.ac_calendar(self.last_processed_date, self.serie_processed), True)
                    except Exception as exx:
                        xbmc.log(str(exx), xbmc.LOGNOTICE)
                else:
                    xbmc.executebuiltin(script_utils.ac_calendar(0, self.serie_processed), True)
        elif action == xbmcgui.ACTION_SCROLL_DOWN or action == xbmcgui.ACTION_MOUSE_WHEEL_DOWN:
            _id = self.getFocus().getId()
            currentpage = xbmc.getInfoLabel('Container(%s).CurrentPage' % _id)
            numpages = xbmc.getInfoLabel('Container(%s).NumPages' % _id)

            if currentpage == numpages:
                self.scroll_down_refresh = True

            if self.scroll_down_refresh:
                self.scroll_down_refresh = False
                self.AddSeriesToCalendar()

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def process_series(self, series):
        air_date = series.get('air', '')
        if air_date not in self.used_dates:
            self.used_dates.append(air_date)
            self.day_count += 1
            if self.serie_processed > 60:
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

        # generate description image
        new_image_url = os.path.join(profileDir, 'titles', color, font_ttf + '-' + font_size, str(aid) + '_d.png')
        if not os.path.exists(new_image_url):
            image_x = 241
            image_y = 105
            font_wide_mitigation = 6
            this_path = os.path.join(font_path, font_ttf)
            font = ImageFont.truetype(this_path, int(font_size), encoding='unic')
            if len(summary) == 0:
                summary = ' '
            text_width, text_height = font.getsize(summary)
            text_lenght_till_split = 30
            if text_width + font_wide_mitigation > image_x:
                char_width = text_width / float(len(summary))
                chars_width = 0
                char_count = 0
                while chars_width < image_x - font_wide_mitigation:
                    chars_width += char_width
                    char_count += 1
                chars_width -= char_width
                char_count -= 1
                text_lenght_till_split = char_count
                xbmc.log('--> we found that text_lenght_till_split is not correct, so we calculate %s'
                         % text_lenght_till_split, xbmc.LOGWARNING)

            list_of_lines = textwrap.wrap(summary, width=int(text_lenght_till_split))
            three_line_support = 1
            processed_line = []
            for line in list_of_lines:
                temp_text_width, temp_text_height = font.getsize(line)
                three_line_support += temp_text_height
                processed_line.append(line)
                if three_line_support > image_y:
                    three_line_support -= temp_text_height
                    del processed_line[-1]
                    break

            image = Image.new('RGBA', (image_x, image_y), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            line_x = 0
            last_line = True
            if len(processed_line) > 1:
                for line in reversed(processed_line):
                    if last_line:
                        last_line = False
                        if len(line) > 3:
                            line = line[:-3] + '...'
                    temp_text_width, temp_text_height = font.getsize(line)
                    three_line_support -= temp_text_height
                    draw.text((line_x, three_line_support), line, font=font, fill=color)
            else:
                draw.text((line_x, 70 - text_height), summary, font=font, fill=color)
            image.save(new_image_url, 'PNG')

        series_listitem = xbmcgui.ListItem(label=title)
        series_listitem.setArt({'thumb': fanart, 'fanart': fanart, 'poster': new_image_url})
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
        pass

    def list_update_left(self):
        pass

    def list_update_up(self):
        pass

    def list_update_down(self):
        try:
            if self.getFocus().getId() > -1:
                _id = self.getFocus().getId()
                position = xbmc.getInfoLabel('Container(%s).Position' % _id)
                row = xbmc.getInfoLabel('Container(%s).Row' % _id)
                column = xbmc.getInfoLabel('Container(%s).Column' % _id)
                currentpage = xbmc.getInfoLabel('Container(%s).CurrentPage' % _id)
                numpages = xbmc.getInfoLabel('Container(%s).NumPages' % _id)
                numitems = xbmc.getInfoLabel('Container(%s).NumItems' % _id)
                numallitems = xbmc.getInfoLabel('Container(%s).NumAllItems' % _id)

                _position = self.calendar_collection[1].getSelectedPosition()  # absolute
                _size = self.calendar_collection[1].size()
                if _position + 3 >= _size:
                    self.AddSeriesToCalendar()
                    self.calendar_collection[1].selectItem(_position)

        except Exception as ex:
            xbmcgui.Dialog().ok('error', str(ex))


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

