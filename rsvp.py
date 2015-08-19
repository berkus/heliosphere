# -*- coding: utf-8 -*-
__author__ = 'artemredkin'

import db
import telegram

from datetime import date, datetime, timedelta


def pretty_date(event):
    d = event.date
    today = datetime.today().date()
    if d.date() == today:
        return "Today"
    elif d.date() == today - timedelta(hours=24):
        return "Tomorrow"
    else:
        return d.strftime('%A, %B %d')


def pretty_event(event):
    event_name = db.find_type(event.type.id()).name
    participants = '\n'.join(event.participants)
    s = ('#' + str(event.key.id()) + ': ' + pretty_date(event) + '  at  ' + event.date.strftime('%H:%M') + '\n' + event_name).encode('utf-8')
    if len(event.comment) > 0:
        s += '  –  ' + event.comment.encode('utf-8')
    s += '\n' + participants.encode('utf-8')
    return s


class RsvpRegisterCommand:

    def call(self, chat, author, psn_id):
        if psn_id is None:
            telegram.send(chat, "Specify your psn-id")
            return
        player = db.find_player_by_psn_id(psn_id)
        if player is None:
            telegram.send(chat, "Player with psn-id " + psn_id + " not found")
            return
        db.register_player_telegram(player, author)
        telegram.send(chat, psn_id + " registered")

    def help(self):
        return "Usage: /register <psn-id>"

    def name(self):
        return "/register"

    def description(self):
        return "Register with LFG bot"


class RsvpTypesCommand:

    def call(self, chat, author, arguments):
        player = db.find_player_by_telegram_id(author)
        if player is None:
            telegram.send(chat, "Introduce yourself by providing your psn id: /register <psn-id>")
            return
        type_list = db.find_types()
        telegram.send(chat, '\n'.join(map(lambda t: t.code.encode('utf-8') + ': ' + t.name.encode('utf-8'), type_list)))

    def help(self):
        return "Usage: /types"

    def name(self):
        return "/types"

    def description(self):
        return "List available types"


class RsvpListCommand:

    def call(self, chat, author, arguments):
        player = db.find_player_by_telegram_id(author)
        if player is None:
            telegram.send(chat, 'Introduce yourself by providing your psn id: /register <psn-id>')
            return
        event_list = db.find_events()
        if len(event_list) == 0:
            telegram.send(author, 'No events')
            return
        if arguments is None:
            event_list = filter(lambda e: e.date.date() == datetime.today().date(), event_list)
        elif arguments == 'my':
            event_list = filter(lambda e: player.psn_id in e.participants, event_list)
        elif arguments == 'all':
            pass
        elif arguments is not None:
            event_type = db.find_type_by_code(arguments).key
            event_list = filter(lambda e: e.type == event_type, event_list)

        for e in event_list:
            telegram.send(chat, pretty_event(e))

    def help(self):
        return "Usage: /list [my|all|type]"

    def name(self):
        return "/list"

    def description(self):
        return "List available events"


class RsvpNewCommand:

    def call(self, chat, author, arguments):
        player = db.find_player_by_telegram_id(author)
        if player is None:
            telegram.send(chat, "Introduce yourself by providing your psn id: /register <psn-id>")
            return
        (event_type_code, date_code, time_code, comment) = self.parse_arguments(chat, arguments)
        event_type = db.find_type_by_code(event_type_code)
        if event_type is None:
            telegram.send(chat, "Event type not found: " + event_type_code + ", see available types: /types")
            return
        if date_code == 'today':
            day = date.today()
        elif date_code == 'tomorrow':
            day = date.today() + timedelta(days=1)
        else:
            year = date.today().year
            day = datetime.strptime(date_code, '%d/%m')
            day = day.replace(year=year)
        if comment is None:
            comment = ""
        d = datetime.combine(day, datetime.strptime(time_code, '%H:%M').time())
        event_id = db.add_event(player, event_type.key.id(), d, comment)
        telegram.send(chat, 'Event #' + event_id + ' added')

    def parse_arguments(self, chat, arguments):
        values = arguments.split(None, 3)
        if len(values) < 3:
            telegram.send(chat, "Not enough arguments")
            return
        if len(values) < 4:
            return values + [None]
        return values

    def help(self):
        return "/event <event type> <date> <time> [comment]"

    def name(self):
        return "/event"

    def description(self):
        return "Add new event"


class RsvpJoinCommand:

    def call(self, chat, author, event_id):
        player = db.find_player_by_telegram_id(author)
        if player is None:
            telegram.send(chat, "Introduce yourself by providing your psn id: /register <psn-id>")
            return
        db.join_event(player, event_id)
        telegram.send(chat, player.psn_id + ' joined event #' + event_id)

    def help(self):
        return "Usage: /join <event id>"

    def name(self):
        return "/join"

    def description(self):
        return "Join event"


class RsvpLeaveCommand:

    def call(self, chat, author, event_id):
        player = db.find_player_by_telegram_id(author)
        if player is None:
            telegram.send(chat, "Introduce yourself by providing your psn id: /register <psn-id>")
            return
        db.leave_event(player, event_id)
        telegram.send(chat, player.psn_id + ' left event #' + event_id)

    def help(self):
        return "Usage: /leave <event id>"

    def name(self):
        return "/leave"

    def description(self):
        return "Leave event"


class RsvpDeleteCommand:

    def call(self, chat, author, event_id):
        player = db.find_player_by_telegram_id(author)
        if player is None:
            telegram.send(chat, "Introduce yourself by providing your psn id: /register <psn-id>")
            return
        db.delete_event(player, event_id)
        telegram.send(chat, "Deleted")

    def help(self):
        return "Usage: /rm <event id>"

    def name(self):
        return "/rm"

    def description(self):
        return "Delete event"
