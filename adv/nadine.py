from core.advbase import *

class Nadine(Adv):
    def prerun(self):
        self.team_s1_hits = 1
        teammates = 2
        if self.condition(f'{teammates} teammates in s1'):
            self.team_s1_hits += teammates

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.team_s1_hits = 1
        teammates = 2
        if adv.condition(f'{teammates} teammates in s1'):
            adv.team_s1_hits += teammates

    def s1_proc(self, e):
        for _ in range(self.team_s1_hits):
            self.add_combo(e.name)
        aseq = 1 if e.group == 'default' else 3 + 1
        s1_hits = 1 if e.group == 'default' else 3 + self.team_s1_hits
        log('debug', 's1_hits', s1_hits, self.team_s1_hits)
        if s1_hits <= 3:
            self.hitattr_make(e.name, e.base, e.group, aseq, self.conf[e.name].extra_3)
            self.energy.add(1)
            return
        if s1_hits <= 5:
            self.hitattr_make(e.name, e.base, e.group, aseq, self.conf[e.name].extra_5)
            self.energy.add(3)
            return
        if s1_hits >= 6:
            self.hitattr_make(e.name, e.base, e.group, aseq, self.conf[e.name].extra_6)
            self.energy.add(5)
            return

variants = {
    None: Nadine
    'RNG': Nadine
}
