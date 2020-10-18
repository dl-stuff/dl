from core.advbase import *

def module():
    return Gala_Prince


class Gala_Prince(Adv):
    conf = {}
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'The_Red_Impulse',
    'An_Ancient_Oath',
    'Entwined_Flames',
    'Dueling_Dancers'
    ]
    conf['slots.paralysis.a'] = [
    'The_Shining_Overlord',
    'Spirit_of_the_Season',
    'An_Ancient_Oath',
    'Entwined_Flames',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon, self.energy()=5
        `s2
        `s1
        `s4, cancel 
        `s3, fsc
        `fs, x=3
    """
    conf['coabs'] = ['Lucretia','Cleo','Peony']
    conf['share'] = ['Gala_Mym']
    
    def prerun(self):
        self.s2.autocharge_init(32000).on()
        if self.condition('draconic charge'):
            self.dragonform.dragon_gauge += 500
        Modifier('dragonlight_dt','dt','hecc',1/0.7-1).on()
        # self.dragonlight_spd = Spdbuff('dragonlight',0.1,-1,wide='self')
        # Event('dragon').listener(self.a3_on)
        # Event('idle').listener(self.a3_off)
        self.dragonform.shift_spd_mod = Modifier('dragonlight_spd', 'spd', 'passive', 0.10).off()

    # def a3_on(self, e):
    #     if not self.dragonlight_spd.get():
    #         self.dragonlight_spd.on()

    # def a3_off(self, e):
    #     if self.dragonlight_spd.get():
    #         self.dragonlight_spd.off()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
