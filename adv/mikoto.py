from core.advbase import *
from module.template import RngCritAdv

def module():
    return Mikoto

class Mikoto(RngCritAdv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['slots.burn.a'] = ['Resounding_Rendition', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon, s=2 
        queue prep
        `s2;s4;s1
        end
        `s3, not buff(s3)
        `s4
        `s1, cancel
        `s2, x=5
        """
    conf['coabs'] = ['Halloween_Mym', 'Dagger', 'Marth']
    conf['share'] = ['Kleimann']

    def prerun(self):
        self.config_rngcrit(cd=15, ev=20)
        self.a1_stack = 0

    def charge(self, name, sp, target=None):
        sp_s1 = self.sp_convert(self.sp_mod(name) + 0.1*self.a1_stack, sp)
        sp = self.sp_convert(self.sp_mod(name), sp)
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            if s == self.s1:
                s.charge(sp_s1)
            else:
                s.charge(sp)
        self.think_pin('sp')
        log('sp', name if not target else f'{name}_{target}', sp, ', '.join([f'{s.charged}/{s.sp}' for s in self.skills]))

    def rngcrit_cb(self, mrate=None):
        self.a1_stack = mrate

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a1_stack

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
