from core.advbase import *

class Elisanne_55MC(Adv):
    conf = {
        'c': {
            'att': 497,
            'hp': 812,
            'spiral': False,
            'a': [['bt', 0.25]]
        },
        's1': {
            'recovery': 1.0,
            'attr': [
                {'buff': ['team', 0.2, 15.0, 'att', 'buff'], 'iv': 0.16667}
            ]
        },
        's2': {
            'attr': [
                {'dmg': 7.54, 'iv': 0.96667}
            ]
        }
    }

variants = {
    None: Adv,
    '55MC': Elisanne_55MC
}