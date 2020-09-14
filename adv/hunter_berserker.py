from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Hunter_Berserker

hzerk_fs = {
    'fs1': {
        'dmg': 296 / 100.0,
        'sp': 600,
        'charge': 24 / 60.0,
        'startup': 50 / 60.0, # 40 + 10
        'recovery': 40 / 60.0,
        'hit': 1, # w/ combo time and doing a c1
    },
    'fs2': {
        'dmg': 424 / 100.0,
        'sp': 960,
        'charge': 48 / 60.0,
        'startup': 50 / 60.0,
        'recovery': 40 / 60.0,
        'hit': 1, # w/ combo time and doing a c1
    },
    'fs3': {
        'dmg': 548 / 100.0,
        'sp': 1400,
        'charge': 72 / 60.0,
        'startup': 50 / 60.0,
        'recovery': 40 / 60.0,
        'hit': 1, # w/ combo time and doing a c1
    }
}

class Hunter_Berserker(Adv):
    comment = 'needs combo time from chain coability to keep combo & do c1 after s2'
    conf = {}
    conf['slots.a'] = The_Lurker_in_the_Woods()+Primal_Crisis()
    conf['slots.d'] = Dreadking_Rathalos()
    conf['acl'] = """
        `s3, not buff(s3)
        `s1, fsc
        `s4, fsc
        queue self.s2.check()
        `s2
        `fs3, x=1
        end
        `dodge, fsc
        `fs3
    """
    conf['coabs'] = ['Nobunaga','Grace','Marth']
    conf['share'] = ['Hunter_Sarisse']

    def prerun(self):
        self.a3_crit = Modifier('a3', 'crit', 'chance', 0)
        self.a3_crit.get = self.a3_crit_get
        self.a3_crit.on()

    def a3_crit_get(self):
        return (self.mod('def') != 1) * 0.20


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)