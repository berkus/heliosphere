__author__ = 'artemredkin'

import db
import telegram
import collections

def parse(message):
    values = message.split(None, 1)
    if len(values) == 1:
        return values[0], None
    return values


def pretty_poll(poll):
    s = u'Poll: ' + poll.question.encode('utf-8')
    s += u'\n'
    answers = []
    for i, a in enumerate(poll.answers):
        answers.append(str(i + 1).encode('utf-8') + u': ' + a)
    s += u'\n'.join(answers)
    return s


class PollCommand:

    def call(self, chat, author, arguments):
        poll = db.get_poll(chat)
        if poll is None:
            telegram.send(chat, 'No active polls')
            return
        telegram.send(chat, pretty_poll(poll))

    def help(self):
        return "Usage: /poll"

    def name(self):
        return "/poll"

    def description(self):
        return "repeat question"


class NewPollCommand:

    def call(self, chat, author, arguments):
        if arguments is None:
            telegram.send(chat, "Add question")
            return
        db.add_poll(chat, arguments)
        telegram.send(chat, "Poll added, now add answers with /answer <answer>")

    def help(self):
        return "Usage: /newpoll"

    def name(self):
        return "/newpoll"

    def description(self):
        return "create a poll"


class AsnwerCommand:

    def call(self, chat, author, arguments):
        poll = db.get_poll(chat)
        if poll is None:
            telegram.send(chat, "No active polls")
            return
        db.add_answer(poll, arguments)
        telegram.send(chat, "Answer addded")

    def help(self):
        return "Usage: /answer <answer>"

    def name(self):
        return "/answer"

    def description(self):
        return "add poll answer"


class VotePollCommand:

    def call(self, chat, author, choice):
        poll = db.get_poll(chat)
        if poll is None:
            telegram.send(chat, "No active poll")
            return
        if choice is None:
            telegram.send(chat, "Specify choice")
            return

        try:
            value = int(choice)
        except ValueError:
            telegram.send(chat, "Specify choice as an integer number")
            return

        if value > len(poll.answers):
            telegram.send(chat, "No such answer")
            return

        db.answer_poll(poll, author, value)
        telegram.send(chat, "Answer recorded")

    def help(self):
        return "Usage: /vote <choice>"

    def name(self):
        return "/vote"

    def description(self):
        return "vote"


class ResultPollCommand:

    def call(self, chat, author, arguments):
        poll = db.get_poll(chat)
        if poll is None:
            telegram.send(chat, "No active poll")
            return
        if len(poll.users_asnwers) is None:
            telegram.send(chat, "No answers yet")
            return
        results = {}
        all_count = len(poll.users_asnwers)
        for user, answer in poll.users_asnwers.iteritems():
            (count, prcnt) = results.get(answer, (0, 0.0))
            count += 1
            results[answer] = (count, (count/all_count * 100))
        s = u'Results:\n'
        answers = []
        for i, answer in enumerate(poll.answers):
            (count, prcnt) = results.get(i + 1, (0, 0.0))
            answers.append(answer + ': ' + str(count).encode('utf-8') + u' votes, ' + str(prcnt).encode('utf-8') + u'%')
        s += '\n'.join(answers)
        telegram.send(chat, s)

    def help(self):
        return "Usage: /results"

    def name(self):
        return "/results"

    def description(self):
        return "see poll results"


class EndPollCommand:

    def call(self, chat, author, command):
        poll = db.get_poll(chat)
        if poll is None:
            telegram.send(chat, "No active poll")
            return
        db.end_poll(poll)


    def help(self):
        return "Usage: /endpoll"

    def name(self):
        return "/endpoll"

    def description(self):
        return "end poll and show results"
