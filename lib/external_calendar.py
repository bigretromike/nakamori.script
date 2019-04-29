# -*- coding: utf-8 -*-
import datetime
import json
import os
import re
import xbmc
import xbmcaddon

x = xbmc.translatePath(xbmcaddon.Addon('script.module.nakamori').getAddonInfo('profile'))
x = os.path.join(x, 'json')


def pack_json(new_list):
    fake_json = dict()
    fake_json['art'] = {'thumb': [], 'banner': [], 'fanart': []}
    fake_json['id'] = 0
    fake_json['name'] = 'Airing Soon'
    fake_json['roles'] = None
    fake_json['summary'] = ''
    fake_json['tags'] = None
    fake_json['type'] = 'group'
    fake_json['url'] = ''
    fake_json['series'] = new_list
    fake_json['size'] = len(new_list)
    return fake_json


def return_only_few(when, offset=0):
    offset = int(offset)
    if len(str(when)) == 8:
        year = int(when[0:4])
        month = int(when[4:6])
        day = int(when[6:8])
    else:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = 1

    y = os.path.join(x, '%s-%02d.json' % (year, month))
    if not os.path.exists(y) and not download_external_source(year, month):
        return
    content = open(y, 'r').read()
    pre_body = json.loads(content)
    body = []
    xbmc.log('--------------- CALENDAR 2 --------------', xbmc.LOGNOTICE)
    xbmc.log('year %s %s month %s day %s, when %s %s, offset %s %s, body_len %s' % (year, type(year), month, day, when, type(when), offset, type(offset), len(pre_body)), xbmc.LOGNOTICE)
    for pre in pre_body:
        if int(pre['air'][8:10]) >= day:
            body.append(pre)

    if len(body) > offset and offset != 0:
        body = body[offset:]
    elif len(body) < offset or offset == 0:
        # process next month
        month += 1
        if month == 13:
            month = 1
            year += 1
        y = os.path.join(x, '%s-%02d.json' % (year, month))
        if not os.path.exists(y) and not download_external_source(year, month):
            return
        content = open(y, 'r').read()
        body_new = json.loads(content)
        body = body + body_new
    return json.dumps(pack_json(body))


def download_external_source(year=datetime.datetime.now().year, month=datetime.datetime.now().month):
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib2 import urlopen

    url = 'https://raw.githubusercontent.com/bigretromike/anime-offline-calendar/master/%s-%02d.json' % (year, month)
    xbmc.log('--------------- %s %s %s --------------' % (url, year, month), xbmc.LOGNOTICE)
    content = urlopen(url).read().decode('utf-8')
    y = os.path.join(x, '%s-%02d-tmp.json' % (year, month))
    if os.path.exists(y):
        os.remove(y)
    open(y, 'wb').write(content.encode('utf-8'))
    try:
        response = json.loads(content)
        # 'thumbs/65x100/214829.jpg-thumb.jpg 214829.jpg'
        # https://img7.anidb.net/pics/anime/thumbs/65x100/207605.jpg-thumb.jpg
        series_list = []
        series_item = {}
        for dates in response.get('calendar'):
            for series in response['calendar'][dates]:
                number = re.search(r'65x100\/(.*)\.jpg-thumb', str(series['image'])).group(1)
                x1 = 'thumbs/65x100/' + number + '.jpg-thumb.jpg'
                x2 = number + '.jpg'
                img = str(series['image']).replace(x1, x2)
                xbmc.log(str(series['image']) + 'x1' + str(x1) + 'x2' + str(2) + 'img' + img, xbmc.LOGNOTICE)
                series_item['aid'] = series['aid']
                series_item['air'] = dates
                series_item['art'] = {'thumb': [{'index': 0, 'url': img}], 'banner': [], 'fanart': []}
                series_item['id'] = -1
                series_item['ismovie'] = 0
                series_item['name'] = series['name']
                series_item['rating'] = 0
                series_item['roles'] = []
                series_item['size'] = 0
                series_item['summary'] = ''
                series_item['tags'] = None
                series_item['titles'] = [{'Language': 'x-jat', 'Title': series['name'], 'Type': 'main'}, {'Language': 'ja', 'Title': series['kanji'], 'Type': 'official'}]
                series_item['type'] = 'serie'
                series_item['votes'] = 0
                series_item['year'] = year
                # series['general']
                series_list.append(series_item)
                series_item = {}  # do this because shit get duplicate ?!

        z = os.path.join(x, '%s-%02d.json' % (year, month))
        if os.path.exists(z):
            os.remove(z)
        series_list = sorted(series_list, key=lambda i: (i['air'], i['name']))
        xbmc.log(str(series_list), xbmc.LOGNOTICE)
        con = json.dumps(series_list)
        xbmc.log(str(con), xbmc.LOGNOTICE)
        open(z, 'wb').write(con.encode('utf-8'))
        # clean tmp
        os.remove(y)
        return True
    except Exception as es:
        xbmc.log('error: ' + str(es), xbmc.LOGNOTICE)
        return False
