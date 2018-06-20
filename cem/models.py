from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from cem.config import *
import random
from random import randrange

class Subsession(BaseSubsession):

    def creating_session(self):
        if self.round_number == 1:

            n = Constants.num_choices
            for p in self.get_players():

                indices = [j for j in range(1, n + 1)]

                form_fields = ['choice_' + str(k) for k in indices]

                if Constants.variation == 'probability':
                    probabilities = [Constants.probability + (k - 1) * Constants.step_size for k in indices]
                else:
                    probabilities = [Constants.probability for k in indices]

                if Constants.variation == 'lottery_hi':
                    lottery_hi = [c(Constants.lottery_hi + (k - 1) * Constants.step_size) for k in indices]
                else:
                    lottery_hi = [c(Constants.lottery_hi) for k in indices]

                if Constants.variation == 'lottery_lo':
                    lottery_lo = [c(Constants.lottery_lo - (k - 1) * Constants.step_size) for k in indices]
                else:
                    lottery_lo = [c(Constants.lottery_lo) for k in indices]

                if Constants.variation == 'sure_payoff':
                    sure_payoffs = [c(Constants.sure_payoff + (k-1) * Constants.step_size) for k in indices]
                else:
                    sure_payoffs = [c(Constants.sure_payoff) for k in indices]

                p.participant.vars['cem_choices'] = list(
                    zip(
                        indices,
                        form_fields,
                        probabilities,
                        lottery_hi,
                        lottery_lo,
                        sure_payoffs
                    )
                )

                p.participant.vars['cem_index_to_pay'] = random.choice(indices)
                p.participant.vars['cem_choice_to_pay'] = 'choice_' + str(p.participant.vars['cem_index_to_pay'])

                if Constants.random_order:
                    random.shuffle(p.participant.vars['cem_choices'])

                p.participant.vars['cem_choices_made'] = [None for j in range(1, n + 1)]

            for participant in self.session.get_participants():
                participant.vars['cem-bot_switching_point'] = random.randint(1, n)

class Group(BaseGroup):
    pass

class Player(BasePlayer):

    for j in range(1, Constants.num_choices + 1):
        locals()['choice_' + str(j)] = models.StringField()
    del j

    random_draw = models.IntegerField()
    choice_to_pay = models.StringField()
    option_to_pay = models.StringField()
    inconsistent = models.IntegerField()
    switching_row = models.IntegerField()

    def set_payoffs(self):

        self.random_draw = randrange(1, 100)

        self.choice_to_pay = self.participant.vars['cem_choice_to_pay']

        self.option_to_pay = getattr(self, self.choice_to_pay)

        indices = [list(t) for t in zip(*self.participant.vars['cem_choices'])][0]
        index_to_pay = indices.index(self.participant.vars['cem_index_to_pay']) + 1
        choice_to_pay = self.participant.vars['cem_choices'][index_to_pay - 1]

        if self.option_to_pay == 'A':
            if self.random_draw <= choice_to_pay[2]:
                self.payoff = Constants.endowment + choice_to_pay[3]
            else:
                self.payoff = Constants.endowment + choice_to_pay[4]
        else:
            self.payoff = Constants.endowment + choice_to_pay[5]

        ## Record Multi Apps vars
        self.participant.vars['cem_payoff'] = self.payoff

    def set_consistency(self):

        n = Constants.num_choices

        self.participant.vars['cem_choices_made'] = [
            1 if j == 'A' else 0 for j in self.participant.vars['cem_choices_made']
        ]

        for j in range(1, n):
            choices = self.participant.vars['cem_choices_made']
            self.inconsistent = 1 if choices[j] > choices[j - 1] else 0
            if self.inconsistent == 1:
                break

    def set_switching_row(self):

        if self.inconsistent == 0:
            self.switching_row = sum(self.participant.vars['cem_choices_made']) + 1
