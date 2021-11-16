from core.advbase import *
from conf import DEFAULT


class Ramona(Adv):
    @allow_acl
    def s(self, n, s1_kind=None):
        if self.in_dform():
            return False
        if n == 1 and s1_kind == "all":
            self.current_s["s1"] = "all"
        else:
            self.current_s["s1"] = DEFAULT
        return super().s(n)


variants = {None: Ramona}
