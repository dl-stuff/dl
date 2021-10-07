from core.advbase import *
from module.bleed import Bleed


class Ieyasu(Adv):
    ### TEST ###
    conf = {"c": {}}
    conf["prefer_baseconf"] = True
    conf["slots.d"] = "Gala_Bahamut"
    conf["c"]["a"] = [["dp", 100.0]]
    conf["dacl"] = ["`ds1, ds1.overcharge=2"]
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

    def s2_ifbleed(self):
        if self.bleed_stack > 0:
            return self.s2_buff.get()
        return 0

    def prerun(self):
        self.s2_buff = Selfbuff("s2", 0.20, 15, "crit")
        self.s2_buff.modifier.get = self.s2_ifbleed

    def s2_proc(self, e):
        if self.nihilism:
            return
        self.s2_buff.on()


variants = {None: Ieyasu}
