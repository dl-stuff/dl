from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import X_alt

def module():
    return Tobias

# C1: 1x 73% Damage + 80 SP
# C2: 2x 82% Damage + 80 SP
# C3: 2x 88% Damage + 138 SP
# C4: 2x 90% Damage + 226 SP
# C5: 2x 97% Damage + 415 SP

# s2,88,,
# s2,190,102,1.7
# x1_sacred,210,20,0.333333333
# x2_sacred,223,13,0.216666667
# x2_sacred,237,14,0.233333333
# x3_sacred,253,16,0.266666667
# x3_sacred,267,14,0.233333333
# x4_sacred,283,16,0.266666667
# x4_sacred,298,15,0.25
# x5_sacred,314,16,0.266666667
# x5_sacred,328,14,0.233333333
# x1_sacred,359,31,0.516666667
# x2_sacred,374,15,0.25
# x2_sacred,388,14,0.233333333
# x3_sacred,404,16,0.266666667
# x3_sacred,418,14,0.233333333
# x4_sacred,435,17,0.283333333
# x4_sacred,449,14,0.233333333
# x5_sacred,464,15,0.25
# x5_sacred,479,15,0.25
# x1_sacred,509,30,0.5


sacred_blade_conf = {
    'x1_sacred.dmg': 73 / 100.0,
    'x1_sacred.sp': 80,
    'x1_sacred.startup': 20 / 60.0,
    'x1_sacred.recovery': 30 / 60.0,
    'x1_sacred.hit': 1,

    'x2_sacred.dmg': 164 / 100.0,
    'x2_sacred.sp': 80,
    'x2_sacred.startup': 0,
    'x2_sacred.recovery': 30 / 60.0,
    'x2_sacred.hit': 2,

    'x3_sacred.dmg': 176 / 100.0,
    'x3_sacred.sp': 138,
    'x3_sacred.startup': 0,
    'x3_sacred.recovery': 30 / 60.0,
    'x3_sacred.hit': 2,

    'x4_sacred.dmg': 180 / 100.0,
    'x4_sacred.sp': 226,
    'x4_sacred.startup': 0,
    'x4_sacred.recovery': 30 / 60.0,
    'x4_sacred.hit': 2,

    'x5_sacred.dmg': 194 / 100.0,
    'x5_sacred.sp': 415,
    'x5_sacred.startup': 0,
    'x5_sacred.recovery': 10 / 60.0,
    'x5_sacred.hit': 2,
}


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

    conf = sacred_blade_conf
    conf['slots.a'] = A_Dogs_Day()+Castle_Cheer_Corps()
    conf['slots.poison.a'] = conf['slots.a']
    conf['slots.d'] = Freyja()
    conf['acl'] = """
        `s1
        `s3
        `s4, s
        `fs, x=5
    """
    conf['coabs'] = ['Bow','Blade','Dagger2']
    conf['share'] = ['Summer_Luca', 'Summer_Cleo']

    def prerun(self):
        self.s1.autocharge_init(85)
        self.s2.charge(1) # 1 sp/s regen
        self.s2_x_alt = TobiasXAlt('sacred')
        self.s2_sp_buff = EffectBuff('sacred_blade', 10, lambda: self.s1.autocharge_timer.on(), lambda: self.s1.autocharge_timer.off())

    def s2_proc(self, e):
        if e.phase == 0:
            self.s2_x_alt.on(10)
            self.s2_sp_buff.on(7)
        else:
            self.s2_x_alt.on()
            self.s2_sp_buff.off()
        self.s2.charge(1) # 1 sp/s regen

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)