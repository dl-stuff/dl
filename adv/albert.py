from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Albert

# non electrified fs
conf_albert_fs = {
    'fs.dmg': 1.265
}

class Albert(Adv):
    a1 = ('fs',0.5)
    conf = conf_albert_fs.copy()
    conf['slots.d'] = Corsaint_Phoenix()
    conf['slots.a'] = The_Shining_Overlord()+Spirit_of_the_Season()
    conf['slots.paralysis.a'] = conf['slots.a']
    conf['acl'] = """
        if self.electrified.get()
        `s1
        `s3, fsc
        if x=3
        `fs2, not self.afflics.paralysis.get()
        `fs1
        end
        else
        `dragon
        `s2, s1.charged>=s1.sp-self.sp_val(2)
        `s1, cancel
        `s3, cancel
        `s4, cancel
        end
        """
    coab = ['Blade','Wand','Peony']
    share = ['Kleimann', 'Ranzal']
    conf['afflict_res.paralysis'] = 0

    def init(self):
        self.conf.fs.hit = 1
        conf_alt_fs = {
            'fs1': {
                'dmg': 1.12,
                'sp': 330,
                'charge': 4 / 60.0,
                'startup': 9 / 60.0,
                'recovery':26 / 60.0,
            },
            'fs2': {
                'dmg': 1.12,
                'sp': 330,
                'charge': 34 / 60.0, # 0.5 ?
                'startup': 9 / 60.0,
                'recovery':26 / 60.0,
            }
        }
        for n, c in conf_alt_fs.items():
            self.conf[n] = Conf(c)
            act = FS_MH(n, self.conf[n])
            self.__dict__['a_'+n] = act
        
        self.l_fs1 = Listener('fs1',self.l_fs1)
        self.l_fs2 = Listener('fs2',self.l_fs2)
        self.fs = None

    def do_fs(self, e, name):
        log('cast',e.name)
        self.__dict__['a_'+name].getdoing().cancel_by.append(name)
        self.__dict__['a_'+name].getdoing().interrupt_by.append(name)
        self.fs_before(e)
        self.update_hits('fs')
        self.dmg_make('fs', self.conf[name+'.dmg'], 'fs')
        e.name = name
        self.fs_proc(e)
        self.think_pin('fs')
        self.charge(name,self.conf[name+'.sp'])

    def l_fs1(self, e):
        self.do_fs(e, 'fs1')

    def fs1(self):
        return self.electrified.get() and self.a_fs1()

    def l_fs2(self, e):
        self.do_fs(e, 'fs2')

    def fs2(self):
        return self.electrified.get() and self.a_fs2()

    def prerun(self):
        self.s2.autocharge_init(self.s2autocharge).on()
        self.electrified = Selfbuff('electrified',1, 25,'ss','ss')
        self.a1_fs = Selfbuff('a1_fs_passive',0.10, 25,'fs','passive')
        self.a3_att = Selfbuff('a3_att_passive',0.30, 25,'att','passive')
        self.a3_spd = Spdbuff('a3_spd', 0.10, 25)

        self.fs_alt_timer = Timer(self.fs_alt_end)
        self.s1_hits = 6 if self.condition('big hitbox') else 4

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.electrified = Dummy()

    def fs_alt_end(self,t):
        self.fs_alt.off()

    def s2autocharge(self, t):
        if not self.electrified.get():
            self.s2.charge(28000)
            log('sp','s2autocharge')

    def fs_proc(self, e):
        if not self.electrified.get():
            self.s2.charge(-50000)
        elif e.name == 'fs2':
            self.afflics.paralysis('fs',120,0.97)

    def s1_proc(self, e):
        with KillerModifier('s1_killer','hit',0.2,['paralysis']):
            if self.electrified.get():
                self.dmg_make(e.name, 12.38)
                for _ in range(2, self.s1_hits+1):
                    self.dmg_make(e.name, 0.83)
                    self.add_hits(1)
                extend = self.s1.ac.getstartup()+self.s1.ac.getrecovery()
                for buff in (self.electrified,
                             self.a1_fs,
                             self.a3_att,
                             self.a3_spd):
                    buff.buff_end_timer.timing += extend
            else:
                self.dmg_make(e.name, 8.25)

    def s2_proc(self, e):
        self.electrified.on()
        self.a1_fs.on()
        self.a3_att.on()
        self.a3_spd.on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)