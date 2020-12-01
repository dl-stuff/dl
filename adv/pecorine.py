from core.advbase import *

class Pecorine(Adv):
    def prerun(self):
        self.gourmand_gauge = 0
        self.gourmand_mode = ModeManager(group='gourmand', fs=True, s1=True, duration=20)
        for buff in self.gourmand_mode.buffs:
            buff.no_bufftime()
        self.heal_event.listener(self.a3_buff)
        self.a3_cd = False

    def a1_update(self, gauge):
        if not self.gourmand_mode.get():
            self.gourmand_gauge += gauge
            if self.gourmand_gauge == 100:
                self.gourmand_mode.on()
                self.gourmand_gauge = 0

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        self.a1_update(attr.get('cp', 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit)

    def a3_buff(self, e):
        if not self.a3_cd:
            Selfbuff('a3_att', 0.20, 10, 'att', 'buff').on()
            self.a3_cd = True
            Timer(self.a3_cd_end).on(20)

    def a3_cd_end(self, t):
        self.a3_cd = False

variants = {None: Pecorine}
