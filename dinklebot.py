__author__ = 'artemredkin'

import db
import json
import urllib

from google.appengine.api import urlfetch


telegram_key = None
api_url = 'https://api.telegram.org/bot'


def message(request):
    r = json.loads(request.body)
    update_id = r['update_id']
    author = r['message']['chat']['id']
    send(author, 'That wizard came from the moon!')
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
