from core.advbase import *
from core.ability import Last_Buff


class Alain(Adv):
    def prerun(self):
        Last_Buff.HEAL_TO = 50

    ### TEST ###
    conf = {"c": {}}
    conf["prefer_baseconf"] = True
    conf["slots.d"] = "Gala_Reborn_Jeanne"
    conf["c"]["a"] = [["dp", 100.0]]
    conf["acl"] = [
        "`dragon(c3-c3-c3-c3-c1-end)",
    ]

    # def post_run(self, end):
    #     print(self._acl._acl_str)
    #     print()
    #     print(core.acl.regenerate_acl(self._acl))
    #     return super().post_run(end)

    ### TEST ###


variants = {None: Alain}
