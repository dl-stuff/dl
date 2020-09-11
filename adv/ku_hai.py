from core.advbase import *
import slot
from slot.a import *
from slot.d import *

def module():
    return Ku_Hai

conf_fs_alt = {
    'fs_apsaras.dmg':0.83*2,
    'fs_apsaras.sp' :330,
    'fs_apsaras.charge': 2/60.0, # needs confirm
    'fs_apsaras.startup':31/60.0,
    'fs_apsaras.recovery':33/60.0,
    'fs_apsaras.hit': 2,
    'fs_apsaras.x2.startup':16/60.0,
    'fs_apsaras.x2.recovery':33/60.0,
    'fs_apsaras.x3.startup':16/60.0,
    'fs_apsaras.x3.recovery':33/60.0,
}

class Ku_Hai(Adv):
    comment = 'c2+fs during s2'
    conf = conf_fs_alt.copy()
    # c1+fs_alt has higher dps and sp rate than c2+fs_alt with or without stellar show  (x)
    # c2+fs_alt fs can init quicker than c1+fs_alt
    conf['slots.a'] = Mega_Friends()+Primal_Crisis()
    conf['slots.poison.a'] = Mega_Friends()+The_Fires_of_Hate()
    conf['slots.d'] = AC011_Garland()
    conf['slots.poison.d'] = Pazuzu()
    conf['acl'] = '''
        `dragon(c3-s-end),fsc
        `s3, not buff(s3)
        `s4
        `s2
        `s1, fsc
        `fs, x=2 and self.fs_alt.get()
        `fs, x=3
        '''
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Akasha']
    conf['share'] = ['Curran']

    def init(self):
        if self.condition('big hitbox'):
            self.conf['fs_apsaras'].dmg += 0.83
            self.conf['fs_apsaras'].hit += 1

    def prerun(self):
        self.fshit = 2
        self.fs_alt = FSAltBuff(group='apsaras', duration=10)

    def s2_proc(self, e):
        self.fs_alt.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)