from core.advbase import *


class Formal_Joachim(Adv):
    @allow_acl
    def s(self, n):
        if n == 1:
            if self.action.getdoing() is self.a_s_dict["s2"].ac:
                self.current_s["s1"] = "from2"
            else:
                self.current_s["s1"] = "default"
        return super().s(n)


variants = {None: Formal_Joachim}
