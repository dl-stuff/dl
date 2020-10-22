from core.advbase import *
from module.template import StanceAdv

class Lazry(StanceAdv):
    def prerun(self):
        self.config_stances({
            'low': ModeManager(group='low', s1=True, s2=True),
            'high': ModeManager(group='high', s1=True, s2=True)
        }, hit_threshold=0)

variants = {None: Lazry}
