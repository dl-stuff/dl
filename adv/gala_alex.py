from core.advbase import *
from module.template import LowerMCAdv, SkillChainAdv


class Gala_Alex(SkillChainAdv):
    comment = "see special for bk chain"

    def prerun(self):
        super().prerun()
        Event("buff").listener(self.l_debuff_amp)

    def l_debuff_amp(self, e):
        if isinstance(e.buff, Debuff) and e.buff.mod_type in ("def", "defb") and not self.is_set_cd("a1", 30):
            self.add_amp(max_level=3)


class Gala_Alex_BK(Gala_Alex):
    conf = {}
    conf["prefer_baseconf"] = True
    conf["slots.a"] = [
        "A_Man_Unchanging",
        "Memory_of_a_Friend",
        "Moonlight_Party",
        "The_Queen_of_the_Knife",
        "A_Small_Courage",
        "Crown_of_Light",
        "Savage_Hawk_Bow",
    ]
    conf["coabs"] = ["Ieyasu", "Delphi", "Vania"]
    conf["share"] = ["Sha_Wujing"]
    # conf["sim_afflict.poison"] = 1

    def __init__(self, **kwargs):
        super().__init__(altchain="break", **kwargs)
        if "poison" in self.sim_afflict:
            self.conf.acl = """
                queue
                `s1; fs, x=4
                `s2; fs, x=4
                `s1;
                `s2;
                `s1;
                end
            """
            self.bk_chain = "s1 s2 s1 s2 s1"
        else:
            self.conf.acl = """
                queue
                `s2; fs, x=4;
                `s1; fs, x=4;
                `s2;
                `s1;
                `s2;
                end
            """
            self.bk_chain = "s2 s1 s2 s1 s2"

    def prerun(self):
        super().prerun()
        self.duration = 10
        self.sr.charged = 1129 * 3
        Selfbuff("agito_s3_spd", 0.30, -1, "spd", "buff").on()
        Selfbuff("agito_s3_crit", 0.05, -1, "crit", "chance").on()
        # EchoBuff("dylily_s4_echo", 0.4, 30).on()
        # Selfbuff("dylily_s4_att", 0.15, 60, "att", "buff").on()
        Debuff("sha_s4_defdown", -0.15, 10, 1, "defb").on()
        self.hits = 100

    def post_run(self, end):
        self.comment = f"{now():.02f}s sim; {self.bk_chain} on bk; no bk def adjustment"

    def build_rates(self, as_list=True):
        rates = super().build_rates(as_list=False)
        rates["break"] = 1.00
        # rates["debuff_def"] = 1.00
        # rates["poison"] = 1.00
        return rates if not as_list else list(rates.items())


class Gala_Alex_50MC(SkillChainAdv, LowerMCAdv):
    pass


variants = {None: Gala_Alex, "BK": Gala_Alex_BK, "50MC": Gala_Alex_50MC}
