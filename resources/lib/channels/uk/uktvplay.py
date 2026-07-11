# -*- coding: utf-8 -*-
# Copyright: (c) 2017, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
from builtins import str
import json
import re

from codequick import Listitem, Resolver, Route
from kodi_six import xbmcgui
import urlquick

# UKTV-001: START use UKTVPlay artwork
import os
import xbmcvfs
# UKTV-001: END use UKTVPlay artwork

# UKTV-008: START debug message
import xbmc
debug = True
def log_message(message, level=xbmc.LOGINFO):
    """
    Logs a message to the Kodi log file.
    
    :param message: The text to log
    :param level: Kodi log level (default: LOGINFO)
    """
    try:
        if not isinstance(message, str):
            message = str(message)
        xbmc.log(f"[U] {message}", level)
    except Exception as e:
        xbmc.log(f"[U] Logging failed: {e}", xbmc.LOGERROR)
# UKTV-008: END debug message

# UKTV-009: START Custom Main menu
media_dir = xbmcvfs.translatePath('special://userdata/customisations/Addon Icons/VOD Addon Artwork/U/')
# UKTV-009: END Custom Main menu

from resources.lib import resolver_proxy, web_utils

from resources.lib.menu_utils import item_post_treatment


URL_ROOT = 'https://u.co.uk'

URL_API = 'https://vschedules.uktv.co.uk'

LETTER_LIST = [
    "0-9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
]

URL_PROGRAMS = URL_API + '/vod/brand_list/?starts_with=%s&letter_name=%s&is_watchable=True'
# Letter

URL_INFO_PROGRAM = URL_API + '/vod/brand/?slug=%s'
# Program_slug

URL_VIDEOS = URL_API + '/vod/series/?id=%s'
# Serie_ID

URL_CATEGORIES = URL_API + '/vod/categories/'

URL_PROGRAMS_SUBCATEGORY = URL_API + '/vod/subcategory_brands/?slug=%s&size=999'
# Slug subcategory

URL_LIVE = 'https://u.uktv.co.uk/watch-live/%s'
# Channel name

URL_STREAM_LIVE = 'https://v2-streams-elb.simplestreamcdn.com/api/live/stream/%s?key=%s&platform=chrome&user=%s'
# data_channel, key, user

URL_CHANNEL_ID = "https://vschedules.uktv.co.uk/vod/now_and_next/"

URL_LIVE_KEY = 'https://mp.simplestream.com/uktv/1.0.4/ss.js'

URL_LIVE_TOKEN = 'https://sctoken.uktvapi.co.uk/?stream_id=%s'
# data_channel

URL_LOGIN_TOKEN = 'https://s3-eu-west-1.amazonaws.com/uktv-static/fgprod/play/6fc13c8.js'

URL_LOGIN_MODAL = 'https://uktvplay.uktv.co.uk/account/'

URL_COMPTE_LOGIN = 'https://live.mppglobal.com/api/accounts/authenticate/'

URL_CHUNKS = "https://u.co.uk/shows/%s/series-%s/episode-%s/%s"

GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}

# UKTV-001: use UKTVPlay artwork
HOME              = xbmcvfs.translatePath('special://home/')
ADDONS            = os.path.join(HOME,     'addons')
RESOURCE_IMAGES   = os.path.join(ADDONS,   'resource.images.catchuptvandmore')
RESOURCES         = os.path.join(RESOURCE_IMAGES,   'resources')
CHANNELS          = os.path.join(RESOURCES,         'channels')
UK_CHANNELS       = os.path.join(CHANNELS,          'uk')
fanartpath        = os.path.join(UK_CHANNELS,       'u_fanart.jpg')
iconpath          = os.path.join(UK_CHANNELS,       'u.png')
# END UKTV-001: use UKTVPlay artwork

# UKTV-003: Customise Viewtypes
# @Route.register
@Route.register(content_type="images")

# UKTV-009: START Custom Main Menu
# def list_categories(plugin, item_id, **kwargs):
    #"""
    #Build categories listing
    #
    #item = Listitem()
    #item.label = 'A-Z'
    #item.set_callback(list_letters, item_id=item_id)
    #item_post_treatment(item)
    #yield item
    #
    #resp = urlquick.get(URL_CATEGORIES, headers=GENERIC_HEADERS, max_age=-1)
    #json_parser = json.loads(resp.text)
    #
    #for category_datas in json_parser["categories"]:
    #    category_title = category_datas["name"]
    #    category_slug = category_datas["slug"]
    #    item = Listitem()
    #    item.label = category_title
    #    item.set_callback(list_sub_categories,
    #                      item_id=item_id,
    #                      category_slug=category_slug)
    #    item_post_treatment(item)
    #    yield item


def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    """
    item = Listitem()
    item.label = 'A-Z'
    # UKTV-009: START Custom main menu 
    item.art["thumb"] = media_dir + 'A - Z.png'
    item.art["fanart"] = ''
    # UKTV-009: END Custom main menu 
    item.set_callback(list_letters, item_id=item_id)
    item_post_treatment(item)
    yield item

    resp = urlquick.get(URL_CATEGORIES, headers=GENERIC_HEADERS, max_age=-1)
    json_parser = json.loads(resp.text)

    for category_datas in json_parser["categories"]:
        category_title = category_datas["name"]
        category_slug = category_datas["slug"]
        item = Listitem()
        item.label = category_title
        # UKTV-009: START Custom main menu        
        item.art["thumb"] = media_dir + category_title + '.png'
        item.art["fanart"] = ''
        # UKTV-009: END Custom main menu 
        item.set_callback(list_sub_categories,
                          item_id=item_id,
                          category_slug=category_slug)
        item_post_treatment(item)
        yield item
    # UKTV-009: END Custom Main Menu


# UKTV-003: Customise Viewtypes
# @Route.register
@Route.register(content_type="files")
def list_sub_categories(plugin, item_id, category_slug, **kwargs):

    resp = urlquick.get(URL_CATEGORIES, headers=GENERIC_HEADERS, max_age=-1)
    json_parser = json.loads(resp.text)

    for category_datas in json_parser["categories"]:
        if category_slug in category_datas["slug"]:
            for sub_category_datas in category_datas["subcategories"]:
                sub_category_title = sub_category_datas["name"]
                sub_category_slug = sub_category_datas["slug"]
                item = Listitem()
                item.label = sub_category_title
                # UKTV-001: use UKTVPlay artwork 
                item.art["thumb"] = iconpath
                item.art["fanart"] = ''
                # END UKTV-001: use UKTVPlay artwork                  
                item.set_callback(list_programs_sub_categories,
                                  item_id=item_id,
                                  sub_category_slug=sub_category_slug)
                item_post_treatment(item)
                yield item


# UKTV-003: Customise Viewtypes
# @Route.register
@Route.register(content_type="videos")
def list_programs_sub_categories(plugin, item_id, sub_category_slug, **kwargs):

    resp = urlquick.get(URL_PROGRAMS_SUBCATEGORY % sub_category_slug, headers=GENERIC_HEADERS, max_age=-1)
    json_parser = json.loads(resp.text)

    for program_datas in json_parser["brand_list"]:
        # UKTV-008: START debug
        if debug == True:
            log_message('list_programs_sub_categories: program_datas = ' + str(program_datas))
        # UKTV-008: END debug        
        program_title = program_datas['name']
        program_image = ''
        if 'image' in program_datas:
            program_image = program_datas['image']
        program_slug = program_datas['slug']

        item = Listitem()
        item.label = program_title
        item.art['thumb'] = item.art['landscape'] = program_image       
        # UKTV-002: use program_image as fanart
        if 'hero_image_4k' in program_datas:
            item.art['fanart'] = program_datas['hero_image_4k']        
        else:
            item.art['fanart'] = program_image
        # END UKTV-002: use program_image as fanart        
        # UKTV-004: START improve plot/descriptions
        if 'medium_description' in program_datas:
            item.info['plot'] = program_datas['medium_description']
        elif 'description' in program_datas:
            item.info['plot'] = program_datas['description']
        else:
            item.info['plot'] = program_title        
        # UKTV-004: END improve plot/descriptions       

        # UKTV-005: START Set up tvshow data
        item.info['mediatype'] = 'tvshow'
        item.info['tvshowtitle'] = program_title
        item.info['title'] = program_title
        # UKTV-005: END Set up tvshow data
        
        item.set_callback(list_seasons,
                          # UKTV-002: START add program_title, program_image and to parameters
                          program_title=program_title,
                          program_image=program_image,
                          fanart=item.art['fanart'],
                          # UKTV-002: END add program_title, program_image and to parameters
                          item_id=item_id,
                          program_slug=program_slug)
        item_post_treatment(item)
        yield item


# UKTV-003: Customise Viewtypes
# @Route.register
@Route.register(content_type="files")
def list_letters(plugin, item_id, **kwargs):
    """
    Build programs listing
    - Les feux de l'amour
    - ...
    """
    for letter_value in LETTER_LIST:
        item = Listitem()
        item.label = letter_value
        # UKTV-001: use UKTVPlay artwork 
        item.art["thumb"] = iconpath
        item.art["fanart"] = ''
        # END UKTV-001: use UKTVPlay artwork 
        item.set_callback(list_programs,
                          item_id=item_id,
                          letter_value=letter_value)
        item_post_treatment(item)
        yield item


# UKTV-003: Customise Viewtypes
# @Route.register
@Route.register(content_type="videos")
def list_programs(plugin, item_id, letter_value, **kwargs):

    resp = urlquick.get(URL_PROGRAMS %
                        (letter_value.replace('0-9', '0'), letter_value),
                        headers=GENERIC_HEADERS, max_age=-1)
    json_parser = json.loads(resp.text)

    for program_datas in json_parser:
        # UKTV-008: START debug
        if debug == True:
            log_message('list_programs: program_datas = ' + str(program_datas))
        # UKTV-008: END debug           
        program_title = program_datas['name']
        program_image = ''
        if 'image' in program_datas:
            program_image = program_datas['image']
        program_slug = program_datas['slug']

        item = Listitem()
        item.label = program_title
        item.art['thumb'] = item.art['landscape'] = program_image
        # UKTV-002: use program_image as fanart
        if 'hero_image_4k' in program_datas:
            item.art['fanart'] = program_datas['hero_image_4k']        
        else:
            item.art['fanart'] = program_image
        # END UKTV-002: use program_image as fanart        
        # UKTV-004: START improve plot/descriptions
        if 'medium_description' in program_datas:
            item.info['plot'] = program_datas['medium_description']
        elif 'description' in program_datas:
            item.info['plot'] = program_datas['description']
        else:
            item.info['plot'] = program_title        
        # UKTV-004: END improve plot/descriptions
        
        # UKTV-005: START Set up tvshow data
        item.info['mediatype'] = 'tvshow'
        item.info['tvshowtitle'] = program_title
        item.info['title'] = program_title
        # UKTV-005: END Set up tvshow data
        item.set_callback(list_seasons,
                          # UKTV-002: START add program_title, program_image and to parameters
                          program_title=program_title,
                          program_image=program_image,
                          fanart=item.art['fanart'],
                          # UKTV-002: END add program_title, program_image and to parameters
                          item_id=item_id,
                          program_slug=program_slug)
        item_post_treatment(item)
        yield item


# UKTV-003: Customise Viewtypes
# @Route.register
@Route.register(content_type="seasons")
# UKTV-002: START add program_title, program_image and fanart to parameters
# def list_seasons(plugin, item_id, program_slug, **kwargs):
def list_seasons(plugin, program_title, program_image, fanart, item_id, program_slug, **kwargs):
# UKTV-002: END add program_title, program_image and fanart to parameters

    resp = urlquick.get(URL_INFO_PROGRAM % program_slug, headers=GENERIC_HEADERS, max_age=-1)
    json_parser = json.loads(resp.text)

    for season_datas in json_parser["series"]:
        # UKTV-008: START debug
        if debug == True:
            log_message('list_seasons: season_datas = ' + str(season_datas))
        # UKTV-008: END debug 
        
        season_title = 'Season - ' + season_datas['number']
        serie_id = season_datas["id"]

        item = Listitem()
        item.label = season_title
        
        # UKTV-005: START Set up season data
        item.info['season'] = season_datas['number']
        item.info['mediatype'] = 'season'
        item.info['tvshowtitle'] = program_title
        item.info['title'] = season_title
        # UKTV-005: END Set up season data     
        
        # UKTV-002: use Program Image artwork instead of CUTV&More artwork for seasons
        item.art["landscape"] = program_image
        item.art["fanart"] = fanart
        # END UKTV-002: use Program Image artwork instead of CUTV&More artwork for seasons        
        
        # UKTV-002: use Program Image artwork instead of CUTV&More artwork for videos fanart      
        # item.set_callback(list_videos, item_id=item_id, serie_id=serie_id)
        item.set_callback(list_videos, item.art["fanart"], item_id=item_id, serie_id=serie_id)
               
        item_post_treatment(item)
        yield item


# UKTV-003: Customise Viewtypes
# @Route.register
@Route.register(content_type="videos")
# UKTV-002: use Program Image artwork instead of CUTV&More artwork for videos fanart
# def list_videos(plugin, item_id, serie_id, **kwargs): 
def list_videos(plugin, program_image, item_id, serie_id, **kwargs): 
    
    resp = urlquick.get(URL_VIDEOS % serie_id, headers=GENERIC_HEADERS, max_age=-1)
    json_parser = json.loads(resp.text)

    for video_datas in json_parser["episodes"]:
        # UKTV-008: START debug
        if debug == True:
            log_message('list_videos: video_datas = ' + str(video_datas))
        # UKTV-008: END debug         
        video_title = video_datas["brand_name"] + \
            ' - ' ' S%sE%s' % (video_datas["series_number"], str(video_datas["episode_number"])) + ' - ' + video_datas["name"]
        video_image = video_datas["image"]
        video_plot = video_datas["synopsis"]
        video_duration = video_datas["duration"] * 60
        video_id = video_datas["video_id"]

        show_name = URL_CHUNKS % (video_datas["brand_slug"],
                                  video_datas["series_number"],
                                  video_datas["episode_number"],
                                  video_datas["video_id"])

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = item.art['landscape'] = video_image
        
        # UKTV-002: START use Program Image artwork instead of CUTV&More artwork for videos fanart        
        item.art["fanart"] = program_image
        # UKTV-002: END use Program Image artwork instead of CUTV&More artwork for videos fanart        

        # UKTV-005: START Set up episode data
        if 'episode_number' in video_datas:
            item.info['episode'] = video_datas['episode_number']
            item.info['season'] = video_datas['series_number']
            item.info['mediatype'] = 'episode'
            item.info['tvshowtitle'] = video_datas['brand_name']
            item.info['title'] = video_datas['name']
        # UKTV-005: END Set up episode data
        
        item.info['plot'] = video_plot
        item.info['duration'] = video_duration
        item.set_callback(get_video_url,
                          item_id=item_id,
                          data_video_id=video_id,
                          show_name=show_name)
        item_post_treatment(item)
        yield item


@Resolver.register
def get_video_url(plugin, item_id, data_video_id, show_name, **kwargs):
    data_account = "1242911124001"
    data_player = "0RyQs9qPh"

    return resolver_proxy.get_brightcove_video_json(plugin, data_account, data_player, data_video_id)


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    # create session request
    session_requests = urlquick.session()
    session_requests.get(URL_LOGIN_MODAL, headers=GENERIC_HEADERS, max_age=-1)

    resptokenid = session_requests.get(URL_LOGIN_TOKEN, headers=GENERIC_HEADERS, max_age=-1)
    token_id = re.compile(r'tokenid\":\"(.*?)\"').findall(resptokenid.text)[0]

    if plugin.setting.get_string(
            'uktvplay.login') == '' or plugin.setting.get_string(
                'uktvplay.password') == '':
        xbmcgui.Dialog().ok('Info',
                            plugin.localize(30604) %
                            ('UKTVPlay', 'https://uktvplay.uktv.co.uk'))
        return False

    # Build PAYLOAD
    payload = {
        'email': plugin.setting.get_string('uktvplay.login'),
        'password': plugin.setting.get_string('uktvplay.password')
    }
    payload = json.dumps(payload)

    # LOGIN
    # KO - resp2 = session_urlquick.post(
    #     URL_COMPTE_LOGIN, data=payload,
    #     headers={'User-Agent': web_utils.get_ua, 'referer': URL_COMPTE_LOGIN})
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://uktvplay.uktv.co.uk',
        'Content-Type': 'application/json;charset=UTF-8',
        'Referer': 'https://uktvplay.uktv.co.uk/account/',
        'User-Agent': web_utils.get_random_ua(),
        'X-TokenId': token_id,
        'X-Version': '9.0.0'
    }
    resp = session_requests.post(URL_COMPTE_LOGIN, data=payload, headers=headers, max_age=-1)
    if resp.status_code >= 400:
        plugin.notify('ERROR', 'UKTVPlay : ' + plugin.localize(30711))
        return False
    json_parser_resplogin = json.loads(resp.content)

    if 'home_uktvplay' in item_id:
        channel_uktvplay_id = 'home'
    else:
        channel_uktvplay_id = item_id

    resp = session_requests.get(URL_CHANNEL_ID, headers=GENERIC_HEADERS, max_age=-1)
    root = json.loads(resp.text)
    data_channel = str(root[channel_uktvplay_id][0]['channel_stream_id'])

    respkey = session_requests.get(URL_LIVE_KEY, headers=GENERIC_HEADERS, max_age=-1)
    app_key = re.compile(r'app\_key"\ \: \"(.*?)\"').findall(respkey.text)[0]

    resp = session_requests.get(URL_LIVE_TOKEN % data_channel, headers=GENERIC_HEADERS, max_age=-1)
    json_parser_resptoken = json.loads(resp.text)

    data_url = URL_STREAM_LIVE % (data_channel, app_key, str(json_parser_resplogin["accountId"]))
    headers = {
        'Token-Expiry': json_parser_resptoken["expiry"],
        'Token': json_parser_resptoken["token"],
        'Uvid': data_channel,
        'Userid': str(json_parser_resplogin["accountId"]),
        "User-Agent": web_utils.get_random_ua()
    }
    respstreamdatas = session_requests.post(data_url, headers=headers, max_age=-1)
    json_parser = json.loads(respstreamdatas.text)

    headers = {'Content-type': ''}
    video_url = json_parser["response"]["drm"]["widevine"]["stream"]
    license_url = json_parser["response"]["drm"]["widevine"]["licenseAcquisitionUrl"]

    return resolver_proxy.get_stream_with_quality(plugin, video_url=video_url, license_url=license_url,
                                                  headers=headers, manifest_type='mpd')
