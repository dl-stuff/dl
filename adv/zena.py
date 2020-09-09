from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Zena

conf_fs_alt = {
    'fs_heal.dmg':0,
    'fs_heal.sp' :0,
    'fs_heal.charge': 30/60.0,
    'fs_heal.startup': 20/60.0,
    'fs_heal.recovery': 60/60.0,
}

class Zena(Adv):
    comment = '40 extra hits s2 on Agito size enemy (max 100 without roll & 120 with roll)'
    conf = conf_fs_alt.copy()
    conf['slots.a'] = Candy_Couriers()+Primal_Crisis()
    conf['acl'] = """
        `s3, not buff(s3)
        `s2
        `s4
        `s1

        # If healing FS is needed
        # `fs, s1.check() and self.fs_alt.uses>0
        # `s3, not buff(s3)
        # `s2
        # `s4
        # `s1, fsc or self.fs_alt.uses=0
        """
    conf['coabs'] = ['Blade', 'Delphi', 'Bow']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

    def prerun(self):
        self.fs_alt = FSAltBuff('heal', uses=1)
        self.s2_extra_hit_rate = 8 # number of hits per second
        self.s2_timers = []
        Event('dragon').listener(self.s2_clear)

    def prerun_skillshare(self, dst):
        self.fs_alt = Dummy()

    def s1_proc(self, e):
        self.fs_alt.on()

    def s2_extra_hits(self, t):
        self.dmg_make(f'{t.name}_extra', self.s2_extra_hit_rate*0.50)
        self.add_hits(self.s2_extra_hit_rate)

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

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
