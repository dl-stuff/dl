from core.advbase import *
from module.template import RngCritAdv

def module():
    return Incognito_Nefaria

class Incognito_Nefaria(RngCritAdv):
    comment = 'no s2; using s2 is dps loss'
    conf = {}
    conf['slots.a'] = [
    'Candy_Couriers',
    'Flash_of_Genius',
    'The_Red_Impulse',
    'His_Clever_Brother',
    'Dueling_Dancers'
    ]
    conf['slots.burn.a'] = [
    'Candy_Couriers',
    'Flash_of_Genius',
    'Me_and_My_Bestie',
    'His_Clever_Brother',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon, s=1 and energy()<5
        `s3, not buff(s3) and x=5
        `s4, energy()=5 and fsc
        `s1
        `fs, x=5
        `dodge, fsc
        
        ## S2 mode
        #`dragon(c3-s-s-end), (s=1 and energy()=3) or s=2
        #`s3, not buff(s3) and x=5
        #`s2, energy()=5
        #`s1, not energy()=5
        #`s4, not energy()=5 and x>3
        """
    conf['slots.d'] = 'Gala_Mars'
    conf['coabs'] = ['Blade', 'Serena', 'Yuya']
    conf['share'] = ['Xander']
    conf['afflict_res.burn'] = 0

    def prerun(self):
        self.config_rngcrit(cd=7, ev=20)
        self.a1_buff = Selfbuff('a1', 0, 20, 'crit', 'damage')
        self.a1_stack = 0

    def rngcrit_cb(self, mrate=None):
        self.a1_buff.set(0.20*mrate)
        self.a1_buff.on()
        self.a1_stack = mrate - 1

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a1_stack

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
