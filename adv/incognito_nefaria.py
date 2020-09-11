from core.advbase import *
from slot.a import *
from slot.d import *
from module.template import RngCritAdv

def module():
    return Incognito_Nefaria

class Incognito_Nefaria(RngCritAdv):
    # need to confirm s1 hits and s2 frames
    conf = {}
    conf['slots.a'] = Candy_Couriers()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon(c3-s-s-end),s
        `s3, not buff(s3) and x=5
        `s1
        `s2
        `s4,cancel
        `s2,x=5
        """
    conf['slots.d'] = Gala_Mars()
    conf['coabs'] = ['Blade', 'Marth', 'Dagger']
    conf['share'] = ['Kleimann']
    conf['afflict_res.burn'] = 0

    def prerun(self):
        self.config_rngcrit(cd=7)
        self.crit_count = 0

    def rngcrit_cb(self):
        Selfbuff('a1', 0.20, 20, 'crit', 'damage').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
