from core.advbase import *

ROMANCE_GAUGE_MODS = {
    "hpdef": (-0.1, -0.05, 0, 0.05, 0.10, 0.15),
    "s": (-0.1, -0.05, 0, 0.05, 0.10, 0.25),
    "affres": (0, 20, 40, 60, 80, 100),
}


class Valentines_Chelsea(Adv):
    def prerun(self):
        self.romance_sd = Modifier("romance1_sd", "s", "passive", -0.05)
        self.romance_sd.get = self.romance_sd_get
        self.romance_hp = Modifier("romance1_hp", "maxhp", "passive", -0.05)
        self.romance_hp.get = self.romance_hpdef_get
        self.romance_def = Modifier("romance1_hp", "defense", "passive", -0.05)
        self.romance_def.get = self.romance_hpdef_get
        self.romance_affres = Modifier("romance1_hp", "affres", "all", 20)
        self.romance_affres.get = self.romance_affres_get
        self.romance_gauge = 0
        Event("buffskill").listener(self.l_buffed_romance_gauge)

        self.is_cd = False
        Event("selfaff").listener(self.a2_proc)
        self.a2_buff = FSAltBuff("a2_fs", "ablaze", 8, 3)
        self.a2_spd_mod = Modifier("a2_spd", "spd", "buff", 0.15, get=self.a2_buff.get)

        self.full_gauge_at = None

    def a2_cd_end(self, t):
        self.is_cd = False

    def a2_proc(self, e):
        if not self.is_cd and e.atype == "burn":
            self.charge_p("a3", 0.25, target="s2")
            self.a2_buff.on()
            self.is_cd = True
            Timer(self.a2_cd_end).on(4.9999)

    @property
    def romance(self):
        return int(self.romance_gauge / 400)

    def add_romance_gauge(self, cp):
        gauge_before = self.romance_gauge
        if cp < 1:
            cp = Adv.sp_convert(cp, 2000)
        self.romance_gauge = min(2000, self.romance_gauge + cp)
        delta = self.romance_gauge - gauge_before
        if delta > 0:
            if self.romance_gauge >= 2000:
                self.a_s_dict["s2"].enable_phase_up = False
                self.current_s["s2"] = "romance"
                self.deferred_x = "romance"
                self.full_gauge_at = now()
            log(
                "romance",
                f"{self.romance_gauge - gauge_before:+}",
                f"{self.romance_gauge}/2000 [{self.romance}]",
            )

    def l_buffed_romance_gauge(self, e):
        # 12.5% of 500% is actually 2.5% of 100%
        self.add_romance_gauge(0.025)

    def s2_proc(self, e):
        if e.group != "romance":
            self.add_romance_gauge(400)

    def romance_sd_get(self):
        return ROMANCE_GAUGE_MODS["s"][self.romance]

    def romance_hpdef_get(self):
        return ROMANCE_GAUGE_MODS["hpdef"][self.romance]

    def romance_affres_get(self):
        return ROMANCE_GAUGE_MODS["affres"][self.romance]

    def post_run(self, end):
        if self.full_gauge_at:
            self.comment += f"full gauge at {self.full_gauge_at:.02f}s;"


variants = {None: Valentines_Chelsea}
