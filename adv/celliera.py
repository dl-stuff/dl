from core.advbase import *

class Celliera(Adv):
    def s2_proc(self, e):
        if e.group == 'enhanced':
            self.dragonform.disabled = False
        else:
            self.dragonform.disabled = True

    def fs_enhanced_proc(self, e):
        self.dragonform.disabled = False

variants = {None: Celliera}
