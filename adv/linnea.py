from core.advbase import *

class Linnea(Adv):
    def prerun(self):
        for lv in range(1, 4):
            for h in range(3, lv*3+1, 3):
                setattr(self, f'fs{lv}_enhanced_hit{h}', self.a1_fs_prep)

    def a1_fs_prep(self, name, base, group, aseq):
        self.charge_p(base, 0.30, target='s1')

variants = {None: Linnea}
