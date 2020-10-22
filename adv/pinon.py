from core.advbase import *
from module.template import SigilAdv

class Pinon(SigilAdv):
    def fs2_proc(self, e):
        self.a_update_sigil(-13)

    def prerun(self):
        self.config_sigil(duration=300, x=True)

    def x(self):
        x_min = 1
        prev = self.action.getprev()
        if self.unlocked and isinstance(prev, X) and prev.index >= 5:
            x_min = 8
        return super().x(x_min=x_min)

    def post_run(self, end):
        if self.unlocked:
            self.comment += f'unlock at {self.unlocked:.02f}s; only s1 if energized after unlock'
        else:
            self.comment += f'not unlocked'

variants = {None: Pinon}
