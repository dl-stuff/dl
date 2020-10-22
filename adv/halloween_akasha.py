from core.advbase import *

def is_defdown(attr):
    return 'debuff' in attr and 'def' in attr

class Halloween_Akasha(Adv):
    conf = {'mbleed': True}
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.debuffing_actions = set()

    def prerun(self):
        self.a1_debuff_rate = Selfbuff('a1_debuff_rate', 0.5, 5.0, 'debuff_rate', 'passive')
        self.a1_cd = False
        # make this less potato maybe
        Event('s').listener(self.a1_proc)

    def hitattr_check(self, name, conf):
        super().hitattr_check(name, conf)
        if conf['attr']:
            for attr in conf['attr']:
                if isinstance(attr, int):
                    continue
                if not 'buff' in attr:
                    continue
                if is_defdown(attr['buff']):
                    self.debuffing_actions.add(name)
                elif isinstance(attr['buff'][0], list) and any((is_defdown(b) for b in attr['buff'])):
                    self.debuffing_actions.add(name)

    def a1_proc(self, e):
        if not self.a1_cd and e.name in self.debuffing_actions:
            self.a1_debuff_rate.on()
            self.a1_cd = True
            Timer(self.a1_cd_off).on()

    def a1_cd_off(self, t):
        self.a1_cd = False

class Halloween_Akasha_RNG(Halloween_Akasha):
    conf = {'mbleed': False}

variants = {
    None: Halloween_Akasha,
    'RNG': Halloween_Akasha_RNG
}
