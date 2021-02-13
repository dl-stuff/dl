from core.advbase import *


class Formal_Joachim(Adv):
    def prerun(self):
        self.a_s_dict["s1"].act_dict["from2"].atype = "s1"

    def cast_s1_from_s2(self, t=None):
        self.current_s["s1"] = "from2"
        self.a_s_dict["s1"].ac.atype = "s1"
        result = self.a_s_dict["s1"]()
        return result

    def s1_proc(self, e):
        self.current_s["s1"] = "default"

    @allow_acl
    def s(self, n):
        if n == 1:
            doing = self.action.getdoing()
            try:
                timing = doing.can_cancel("s1")
                if timing is not None:
                    if timing > 0:
                        Timer(self.cast_s1_from_s2).on(timing)
                        return False
                    else:
                        return self.cast_s1_from_s2()
            except AttributeError:
                pass
        return super().s(n)


variants = {None: Formal_Joachim}
