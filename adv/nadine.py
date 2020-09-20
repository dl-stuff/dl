from core.advbase import *

def module():
    return Nadine

class Nadine(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon(c3-s-s-end), s=1
        `s3, not buff(s3)
        `s2
        `s4
        `s1
        `fs, x=5
        """
    conf['coabs'] = ['Blade', 'Wand', 'Marth']
    conf['afflict_res.burn'] = 0
    conf['share'] = ['Summer_Patia']

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


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)