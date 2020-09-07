from core.advbase import *
from slot.a import *
from module.x_alt import Fs_alt

def module():
    return Julietta

class Julietta(Adv):
    conf = {}
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
        conf_fs_alt = {'fs.dmg': 14.976}
        self.fs_alt = Fs_alt(self, conf_fs_alt)

    def s2_proc(self, e):
       Selfbuff(e.name+'_defense', 0.50, 10, 'defense').on()
       self.fs_alt.on(1)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
