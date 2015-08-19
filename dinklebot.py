__author__ = 'artemredkin'

import json
import urllib
import urlparse
import db
import telegram
import collections
import rsvp
import logging
import random
import poll

from google.appengine.api import urlfetch


def parse(message):
    values = message.split(None, 1)
    if len(values) == 1:
        return values[0], None
    return values


class Registry():

    def __init__(self):
        self.commands = commands = collections.OrderedDict({})

    def register(self, command):
        self.commands[command.name()] = command


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
        telegram.send(chat, arguments.encode('utf-8'))

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


class QuoteCommand(Command):

    def __init__(self):
        self.quotes = ['We\'ve woken the hiiiveee!', 'Well, at least it\'s chained up.',
                       'An I thought YOU had the hard job.', 'I\'m beginning to sense a pattern!',
                       'Don\'t do that.', 'Can\'t we just stay here with the murderous robots?',
                       'Well that had to ruin their day.', 'I think you got your point across.',
                       'IT\'S IN THE WALLS!!!', 'That wizard came from The Moon.',
                       'Just so you know I have no idea what I\'m doing','This should take us right to the grave.',
                       'I\'m a Ghost, actually', 'We may want to move back.',
                       'Think they\'d mind if we take their Pikes?','Fallen ships this close to the surface.... MOVE!',
                       'This will take just a little while longer.', 'So... think you can kill a God?',
                       'This could be bad!', 'This could be good!', 'This could be going better...',
                       'Those Fallen are just as crazy as we are.', 'I\'ll work faster']

    def call(self, chat, author, arguments):
        telegram.send(chat, random.choice(self.quotes))

    def help(self):
        return "Usage: /quote"

    def name(self):
        return "/quote"

    def description(self):
        return "Dinklebot Wisdom"


r = Registry()
r.register(EchoCommand())
r.register(ImageCommand())
r.register(QuoteCommand())
r.register(rsvp.RsvpRegisterCommand())
r.register(rsvp.RsvpTypesCommand())
r.register(rsvp.RsvpListCommand())
r.register(rsvp.RsvpNewCommand())
r.register(rsvp.RsvpJoinCommand())
r.register(rsvp.RsvpLeaveCommand())
r.register(rsvp.RsvpDeleteCommand())
r.register(poll.PollCommand())
r.register(poll.NewPollCommand())
r.register(poll.AsnwerCommand())
r.register(poll.VotePollCommand())
r.register(poll.ResultPollCommand())
r.register(poll.EndPollCommand())


def recieve(request):
    commands = r.commands
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
            try:
                commands[command].call(chat, author, arguments)
            except Exception as e:
                logging.info(request)
                logging.error(e, exc_info=True)
