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


def process_month(year, month, day, day_already_processed, url):
    y = os.path.join(x, '%s-%02d.json' % (year, month))
    if not os.path.exists(y) and not download_external_source(url, year, month):
        return
    content = open(y, 'r').read()
    pre_body = json.loads(content)
    body = []

    for pre in pre_body:
        if int(pre['air'][8:10]) >= day:
            if pre['air'] not in day_already_processed:
                if len(day_already_processed) > 7:
                    break
                day_already_processed.append(pre['air'])
            body.append(pre)

    return body


def return_only_few(when, offset=0, url=''):
    offset = int(offset)
    when = str(when)
    if len(when) == 8:
        year = int(when[0:4])
        month = int(when[4:6])
        day = int(when[6:8])
    else:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = 1

    day_already_processed = []
    body = process_month(year, month, day, day_already_processed, url)

    if len(day_already_processed) < 7:
        # process next month
        month += 1
        day = 0
        if month == 13:
            month = 1
            year += 1
        body = body + process_month(year, month, day, day_already_processed, url)
    return json.dumps(pack_json(body))


def download_external_source(url, year=datetime.datetime.now().year, month=datetime.datetime.now().month):
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib2 import urlopen

    url = url % (year, month)

    content = urlopen(url).read().decode('utf-8')
    y = os.path.join(x, '%s-%02d-tmp.json' % (year, month))
    if os.path.exists(y):
        os.remove(y)
    open(y, 'wb').write(content.encode('utf-8'))
    try:
        response = json.loads(content)
        series_list = []
        series_item = {}
        for dates in response.get('calendar'):
            for series in response['calendar'][dates]:
                number = re.search(r'65x100\/(.*)\.jpg-thumb', str(series['image'])).group(1)
                x1 = 'thumbs/65x100/' + number + '.jpg-thumb.jpg'
                x2 = number + '.jpg'
                img = str(series['image']).replace(x1, x2)
                # xbmc.log(str(series['image']) + 'x1' + str(x1) + 'x2' + str(2) + 'img' + img, xbmc.LOGNOTICE)
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
        # xbmc.log(str(series_list), xbmc.LOGNOTICE)
        con = json.dumps(series_list)
        # xbmc.log(str(con), xbmc.LOGNOTICE)
        open(z, 'wb').write(con.encode('utf-8'))
        # clean tmp
        os.remove(y)
        return True
    except Exception as es:
        xbmc.log('error: ' + str(es), xbmc.LOGNOTICE)
        return False
