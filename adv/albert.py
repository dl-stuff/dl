from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Albert

class Albert(Adv):
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Spirit_of_the_Season()
    conf['acl'] = """
        if electrified
        `s1
        `s3, fsc
        if x=3
        `fs2, not afflics.paralysis.get()
        `fs1
        end
        else
        `dragon, cancel
        `s2, sp_in(2, s1)
        `s1, cancel
        `s3, cancel
        `s4, cancel
        end
        """
    conf['coabs'] = ['Blade','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0

    def prerun(self):
        self.s2.autocharge_init(self.s2_autocharge).on()

    @property
    def electrified(self):
        return self.buff('s2')

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.electrified = dummy_function

    def s2_autocharge(self, t):
        if not self.electrified:
            log('s2', 4480)
            self.s2.charge(4480)

    def fs_proc(self, e):
        self.s2.charge(-8000)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)