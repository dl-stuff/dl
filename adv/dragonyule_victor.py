from core.advbase import *


class Dragonyule_Victor(Adv):
    def s2_proc(self, e):
        for aseq in range(self.zonecount):
            self.hitattr_make(
                e.name, e.base, e.group, aseq + 1, self.conf[e.name].extra_self
            )


variants = {None: Dragonyule_Victor}
