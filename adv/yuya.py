from core.advbase import *

class Yuya(Adv):
    def prerun(self):
        self.a1_hits = 0
        self.a1_buff = SingleActionBuff('a1_sd', 0, 1, 's', 'buff')
        self.set_hp(100)

    def s1_before(self, e):
        self.a1_buff = SingleActionBuff('a1_sd', 0, 1, 's', 'buff')

    def add_combo(self, name='#'):
        result = super().add_combo(name=name)
        if name.startswith('s1'):
            for _ in range(self.echo):
                self.a1_hits += 1
                if self.a1_hits % 3 == 0:
                    cvalue = self.a1_buff.get()
                    if cvalue:
                        self.a1_buff.value(min(1, cvalue+0.05))
                    else:
                        self.a1_buff.on()
                        self.a1_buff.value(0.05)
        return result

variants = {None: Yuya}
