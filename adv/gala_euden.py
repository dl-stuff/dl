from core.advbase import *

def module():
    return Gala_Euden


class Gala_Euden(Adv):
    conf = {}
    conf['acl'] = """
        `dragon, self.energy()=5
        `s2
        `s3
        `s4, cancel
        `s1, fsc and self.energy()<5
        `fs, x=3
    """
    conf['coabs'] = ['Raemond','Cleo','Peony']
    conf['share'] = ['Gala_Mym']
    conf['afflict_res.paralysis'] = 0

    def prerun(self):
        self.s2.autocharge_init(15873).on()
        if self.condition('draconic charge'):
            self.dragonform.dragon_gauge += 500
        Modifier('dragonlight_dt','dt','hecc',1/0.7-1).on()
        # self.dragonlight_spd = Spdbuff('dragonlight',0.1,-1,wide='self')
        # Event('dragon').listener(self.a3_on)
        # Event('idle').listener(self.a3_off)
        self.dragonform.shift_spd_mod = Modifier('dragonlight_spd', 'spd', 'passive', 0.10)

    # def a3_on(self, e):
    #     if not self.dragonlight_spd.get():
    #         self.dragonlight_spd.on()

    # def a3_off(self, e):
    #     if self.dragonlight_spd.get():
    #         self.dragonlight_spd.off()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
