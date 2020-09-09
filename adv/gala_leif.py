from core.advbase import *
from slot.d import *
from slot.a import *
from module.template import StanceAdv

def module():
    return Gala_Leif

leef_conf = {
    'x1_striking.dmg': 112 / 100.0,
    'x1_striking.sp': 152,
    'x1_striking.startup': 10 / 60.0,
    'x1_striking.recovery': 0 / 60.0,
    'x1_striking.hit': 2,

    'x2_striking.dmg': 174 / 100.0,
    'x2_striking.sp': 345,
    'x2_striking.startup': 44 / 60.0,
    'x2_striking.recovery': 0 / 60.0,
    'x2_striking.hit': 3,

    'x3_striking.dmg': 327 / 100.0,
    'x3_striking.sp': 655,
    'x3_striking.startup': 40 / 60.0,
    'x3_striking.recovery': 30 / 60.0, # needs verification
    'x3_striking.hit': 5,

    'x1_shielding.dmg': 182 / 100.0,
    'x1_shielding.sp': 400,
    'x1_shielding.startup': 16 / 60.0,
    'x1_shielding.recovery': 0 / 60.0,
    'x1_shielding.hit': 1,

    'x2_shielding.dmg': 367 / 100.0,
    'x2_shielding.sp': 600,
    'x2_shielding.startup': 56 / 60.0,
    'x2_shielding.recovery': 0 / 60.0,
    'x2_shielding.hit': 1,

    'x3_shielding.dmg': 548 / 100.0,
    'x3_shielding.sp': 800,
    'x3_shielding.startup': 76 / 60.0,
    'x3_shielding.recovery': 30 / 60.0, # needs verification
    'x3_shielding.hit': 1,
}

class Gala_Leif(StanceAdv):
    conf = leef_conf.copy()
    conf['slots.a'] = The_Shining_Overlord()+The_Fires_of_Hate()
    conf['slots.d'] = Vayu()
    conf['acl'] = """
        `dragon(c3-s-end),fsc
        `s3, not buff(s3)
        `s4, afflics.poison.get()
        if s2.check()
        `s2(shielding)
        else
        `s1(striking)
        end
        `fs, x=3
        """
    conf['coabs'] = ['Dragonyule_Xainfried', 'Blade', 'Lin_You']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0
    
    def prerun(self):
        self.config_stances({
            'striking': ModeManager(self, 'striking', x=True, s1=True, s2=True),
            'shielding': ModeManager(self, 'shielding', x=True, s1=True, s2=True),
        }, hit_threshold=5)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)