# -*- coding: utf-8 -*-
__author__ = 'artemredkin'

import json
import urllib
import urlparse
import db

from datetime import datetime, timedelta
from google.appengine.api import urlfetch
from poster.encode import multipart_encode, MultipartParam


telegram_key = None
google_search_key = None
api_url = 'https://api.telegram.org/bot'


def echo(chat, author, arguments):
    send(chat, arguments)


def pretty_date(event):
    date = event.date
    today = datetime.today().date()
    if date.date() == today:
        return "Today"
    elif date.date() == today - timedelta(hours=24):
        return "Tomorrow"
    else:
        return date.strftime('%A, %B %d')


def pretty_event(event):
    event_name = db.find_type(event.type.id()).name
    participants = '[' + ', '.join(event.participants) + ']'
    s = pretty_date(event) + '\t' + event.date.strftime('%H:%M') + '\t' + event_name + '\t' + participants
    if len(event.comment) > 0:
        s = s + u'\t–\t' + event.comment
    return s


def rsvp(chat, author, cmd):
    if cmd == 'list':
        event_list = db.find_events()
        if len(event_list) == 0:
            send(author, "No events")
            return
        events = '\n'.join(map(pretty_event, event_list)).encode('utf-8')
        send(chat, events)


def images(chat, author, q):
    global google_search_key
    if google_search_key is None:
        google_search_key = db.get_key('google_search')
    data = {
        'key': google_search_key,
        'cx': '009373417816394415455:i3e_omr58us',
        'q': q,
        'searchType': 'image',
        'num': 1
    }
    response = urlfetch.fetch(url='https://www.googleapis.com/customsearch/v1?' + urllib.urlencode(data), method=urlfetch.GET)
    items = json.loads(response.content)['items']
    if len(items) == 0:
        send(chat, "Nothing found")
        return
    image = items[0]
    image_url = image['link']
    image_response = urlfetch.fetch(image_url, method=urlfetch.GET)
    if image_response.status_code != 200:
        send(chat, "Error retrieving image")
        return
    image_name = urlparse.urlsplit(image_url).path.split('/')[-1]
    send_image(chat, image_response.content, image_name, image['mime'])


commands = {
    '!echo': echo,
    '!r': rsvp,
    '!img': images
}


def recieve(request):
    r = json.loads(request.body)
    message = r['message']['text']
    author = r['message']['from']['id']
    chat = r['message']['chat']['id']
    if message.startswith('!'):
        (command, arguments) = message.split(None, 1)
        if command in commands:
            commands[command](chat, author, arguments)
    return ''


def send(recipient, message):
    global telegram_key
    global api_url

    if recipient == 'console':
        print(message)
        return

    if telegram_key is None:
        telegram_key = db.get_key('telegram')
    data = {
        'chat_id': recipient,
        'text': message
    }
    urlfetch.fetch(url=api_url + telegram_key + '/sendMessage',
                   payload=urllib.urlencode(data),
                   method=urlfetch.POST,
                   headers={'Content-Type': 'application/x-www-form-urlencoded'})


def send_image(recipient, image_content, image_name, image_type):
    global telegram_key
    global api_url

    if telegram_key is None:
        telegram_key = db.get_key('telegram')
    data = {
        'chat_id': recipient,
        'photo': MultipartParam('photo', value=image_content, filename=image_name, filetype=image_type)
    }
    payload, headers = multipart_encode(data)
    urlfetch.fetch(url=api_url + telegram_key + '/sendPhoto',
                   payload=''.join(payload),
                   method=urlfetch.POST,
                   headers={'Content-Type': headers['Content-Type']})
