from core.advbase import *
from core.ability import Last_Buff


class Alain(Adv):
    def prerun(self):
        Last_Buff.HEAL_TO = 50

    ### TEST ###
    conf = {"c": {}}
    conf["prefer_baseconf"] = True
    conf["slots.d"] = "Gala_Reborn_Agni"
    conf["c"]["a"] = [["dp", 100.0]]
    conf["acl"] = [
        "`dragon(c2-s-c2-c2-c2-end)",
    ]

    # def post_run(self, end):
    #     print(self._acl._acl_str)
    #     print()
    #     print(core.acl.regenerate_acl(self._acl))
    #     return super().post_run(end)

    ### TEST ###


variants = {None: Alain}
