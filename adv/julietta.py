from core.advbase import *
from slot.a import *

def module():
    return Julietta

juli_smash = {
    'fs_divine.dmg': 14.976
}

class Julietta(Adv):
    conf = juli_smash.copy()
    conf['slots.a'] = Valiant_Crown()+Primal_Crisis()
    conf['acl'] = """
        `dragon, self.energy()<4
        `s3, not self.s3_buff
        `s2
        `s1
        `s4, s1.charged<s1.sp/2
        `fs, x=4 and self.fs_alt.uses>0
        """
    conf['coabs'] = ['Blade','Lucretia','Peony']
    conf['share'] = ['Summer_Cleo']

    def prerun(self):
        self.fs_alt = FSAltBuff(self, fs_name='divine', uses=1)

    def s2_proc(self, e):
       Selfbuff(f'{e.name}_defense', 0.50, 10, 'defense').on()
       self.fs_alt.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
