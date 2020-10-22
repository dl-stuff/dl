from core.advbase import *

class Sinoa_RNG(Adv):
    conf = {
        's1': {
            'startup': 0.26667,
            'recovery': 0.83333,
            'attr': []
        }
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.s1_buff_args = [
            (0.25, 15.0, 'att', 'buff'),
            (0.25, 15.0, 'defense', 'buff'),
            (0.25, 10.0, 'crit', 'chance'),
            (0.15, -1, 'maxhp', 'buff')
        ]
    
    def s1_proc(self, e):
        Teambuff(e.name, *random.choice(self.s1_buff_args)).on()

variants = {
    None: Adv,
    'RNG': Sinoa_RNG
}
