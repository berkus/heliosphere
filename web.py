__author__ = 'artemredkin'

import os
import webapp2
import jinja2
import db
import dinklebot

from itertools import groupby
from datetime import datetime, timedelta
from google.appengine.api import users


class PlayerPage(webapp2.RequestHandler):

    def get(self):
        player = db.find_player(users.get_current_user().user_id())
        template_values = {
            'registered': (player is not None),
            'player': player
        }
        template = templates.get_template('player.html')
        self.response.write(template.render(template_values))

    def post(self):
        user_id = users.get_current_user().user_id()
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        psn_id = self.request.get('psn_id')
        list_me = self.request.get('list_me') == 'on'
        telegram = self.request.get('telegram')
        bungie = self.request.get('bungie')
        dtr = self.request.get('dtr')
        youtube = self.request.get('youtube')
        twitch = self.request.get('twitch')

        player = db.find_player(user_id)
        if player is None:
            db.add_player(user_id, first_name, last_name, psn_id, telegram, bungie, dtr, youtube, twitch, list_me)
            self.redirect('/')
        else:
            db.update_player(player, first_name, last_name, psn_id, telegram, bungie, dtr, youtube, twitch, list_me)
            self.redirect('/players')


class InfoPage(webapp2.RequestHandler):

    def get(self):
        player = db.find_player(users.get_current_user().user_id())
        if player is None:
            self.redirect('/players')
            return

        template_values = {
            'players': map(lambda p: p.to_dict(), db.find_players(True))
        }
        template = templates.get_template('info.html')
        self.response.write(template.render(template_values))


class MainPage(webapp2.RequestHandler):

    def get(self):
        player = db.find_player(users.get_current_user().user_id())
        if player is None:
            self.redirect('/players')
            return

        events_page(self, player)

    def post(self):
        event_type = self.request.get('event_type')
        date = self.request.get('date')
        time = self.request.get('time')
        comment = self.request.get('comment')

        event_date = datetime.strptime(date + ' ' + time, '%m/%d/%Y %H:%M')

        player = db.find_player(users.get_current_user().user_id())
        db.add_event(player, event_type, event_date, comment)

        events_for(self, player)


class JoinHandler(webapp2.RequestHandler):

    def put(self, event_id):
        player = db.find_player(users.get_current_user().user_id())
        db.join_event(player, event_id)
        events_for(self, player)

    def delete(self, event_id):
        player = db.find_player(users.get_current_user().user_id())
        db.leave_event(player, event_id)
        events_for(self, player)


class EventHandler(webapp2.RequestHandler):

    def delete(self, event_id):
        player = db.find_player(users.get_current_user().user_id())
        db.delete_event(player, event_id)
        events_for(self, player)


class AdminHandler(webapp2.RequestHandler):

    def get(self, cmd):
        if cmd == 'init':
            db.init()
        elif cmd == 'reindex':
            db.reindex()
        self.response.write("ok")


class BotHandler(webapp2.RequestHandler):

    def post(self):
        dinklebot.recieve(self.request)


def get_template_values(player):
    types_list = db.find_types()
    types = dict(map(lambda event_type: (event_type.key.id(), event_type), types_list))
    grouped_types = groupby(types_list, db.EventType.pretty_group)
    grouped_events = groupby(db.find_events(), pretty_date)

    template_values = {
        'player': player,
        'types': types,
        'grouped_types': grouped_types,
        'grouped_events': grouped_events
    }
    return template_values


def events_page(request, player):
    template = templates.get_template('index.html')
    request.response.write(template.render(get_template_values(player)))


def events_for(request, player):
    template = templates.get_template('events.html')
    request.response.write(template.render(get_template_values(player)))


def pretty_date(event):
    date = event.date
    today = datetime.today().date()
    if date.date() == today:
        return "Today"
    elif date.date() == today - timedelta(hours=24):
        return "Tomorrow"
    else:
        return date.strftime('%A, %B %d')


templates = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/players', PlayerPage),
    ('/info', InfoPage),
    ('/events/(\d+)/participants', JoinHandler),
    ('/events/(\d+)', EventHandler),
    ('/admin/(\w+)', AdminHandler),
    ('/bot/_tell', BotHandler)
], debug=True)
