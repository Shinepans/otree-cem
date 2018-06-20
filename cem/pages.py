from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from django.utils.translation import ugettext as _

def vars_for_all_templates(self):
    return {
        'lottery_lo':  c(Constants.lottery_lo),
        'lottery_hi':  c(Constants.lottery_hi),
        'probability': "{0:.1f}".format(Constants.probability) + "%"
    }

class Instructions(Page):

    def is_displayed(self):
        return self.subsession.round_number == 1

class Decision(Page):

    form_model = 'player'

    def get_form_fields(self):

        form_fields = [list(t) for t in zip(*self.participant.vars['cem_choices'])][1]

        if Constants.one_choice_per_page:
            page = self.subsession.round_number
            return [form_fields[page - 1]]
        else:
            return form_fields

    def vars_for_template(self):

        total = Constants.num_choices
        page = self.subsession.round_number
        progress = page / total * 100

        if Constants.one_choice_per_page:
            return {
                'page':      page,
                'total':     total,
                'progress':  progress,
                'choices':   [self.player.participant.vars['cem_choices'][page-1]]
            }
        else:
            return {
                'choices':   self.player.participant.vars['cem_choices']
            }

    def before_next_page(self):

        round_number = self.subsession.round_number
        form_fields = [list(t) for t in zip(*self.participant.vars['cem_choices'])][1]
        indices = [list(t) for t in zip(*self.participant.vars['cem_choices'])][0]
        index = indices[round_number - 1]

        if Constants.one_choice_per_page:

            current_choice = getattr(self.player, form_fields[round_number - 1])
            self.participant.vars['cem_choices_made'][index - 1] = current_choice

            if index == self.player.participant.vars['cem_index_to_pay']:
                self.player.set_payoffs()

            if round_number == Constants.num_choices:
                self.player.set_consistency()
                self.player.set_switching_row()

        if not Constants.one_choice_per_page:

            for j, choice in zip(indices, form_fields):
                choice_i = getattr(self.player, choice)
                self.participant.vars['cem_choices_made'][j - 1] = choice_i

            self.player.set_payoffs()
            self.player.set_consistency()
            self.player.set_switching_row()

class Results(Page):

    def is_displayed(self):
        if Constants.one_choice_per_page:
            return self.subsession.round_number == Constants.num_rounds
        return True

    def vars_for_template(self):
        choices = [list(t) for t in zip(*self.participant.vars['cem_choices'])]
        indices = choices[0]
        index_to_pay = self.player.participant.vars['cem_index_to_pay']
        round_to_pay = indices.index(index_to_pay) + 1
        choice_to_pay = self.participant.vars['cem_choices'][round_to_pay - 1]

        if Constants.one_choice_per_page:
            return {
                'choice_to_pay':  [choice_to_pay],
                'option_to_pay':  self.player.in_round(round_to_pay).option_to_pay,
                'accept_reject':  _("accept") if self.player.in_round(round_to_pay).option_to_pay == "A" else _("reject"),
                'payoff':         self.player.in_round(round_to_pay).payoff,
            }
        else:
            return {
                'choice_to_pay':  [choice_to_pay],
                'option_to_pay':  self.player.option_to_pay,
                'accept_reject':  _("accept") if self.player.option_to_pay == "A" else _("reject"),
                'payoff':         self.player.payoff
            }

page_sequence = [Instructions, Decision, Results]

