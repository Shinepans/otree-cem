from otree.api import Currency as c
from otree.constants import BaseConstants


class Constants(BaseConstants):
    show_app_name = "Risk"

    variation = 'sure_payoff'

    num_choices = 7

    lottery_hi = 5.00
    lottery_lo = 2.00

    probability = 90

    sure_payoff = 2.00

    step_size = 0.50

    endowment = 0.00

    accept_reject = False

    one_choice_per_page = True

    random_order = False

    enforce_consistency = False

    progress_bar = True

    instructions = True

    results = True

    name_in_url = 'cem'
    players_per_group = None
    num_rounds = num_choices if one_choice_per_page else 1
