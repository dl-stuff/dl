from core.advbase import *
from slot.a import *
from module.x_alt import Fs_alt

def module():
    return Julietta

class Julietta(Adv):
    conf = {}
    conf['slots.a'] = Valiant_Crown()+Breakfast_at_Valerios()
    conf['acl'] = """
        `dragon
        `s1
        `s2
        `s3
        `s4
        `fs, x=4 and self.fs_alt.uses>0
        """
    coab = ['Blade','Dagger','Peony']
    share = ['Ranzal','Kleimann']

    def prerun(self):
        conf_fs_alt = {'fs.dmg': 14.976}
        self.fs_alt = Fs_alt(self, Conf(conf_fs_alt))

    def s2_proc(self, e):
       Selfbuff(e.name+'_defense', 0.50, 10, 'defense').on()
       self.fs_alt.on(1)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
