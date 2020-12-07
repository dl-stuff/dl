from core.advbase import *

class Yuya(Adv):
    def prerun(self):
        self.a1_hits = 0
        for h in range(1, 13):
            setattr(self, f's1_hit{h}', self.s1_hit)
        self.a1_buff = SingleActionBuff('a1_buff', 0, 1, 's', 'buff')

    def s1_before(self, e):
        self.a1_buff = SingleActionBuff('a1_buff', 0, 1, 's', 'buff')

    def s1_hit(self, name, base, group, aseq):
        self.a1_hits += 1
        if self.a1_hits % 3 == 0:
            cvalue = self.a1_buff.get()
            if cvalue:
                self.a1_buff.value(min(1, cvalue+0.05))
            else:
                self.a1_buff.on()
                self.a1_buff.value(0.05)

variants = {None: Yuya}
