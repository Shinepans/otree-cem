from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants
import random

class PlayerBot(Bot):

    def play_round(self):

        page = self.subsession.round_number

        switching_point = self.player.participant.vars['cem-bot_switching_point']

        if Constants.instructions:
            if Constants.one_choice_per_page:
                if page == 1:
                    yield (pages.Instructions)
            else:
                yield (pages.Instructions)

        indices = [list(t) for t in zip(*self.player.participant.vars['cem_choices'])][0]
        form_fields = [list(t) for t in zip(*self.player.participant.vars['cem_choices'])][1]

        if Constants.one_choice_per_page:
            if indices[page - 1] <= switching_point:
                yield (pages.Decision, {
                    form_fields[page - 1]: 'A'
                })
            else:
                yield (pages.Decision, {
                    form_fields[page - 1]: 'B'
            })

        else:
            decisions = []
            for i in indices:
                if i <= switching_point:
                    decisions.append('A')
                else:
                    decisions.append('B')

            choices = zip(form_fields, decisions)
            yield (pages.Decision, {
                i: j for i, j in choices
            })

        if Constants.results:
            if Constants.one_choice_per_page:
                if page == Constants.num_choices:
                    yield (pages.Results)
            else:
                yield (pages.Results)