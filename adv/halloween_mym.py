from core.advbase import *

def module():
    return Halloween_Mym

class Halloween_Mym(Adv):
    conf = {}
    conf['slots.a'] = [
    'Kung_Fu_Masters',
    'An_Ancient_Oath',
    'The_Red_Impulse',
    'Entwined_Flames',
    'Dueling_Dancers'
    ]
    conf['slots.burn.a'] = [
    'Kung_Fu_Masters',
    'Dragon_and_Tamer',
    'Me_and_My_Bestie',
    'Entwined_Flames',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon, s
        `s3, not buff(s3)
        `s4
        `s1
        `s2, cancel
        `fsf, x=4 and (s1.charged=self.sp_val(4))
    """
    conf['coabs'] = ['Yuya', 'Dagger2', 'Serena']
    conf['share'] = ['Gala_Mym']

    # conf['dragonform'] = {
    #     'act': 'c3-s',

    #     'dx1.dmg': 2.20,
    #     'dx1.startup': 15 / 60.0 = 0.25, # c1 frames
    #     'dx1.hit': 1,

    #     'dx2.dmg': 3.30,
    #     'dx2.startup': 44 / 60.0 = 0.73333333333333333333, # c2 frames
    #     'dx2.hit': 1,

    #     'dx3.dmg': 3.74*2,
    #     'dx3.startup': (38+24) / 60.0 = 1.0333333333333333333, # c3 frames
    #     'dx3.recovery': 54 / 60.0 = 0.9, # recovery
    #     'dx3.hit': 2,

    #     'ds.dmg': 12.32,
    #     'ds.recovery': 178 / 60 = , # skill frames
    #     'ds.hit': 8,

    #     'dodge.startup': 41 / 60.0, # dodge frames
    # }

    # def ds_proc(self):
    #     return self.dmg_make('ds',self.dragonform.conf.ds.dmg,'s')

    def prerun(self):
        self.a3_da = Selfbuff('a3_dreamboost',0.20,15,'da','passive')
        self.dragonform.shift_spd_mod = Modifier('flamewyrm_spd', 'spd', 'passive', 0.15).off()

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.a3_da = Dummy()

    def s2_proc(self, e):
        self.a3_da.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)