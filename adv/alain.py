from core.advbase import *
from core.ability import Last_Buff


class Alain(Adv):
    def prerun(self):
        Last_Buff.HEAL_TO = 50

    ### TEST ###
    conf = {"c": {}}
    conf["prefer_baseconf"] = True
    conf["slots.d"] = "Gala_Mars"
    conf["c"]["a"] = [["dp", 100.0]]
    conf["acl"] = [
        "`dragon(c3-s-c3-c3-c3-end), s=1 and buff(s2) and dshift_count=0",
        "`dragon(c3-s-c3-end), s=1 and buff(s2) and dshift_count=1",
        "`s3, not buff(s3) or duration-now<=2.4",
        "`s2, charged_in(5, s1)",
        "`s1",
        "`s4, xf or fsc",
        "`fs, (charged_in(fs, s1) or charged_in(fs, s4)) and xf>1",
        "`fsf, xf=5",
    ]

    # def post_run(self, end):
    #     print(self._acl._acl_str)
    #     print()
    #     print(core.acl.regenerate_acl(self._acl))
    #     return super().post_run(end)

    ### TEST ###


variants = {None: Alain}
