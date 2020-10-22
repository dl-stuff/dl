from core.advbase import *

class Zena(Adv):
    comment = '40 extra hits s2 on Agito size enemy (max 100 without roll & 120 with roll)'
    def prerun(self):
        self.s2_extra_hit_rate = 8 # number of hits per second
        self.s2_timers = []
        Event('dragon').listener(self.s2_clear)

    def s2_extra_hits(self, t):
        for _ in range(self.s2_extra_hit_rate):
            self.dmg_make(f'{t.name}_extra', 0.50)
            self.add_combo()

    def s2_clear(self, e):
        for t in self.s2_timers:
            t.off()

    def s2_proc(self, e):
        self.s2_clear(e)
        for i in range(0, 5):
            t = Timer(self.s2_extra_hits)
            t.name = e.name
            t.on(i)
            self.s2_timers.append(t)

class Zena_ALL(Zena):
    comment = '100 extra hits on s2'
    def prerun(self):
        super().prerun()
        self.s2_extra_hit_rate = 20

variants = {
    None: Zena,
    'ALL': Zena_ALL
}
