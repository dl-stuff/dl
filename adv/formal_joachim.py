from core.advbase import *
from conf import DEFAULT


class Formal_Joachim(Adv):
    @allow_acl
    def s(self, n):
        if self.in_dform():
            return False
        if n == 1:
            if self.action.getdoing() is self.a_s_dict["s2"].ac:
                self.current_s["s1"] = "from2"
            else:
                self.current_s["s1"] = DEFAULT
        return super().s(n)


variants = {None: Formal_Joachim}
