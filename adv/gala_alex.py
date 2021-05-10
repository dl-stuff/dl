from core.advbase import *


class Skill_Reservoir(Skill):
    def __init__(self, name=None, altchain=None):
        super().__init__(name)
        self.chain_timer = Timer(self.chain_off)
        self.chain_status = 0
        self.altchain = altchain or "base"

    def chain_on(self, skill, timeout=3):
        timeout += self.ac.getrecovery()
        self.chain_status = skill
        self.chain_timer.on(timeout)
        log("skill_chain", f"s{skill}", timeout)
        self._static.current_s[f"s{skill}"] = f"chain{skill}"
        self._static.current_s[f"s{3-skill}"] = f"{self.altchain}{3-skill}"

    def chain_off(self, t=None, reason="timeout"):
        log("skill_chain", "chain off", reason)
        self.chain_status = 0
        self._static.current_s["s1"] = "base1"
        self._static.current_s["s2"] = "base2"

    @property
    def sp(self):
        return 1129

    def charge(self, sp):
        self.charged = min(self.sp * 3, self.charged + sp)
        if self.charged >= self.sp * 3:
            self.skill_charged()

    @property
    def count(self):
        return self.charged // self.sp

    def __call__(self, call=1):
        self.name = f"s{call}"
        casted = super().__call__()
        if casted:
            if self.count == 0 and self.chain_timer.online:
                self.chain_timer.off()
                self.chain_off(reason="reservoir below 1")
            else:
                self.chain_on(call)
        return casted


class Gala_Alex(Adv):
    comment = "see special for bk chain"

    def __init__(self, altchain=None, **kwargs):
        super().__init__(**kwargs)
        self.sr = Skill_Reservoir("s1", altchain=altchain)
        self.a_s_dict["s1"] = self.sr
        self.a_s_dict["s2"] = self.sr

    def prerun(self):
        self.current_s["s1"] = "base1"
        self.current_s["s2"] = "base2"
        self.sr.enable_phase_up = False

    @allow_acl
    def s(self, n):
        sn = f"s{n}"
        if n == 1 or n == 2:
            return self.a_s_dict[sn](call=n)
        else:
            return self.a_s_dict[sn]()

    @property
    def skills(self):
        return (self.sr, self.s3, self.s4)

    def charge_p(self, name, percent, target=None, no_autocharge=False):
        percent = percent / 100 if percent > 1 else percent
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            if no_autocharge and hasattr(s, "autocharge_timer"):
                continue
            s.charge(self.sp_convert(percent, s.sp))
        log(
            "sp",
            name if not target else f"{name}->{target}",
            f"{percent*100:.0f}%",
            f"{self.sr.charged}/{self.sr.sp} ({self.sr.count}), {self.s3.charged}/{self.s3.sp}, {self.s4.charged}/{self.s4.sp}",
        )
        self.think_pin("prep")

    def charge(self, name, sp, target=None):
        sp = self.sp_convert(self.sp_mod(name), sp)
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            s.charge(sp)
        log(
            "sp",
            name,
            sp,
            f"{self.sr.charged}/{self.sr.sp} ({self.sr.count}), {self.s3.charged}/{self.s3.sp}, {self.s4.charged}/{self.s4.sp}",
        )
        self.think_pin("sp")


class Gala_Alex_70MC(Gala_Alex):
    SAVE_VARIANT = False
    comment = "70MC"
    conf = {
        "c": {
            "name": "Gala Alex",
            "icon": "100005_02_r05",
            "att": 606,
            "hp": 902,
            "ele": "shadow",
            "wt": "sword",
            "spiral": True,
            "a": [
                ["k_debuff_def", 0.3],
                ["resself_blind_att", 0.15, 10.0, 15.0],
                ["resself_paralysis_att", 0.15, 10.0, 15.0],
                ["affres_blind", 100.0],
                ["affres_paralysis", 100.0],
                ["k_poison", 0.3],
                ["edge_poison", 30.0],
            ],
        },
        "s1_dispel1": {
            "attr": [
                {"dmg": 2.02, "iv": 0.16667},
                {"dispel": 100, "iv": 0.16667},
                {"dmg": 2.02, "iv": 0.36667},
                {"dmg": 2.02, "iv": 0.6},
                {"dmg": 4.95, "killer": [0.1, ["debuff_def"]], "iv": 1.0, "msl": 0.33333},
            ],
        },
        "s1_break1": {
            "attr": [
                {"dmg": 2.45, "killer": [0.5, ["break"]], "iv": 0.16667},
                {"dmg": 2.45, "killer": [0.5, ["break"]], "iv": 0.36667},
                {"dmg": 2.45, "killer": [0.5, ["break"]], "iv": 0.6},
                {"dmg": 6.68, "killer": [0.5, ["break"]], "iv": 1.0, "msl": 0.33333},
            ],
        },
        "s2_dispel2": {
            "attr": [{"dmg": 5.53, "iv": 0.46667, "msl": 0.06667}, {"dispel": 100, "iv": 0.46667, "msl": 0.06667}, {"dmg": 4.52, "killer": [0.1, ["poison"]], "iv": 1.3, "msl": 0.06667}],
        },
        "s2_break2": {
            "attr": [{"dmg": 6.58, "killer": [0.5, ["break"]], "iv": 0.46667, "msl": 0.06667}, {"dmg": 6.58, "killer": [0.5, ["break"]], "iv": 1.3, "msl": 0.06667}],
        },
        "x1": {"attr": [{"dmg": 1.03, "sp": 150}]},
        "x2": {"attr": [{"dmg": 1.11, "sp": 150}]},
        "x3": {"attr": [{"dmg": 1.31, "sp": 196}]},
        "x4": {"attr": [{"dmg": 1.39, "sp": 265}]},
        "x5": {"attr": [{"dmg": 2.08, "sp": 391}]},
    }


class Gala_Alex_BK(Gala_Alex):
    conf = {}
    conf["prefer_baseconf"] = True
    conf["slots.a"] = [
        "A_Man_Unchanging",
        "Memory_of_a_Friend",
        "The_Shining_Overlord",
        "The_Queen_of_the_Knife",
        "The_Warrioresses",
    ]
    conf["coabs"] = ["Ieyasu", "Delphi", "Wand"]
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


variants = {None: Gala_Alex, "BK": Gala_Alex_BK, "70MC": Gala_Alex_70MC}
