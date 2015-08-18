__author__ = 'artemredkin'

import json
import urllib
import db

from google.appengine.api import urlfetch
from poster.encode import multipart_encode, MultipartParam


telegram_key = None
api_url = 'https://api.telegram.org/bot'


def recieve(request):
    r = json.loads(request.body)
    message = r['message']['text']
    author = r['message']['from']['id']
    chat = r['message']['chat']['id']
    return chat, author, message.strip()


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
