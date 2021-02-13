from core.advbase import *


class Albert(Adv):
    def prerun(self):
        self.s2.autocharge_init(self.s2_autocharge).on()

    @property
    def electrified(self):
        return self.buff("s2")

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.electrified = dummy_function

    def s2_autocharge(self, t):
        if not self.electrified:
            log("s2", 4480)
            self.s2.charge(4480)

    def fs_proc(self, e):
        self.s2.charge(-8000)


variants = {None: Albert}
