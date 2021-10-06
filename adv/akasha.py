from core.advbase import *
from module.template import LowerMCAdv


class Akasha(Adv):

    ### TEST ###
    conf = {"c": {}}
    conf["prefer_baseconf"] = True
    conf["slots.d"] = "Gala_Beast_Volk"
    conf["c"]["a"] = [["dp", 100.0]]
    conf["dacl"] = [
        "`x, fsc and moonlit_rage>=9",
        "`ds1, blood_moon=0",
        "`fst(8), blood_moon=1",
    ]
    conf["acl"] = [
        "`dragon",
        "`s1",
        "`s2",
        "`s3, not buff(s3)",
        "`s4",
    ]

    # def post_run(self, end):
    #     print(self._acl._acl_str)
    #     print()
    #     print(core.acl.regenerate_acl(self._acl))
    #     return super().post_run(end)

    ### TEST ###

    def prerun(self):
        super().prerun()
        Event("s").listener(self.a1_amp)
        Event("ds").listener(self.a1_amp)

    def a1_amp(self, e):
        if not self.is_set_cd("a1_amp", 30):
            self.add_amp(max_level=2)


variants = {None: Akasha, "50MC": LowerMCAdv}
