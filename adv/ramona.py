from core.advbase import *


class Ramona(Adv):
    @allow_acl
    def s(self, n, s1_kind=None):
        if n == 1 and s1_kind == "all":
            self.current_s["s1"] = "all"
        else:
            self.current_s["s1"] = "default"
        return super().s(n)


variants = {None: Ramona}
