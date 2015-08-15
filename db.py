# -*- coding: utf-8 -*-
__author__ = 'artemredkin'

from datetime import datetime, timedelta
from google.appengine.ext import ndb


class Player(ndb.Model):
    order = ndb.IntegerProperty(indexed=True)
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)
    psn_id = ndb.StringProperty(indexed=False, required=True)
    leader = ndb.BooleanProperty(indexed=True)
    telegram = ndb.StringProperty(indexed=False)
    bungie = ndb.StringProperty(indexed=False)
    dtr = ndb.StringProperty(indexed=False)
    youtube = ndb.StringProperty(indexed=False)
    twitch = ndb.StringProperty(indexed=False)
    list_me = ndb.BooleanProperty(indexed=True)

event_groups = {
    0: "Raids",
    1: "Not Raids, but kewl",
    2: "Strikes and Stories",
    3: "Crucible",
    4: "Other"
}


class EventType(ndb.Model):
    group = ndb.IntegerProperty(indexed=True, required=True)
    name = ndb.StringProperty(indexed=False, required=True)
    capacity = ndb.IntegerProperty(indexed=False, required=True)

    def pretty_group(self):
        return event_groups[self.group]

    def get_id(self):
        return self.key.id()


class Event(ndb.Model):
    author = ndb.KeyProperty(kind=Player, required=True)
    type = ndb.KeyProperty(kind=EventType, required=True)
    date = ndb.DateTimeProperty(indexed=True, required=True)
    comment = ndb.StringProperty(indexed=False)
    participants = ndb.StringProperty(repeated=True)

    def is_participant(self, player):
        for participant in self.participants:
            if participant == player.psn_id:
                return True
        return False

    def can_join(self):
        event_type = EventType.get_by_id(self.type.id())
        return event_type.capacity > len(self.participants)

events_ancestor = ndb.Key(Event, 'Events')


def find_players(only_listed):
    q = Player.query()
    if only_listed:
        q = q.filter(Player.list_me == True)
    return q.fetch()

def find_player(user_id):
    return Player.get_by_id(user_id)


@ndb.transactional(xg=True)
def add_player(user_id, first_name, last_name, psn_id, telegram, bungie, dtr, youtube, twitch, list_me):
    Player(id=user_id, first_name=first_name, last_name=last_name, psn_id=psn_id, list=list, telegram=telegram,
           bungie=bungie, dtr=dtr, youtube=youtube, twitch=twitch, list_me=list_me).put()

@ndb.transactional(xg=True)
def update_player(player, first_name, last_name, psn_id, telegram, bungie, dtr, youtube, twitch, list_me):
    player.first_name = first_name
    player.last_name = last_name
    player.psn_id = psn_id
    player.telegram = telegram
    player.bungie = bungie
    player.dtr = dtr
    player.youtube = youtube
    player.twitch = twitch
    player.list_me = list_me
    player.put()

def find_types():
    return EventType.query().order(EventType.group).fetch()


def find_events():
    return Event.query(Event.date >= datetime.now() + timedelta(hours=1), ancestor=events_ancestor).order(Event.date).fetch(100)


@ndb.transactional(xg=True)
def add_event(player, event_type, date, comment):
    event_type = EventType.get_by_id(event_type).key
    event_id = get_and_increment('Event')
    event = Event(id=str(event_id), parent=events_ancestor, author=player.key, type=event_type, date=date, comment=comment)
    event.put()


@ndb.transactional(xg=True)
def join_event(player, event_id):
    event = Event.get_by_id(event_id, parent=events_ancestor)
    event_type = EventType.get_by_id(event.type.id())
    if event_type.capacity > len(event.participants):
        event.participants.append(player.psn_id)
        event.put()


@ndb.transactional(xg=True)
def leave_event(player, event_id):
    event = Event.get_by_id(event_id, parent=events_ancestor)
    event.participants.remove(player.psn_id)
    event.put()


@ndb.transactional(xg=True)
def delete_event(player, event_id):
    event = Event.get_by_id(event_id, parent=events_ancestor)
    if event.author == player.key:
        event.key.delete()


class Counter(ndb.Model):
    count = ndb.IntegerProperty(default=0)


@ndb.transactional
def get_and_increment(collection):
    counter = Counter.get_by_id(collection)
    if counter is None:
        counter = Counter(id=collection)
    counter.count += 1
    counter.put()
    return counter.count


def init():
    EventType(id='0', group=2, name="Patrol", capacity=3).put()
    EventType(id='1', group=2, name="Story", capacity=3).put()
    EventType(id='2', group=2, name="Daily Heroic Story", capacity=3).put()
    EventType(id='3', group=2, name="Weekly Heroic Strike", capacity=3).put()
    EventType(id='4', group=2, name="Nightfall Strike", capacity=3).put()
    EventType(id='5', group=2, name="Strikes", capacity=3).put()

    EventType(id='6', group=0, name="Vault of Glass – Normal", capacity=6).put()
    EventType(id='7', group=0, name="Vault of Glass – Hard", capacity=6).put()
    EventType(id='8', group=0, name="Crota's End – Normal", capacity=6).put()
    EventType(id='9', group=0, name="Crota's End – Hard", capacity=6).put()

    EventType(id='16', group=1, name="Prison of Elders", capacity=3).put()

    EventType(id='10', group=3, name="Control", capacity=6).put()
    EventType(id='11', group=3, name="Clash", capacity=6).put()
    EventType(id='12', group=3, name="Salvage", capacity=3).put()
    EventType(id='13', group=3, name="Skirmish", capacity=3).put()
    EventType(id='14', group=3, name="Doubles", capacity=3).put()
    EventType(id='15', group=3, name="Rumble", capacity=3).put()

    EventType(id='17', group=3, name="Trials of Osiris", capacity=3).put()

    EventType(id='18', group=4, name="Planetside", capacity=100).put()
    EventType(id='19', group=4, name="Rocket League", capacity=6).put()
