from core.advbase import *


class Chelsea(Adv):
    def prerun(self):
        Event("dragon").listener(self.s2_clear)
        Event("s").listener(self.s_hp_check, order=0)
        self.s2_buffs = []

    def s2_clear(self, e):
        for b in self.s2_buffs:
            b.off()
        self.s2_buffs = []

    def fs_before(self, e):
        if self.obsession:
            self.add_hp(-3 * self.obsession)

    def x_before(self, e):
        if self.obsession:
            self.add_hp(-3 * self.obsession)

    def s_hp_check(self, e):
        if self.obsession and e.name in self.damage_sources:
            self.add_hp(-3 * self.obsession)

    @property
    def obsession(self):
        return len(self.s2_buffs)

    def s2_proc(self, e):
        if self.nihilism:
            return
        self.s2_buffs.append(Selfbuff("s2_obsession", 0.3, 60, "att", "buff").on())


variants = {None: Chelsea}
