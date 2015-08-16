# -*- coding: utf-8 -*-
__author__ = 'artemredkin'

import db
import json
import urllib

from datetime import datetime, timedelta
from google.appengine.api import urlfetch


telegram_key = None
api_url = 'https://api.telegram.org/bot'


def echo(author, arguments):
    send(author, arguments)


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
        s = s + '\t–\t' + event.comment
    return s


def rsvp(author, cmd):
    if cmd == 'list':
        list = db.find_events()
        if len(list) == 0:
            send(author, "No events")
            return
        events = '\n'.join(map(pretty_event, list)).encode('utf-8')
        send(author, events)


def images(author, arguments):
    pass


commands = {
    '!echo': echo,
    '!r': rsvp,
    '!img': images
}


def message(request):
    r = json.loads(request.body)
    message = r['message']['text']
    author = r['message']['chat']['id']
    if message.startswith('!'):
        (command, arguments) = message.split(None, 1)
        if command in commands:
            commands[command](author, arguments)
    return ''


def send(recipient, message):
    global telegram_key
    global api_url

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
