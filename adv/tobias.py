from core.advbase import *
from module.x_alt import X_alt

def module():
    return Tobias


class TobiasXAlt(XAltBuff):
    def enable_x(self, enabled):
        super().enable_x(enabled)
        try:
            self.adv.a_fs_dict['default'].set_enabled(not enabled)
            self.adv.a_dodge.enabled = not enabled
        except (KeyError, AttributeError):
            pass

class Tobias(Adv):
    comment = 'c5fs, no s2, s!cleo ss after s1'

    conf = {}
    conf['slots.a'] = [
        'A_Dogs_Day',
        'Study_Rabbits',
        'Castle_Cheer_Corps',
        'From_Whence_He_Comes',
        'Bellathorna'
    ]
    conf['slots.d'] = 'Freyja'
    conf['acl'] = """
        `s1
        `s3
        `s4, fsc
        `fs, xf=5
    """
    conf['coabs'] = ['Bow','Blade','Dagger2']
    conf['share'] = ['Dragonyule_Xainfried', 'Templar_Hope']

    def prerun(self):
        self.s1.autocharge_init(85)
        self.s2.charge(1) # 1 sp/s regen
        self.s2_x_alt = TobiasXAlt(group='sacred')
        self.s2_sp_buff = EffectBuff('sacred_blade', 10, lambda: self.s1.autocharge_timer.on(), lambda: self.s1.autocharge_timer.off())

    def s2_proc(self, e):
        if e.group == 'enhanced':
            self.s2_x_alt.on(10)
            self.s2_sp_buff.on(7)
        else:
            self.s2_x_alt.off()
            self.s2_sp_buff.off()
        self.s2.charge(1) # 1 sp/s regen

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)