from core.advbase import *
from slot.a import *

def module():
    return Summer_Cleo

class Summer_Cleo(Adv):
    a1 = ('affself_paralysis_sp_passive', 0.12, 20, 5, True)
    a3 = ('k_paralysis',0.35)

    conf = {}
    conf['slots.a'] = Forest_Bonds()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, s=1
        `s3, not self.s3_buff
        `s2, s1.charged<s1.sp/3
        `s1
        `s4, cancel
        `fs,x=5
    """
    coab = ['Lucretia','Sharena','Peony']
    share = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0

    def init(self):
        random.seed()
        self.buff_class = Teambuff if self.condition('buff all team') else Selfbuff

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.buff_class = Teambuff if adv.condition('buff all team') else Selfbuff

    def s1_lantency(self, t):
        self.dmg_make(t.name,1.07)
        self.add_hits(1)
        self.afflics.paralysis(t.name,120,0.97)
        self.dmg_make(t.name,1.07)
        self.add_hits(1)
        self.dmg_make(t.name,1.07)
        self.add_hits(1)
        self.dmg_make(t.name,5.4)
        self.add_hits(1)

        for _ in range(min(self.buffcount, 5)):
            self.dmg_make(t.name,1.07)
            self.add_hits(1)

    def s1_proc(self, e):
        t = Timer(self.s1_lantency)
        t.name = e.name
        t.on(0.8333)

    def s2_proc(self, e):
        self.buff_class(e.name,0.05,10).on()
        self.buff_class(f'{e.name}_cc',0.03,10,'crit','chance').on()
        self.buff_class(f'{e.name}_sd',0.10,10,'s').on()
        self.buff_class(f'{e.name}_sp',0.10,10,'sp','passive').on()
        Selfbuff(f'{e.name}_def',0.10,10,'defense').on()
        if self.buff_class == Teambuff:
            Selfbuff(f'{e.name}_cd',0.10,10,'crit','damage').on()
            self.s1.charge(self.s1.sp)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
