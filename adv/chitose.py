from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Chitose

class Chitose(Adv):
    a3 = ('a',-0.1)

    conf = {}
    conf['slots.a'] = A_Game_of_Cat_and_Boar()+Castle_Cheer_Corps()
    conf['slots.paralysis.a'] = conf['slots.a']
    conf['slots.d'] = Tie_Shan_Gongzhu()
    conf['acl'] = """
        `fs, self.fs_prep_c>0 and x=5
        `s1
        `s4, s=1
        `s3, cancel and x!=1
        """
    conf['coabs'] = ['Tobias','Dagger2','Bow']
    conf['share'] = ['Summer_Luca','Summer_Cleo']

    def init(self):
        self.buff_class = Teambuff if self.condition('buff all team') else Selfbuff

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.buff_class = Dummy if adv.slots.c.ele != 'light' else Teambuff if adv.condition('buff all team') else Selfbuff

    def s1_proc(self, e):
        self.buff_class(e.name,0.25,15).on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)