from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import X_alt
import wep.wand

def module():
    return Lily

cp_auto_conf = {
    'x1_cp.attr': [{'dmg': 1.27075, "sp": 130, "killer": [0.3, ["frostbite"]]}],
    'x2_cp.attr': [{'dmg': 0.68425, "sp": 200, "killer": [0.3, ["frostbite"]]}, 2],
    'x3_cp.attr': [{'dmg': 0.46, "sp": 240, "killer": [0.3, ["frostbite"]]}, 3],
    'x4_cp.attr': [{'dmg': 0.94875, "sp": 430, "killer": [0.3, ["frostbite"]]}, 2],
    'x5_cp.attr': [{'dmg': 0.759, "sp": 600, "killer": [0.3, ["frostbite"]]}, {'dmg': 0.46, "killer": [0.3, ["frostbite"]]}, 4],
}

# C1: 1x 127.075%
# C2: 136.85%
# C3: 3x 46%
# C4: 2x 94.875%
# C5: 1x 75.9% + 4x 46%
# 75.9+46*4

class Lily(Adv):
    conf = cp_auto_conf.copy()
    comment = 's1 for freeze/frostbite only'
    conf['slots.a'] = Candy_Couriers()+His_Clever_Brother()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end), s
        `s3
        `s4
        `s2, cancel
        `s1, x=5
    """
    conf['coabs'] = ['Blade', 'Renee', 'Summer_Celliera']
    conf['share'] = ['Gala_Elisanne', 'Eugene']

    def prerun(self):
        self.crystalian_princess = XAltBuff('cp')

    def s2_proc(self, e):
        self.crystalian_princess.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
