from core.advbase import *
from slot.a import *

def module():
    return Hunter_Vanessa

hvan_fs = {
    'fs1': {
        'dmg': 143 / 100.0,
        'sp': 100,
        'charge': 24 / 60.0,
        'startup': 17 / 60.0,
        'recovery': 46 / 60.0,
        'hit': 1,
    },
    'fs2': {
        'dmg': 370 / 100.0,
        'sp': 300,
        'charge': 72 / 60.0,
        'startup': 17 / 60.0,
        'recovery': 46 / 60.0,
        'hit': 1,
    }
}

class Hunter_Vanessa(Adv):
    conf = hvan_fs.copy()
    conf['slots.a'] = Mega_Friends()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, s
        `s2, not self.s2_att_boost.get()
        `fs2, cancel and (s1.charged>=s1.sp-self.sp_val('fs2') or s4.charged>=s4.sp-self.sp_val('fs2'))
        `s3, not self.s3_buff and fsc
        `s1, fsc
        `s4, fsc
        `dodge,fsc
        `fs2,x=5
        """
    conf['coabs'] = ['Sharena','Blade','Peony']
    conf['afflict_res.paralysis'] = 0
    conf['share'] = ['Kleimann']

    def d_slots(self):
        if self.duration <= 60:
            self.conf['slots.a'] = Mega_Friends()+The_Chocolatiers()

    def prerun(self):
        self.s2_att_boost = Selfbuff('s2', 0.30, 90, 'att', 'buff')

        self.a3_crit = Modifier('a3', 'crit', 'chance', 0)
        self.a3_crit.get = self.a3_crit_get
        self.a3_crit.on()

        self.fs_debuff = Debuff('fs',0.05,15)

    def a3_crit_get(self):
        return (self.mod('def') != 1) * 0.20

    def s1_proc(self, e):
        self.afflics.paralysis(e.name,120, 0.97)

    def s2_proc(self, e):
        self.s2_att_boost.on()

    def fs_proc(self, e):
        if e.level == 2:
            self.fs_debuff.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
