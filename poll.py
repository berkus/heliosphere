__author__ = 'artemredkin'

import db
import telegram

def parse(message):
    values = message.split(None, 1)
    if len(values) == 1:
        return values[0], None
    return values


def pretty_poll(poll):
    s = 'Poll: ' + poll.question.encode('utf-8') + '\n'
    answers = []
    for i, a in enumerate(poll.answers):
        answers.append(str(i + 1) + ': ' + a.encode('utf-8'))
    s += '\n'.join(answers)
    return s


class PollCommand:

    def call(self, chat, author, arguments):
        poll = db.get_poll(chat)
        if poll is None:
            telegram.send(chat, 'No active polls')
            return
        telegram.send(chat, pretty_poll(poll))

    def help(self):
        return "To see active poll type: /poll"

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
        return "To add new poll type: /newpoll <question>"

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
        return "To add answer to active poll type: /answer <answer>"

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
        return "To vote type: /vote <choice>"

    def name(self):
        return "/vote"

    def description(self):
        return "vote"


def pretty_results(chat, poll):
    if poll.users_asnwers is None:
        telegram.send(chat, "No answers yet")
        return
    results = {}
    all_count = len(poll.users_asnwers)
    for user, answer in poll.users_asnwers.iteritems():
        (count, prcnt) = results.get(answer, (0, 0.0))
        count += 1
        results[answer] = (count, (count/all_count * 100))
    s = 'Results:\n'
    answers = []
    for i, answer in enumerate(poll.answers):
        (count, prcnt) = results.get(i + 1, (0, 0.0))
        answers.append(answer.encode('utf-8') + ': ' + str(count) + ' votes, ' + str(prcnt) + '%')
    s += '\n'.join(answers)
    telegram.send(chat, s)


class ResultPollCommand:

    def call(self, chat, author, arguments):
        poll = db.get_poll(chat)
        if poll is None:
            telegram.send(chat, "No active poll")
            return
        pretty_results(chat, poll)

    def help(self):
        return "To see active poll results type: /results"

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
        pretty_results(chat, poll)
        db.end_poll(poll)


    def help(self):
        return "Usage: /endpoll"

    def name(self):
        return "/endpoll"

    def description(self):
        return "end poll and show results"
