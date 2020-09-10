from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Nobunaga

class Nobunaga(Adv):
    a1 = ('a',0.2,'hit15')

    conf = {}
    conf['slots.a'] = The_Wyrmclan_Duo()+Primal_Crisis()
    conf['slots.burn.a'] = Resounding_Rendition()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s=2
        `s3, not self.s3_buff
        `s4, cancel
        `s1
        `s2, self.burning_ambition
        `fs, x=5 and s2.charged<s2.sp-self.sp_val(2)
        """
    conf['coabs'] = ['Wand','Marth','Yuya']
    conf['share'] = ['Summer_Patia']

    def prerun(self):
        self.burning_ambition = 0
        self.ba_t = Timer(self.ba_proc)
    
    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.burning_ambition = 0
        adv.rebind_function(Nobunaga, 'ba_proc')
        adv.ba_t = Timer(adv.ba_proc)

    def s1_proc(self, e):
        self.burning_ambition = self.dmg_formula('s', 11.18)
        self.ba_t.name = e.name
        self.ba_t.on(30)

    def ba_proc(self, t):
        if self.burning_ambition > 0:
            self.dmg_make('s1_burning_ambition', self.burning_ambition, fixed=True)
            self.burning_ambition = 0
            self.ba_t.off()
            return True
        return False

    def s2_proc(self, e):
        if self.ba_proc(e):
            self.dmg_make(f'{e.name}_boost',self.conf[e.name].dmg*0.3)

    def fs_proc(self, e):
        self.ba_proc(e)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)