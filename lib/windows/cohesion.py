# -*- coding: utf-8 -*-
import os
import zlib

import xbmc
import xbmcgui
import xbmcaddon

from nakamori_utils.globalvars import *


# TODO make custom window to show error better

def check_files(directory):
    list_of_error = []
    # plugin.py 0FF6B741
    crc_values = dict()
    with open(os.path.join(directory, 'resources', 'hash.sfv'), 'rb') as fp:
        for line in fp:
            x = line.split(' ')
            crc_values[x[0]] = x[1]

    for root, directories, files in os.walk(directory):
        for filename in files:
            if filename in crc_values:
                buf = open(os.path.join(root, filename), 'rb').read()
                buf = format(zlib.crc32(buf) & 0xFFFFFFFF, 'x')
                if buf != str(crc_values[filename]).rstrip('\r\n'):
                    list_of_error.append(filename)

    return list_of_error


def check_if_installed(script_name):
    return xbmc.getCondVisibility('System.HasAddon(%s)' % script_name) == 1


def check_cohesion():
    list_of_errors = dict()
    progress = xbmcgui.DialogProgress()
    progress.create('Kodi', 'Getting files...')

    progress.update(5, line1='Integrity check', line2='Checking plugin', line3='')
    list_of_errors['plugin'] = check_files(xbmc.translatePath(plugin_addon.getAddonInfo('path')))
    progress.update(20, line1='Integrity check', line2='Checking service', line3='')
    list_of_errors['service'] = check_files(xbmc.translatePath(service_addon.getAddonInfo('path')))
    progress.update(35, line1='Integrity check', line2='Checking script', line3='')
    list_of_errors['script'] = check_files(xbmc.translatePath(script_addon.getAddonInfo('path')))
    progress.update(50, line1='Integrity check', line2='Checking script-lib', line3='')
    list_of_errors['script-lib'] = check_files(xbmc.translatePath(xbmcaddon.Addon('script.module.nakamori-lib').getAddonInfo('path')))
    progress.update(65, line1='Integrity check', line2='Checking player', line3='')
    if check_if_installed('script.module.nakamoriplayer'):
        list_of_errors['player'] = check_files(xbmc.translatePath(xbmcaddon.Addon('script.module.nakamoriplayer').getAddonInfo('path')))

    progress.update(80, line1='Integrity check', line2='Checking plugin', line3='')
    progress.close()

    error = 0
    for key in list_of_errors.keys():
        if len(list_of_errors[key]) > 0:
            error += len(list_of_errors[key])
            xbmcgui.Dialog().ok('Error found in ' + key, str(list_of_errors[key]))
    if error == 0:
        xbmcgui.Dialog().ok('Check complete', 'Your installation is correct')
