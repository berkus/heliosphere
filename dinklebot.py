__author__ = 'artemredkin'

import json
import urllib
import urlparse
import db
import telegram
import collections
import rsvp

from google.appengine.api import urlfetch


def parse(message):
    values = message.split(None, 1)
    if len(values) == 1:
        return values[0], None
    return values


class Command:

    def call(self, chat, author, arguments):
        pass

    def help(self):
        pass

    def name(self):
        pass

    def description(self):
        pass


class EchoCommand(Command):

    def call(self, chat, author, arguments):
        telegram.send(chat, arguments)

    def help(self):
        return "Usage: /echo <string>"

    def name(self):
        return "/echo"

    def description(self):
        return "Send back message"


class ImageCommand(Command):

    def __init__(self):
        self.google_search_key = None

    def call(self, chat, author, q):
        if self.google_search_key is None:
            self.google_search_key = db.get_key('google_search')
        data = {
            'key': self.google_search_key,
            'cx': '009373417816394415455:i3e_omr58us',
            'q': q.encode('utf-8'),
            'searchType': 'image',
            'num': 1
        }
        response = urlfetch.fetch(url='https://www.googleapis.com/customsearch/v1?' + urllib.urlencode(data), method=urlfetch.GET)
        items = json.loads(response.content)['items']
        if len(items) == 0:
            telegram.send(chat, "Nothing found")
            return
        image = items[0]
        image_url = image['link']
        image_response = urlfetch.fetch(image_url, method=urlfetch.GET)
        if image_response.status_code != 200:
            telegram.send(chat, "Error retrieving image")
            return
        image_name = urlparse.urlsplit(image_url).path.split('/')[-1]
        telegram.send_image(chat, image_response.content, image_name, image['mime'])

    def help(self):
        return "Usage: /img <query>"

    def name(self):
        return "/img"

    def description(self):
        return "Google Image Search"


commands = collections.OrderedDict({
    '/echo': EchoCommand(),
    '/img': ImageCommand(),
    '/r': rsvp.RsvpCommand(),
})


def recieve(request):
    (chat, author, message) = telegram.recieve(request)
    if message.startswith('/'):
        (command, arguments) = parse(message)
        if command == '/help':
            if arguments is not None:
                cmd = '/' + arguments
                if cmd not in commands:
                    telegram.send(chat, "Uknown command: " + str(arguments))
                    return
                telegram.send(chat, commands[cmd].help())
                return

            response = 'Commands:'
            for name, command in commands.iteritems():
                response += '\n' + name + ': ' + command.description()
            response += '\n\nType /help <command> to know more'
            telegram.send(chat, response)
            return
        if command in commands:
            commands[command].call(chat, author, arguments)
