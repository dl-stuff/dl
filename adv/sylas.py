from core.advbase import *

class Sylas_RNG(Sylas):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conf.s2.startup += 0.13333
        self.conf.s2.recovery -= 0.13333
        del self.conf.s2['attr']
        self.s2_buff_args = [
            (0.25, 15.0, 'att', 'buff'),
            (0.25, 15.0, 'defense', 'buff'),
            (0.20, -1, 'maxhp', 'buff'),
            'all'
        ]
    
    def s1_proc(self, e):
        pick = random.choice(self.s2_buff_args)
        if pick == 'all':
            for buffarg in self.s2_buff_args[0:3]:
                Teambuff(e.name, *buffarg).on()
        else:
            Teambuff(e.name, *pick).on()

variants = {
    None: Adv,
    'RNG': Sylas_RNG
}
