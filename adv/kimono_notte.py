from core.advbase import *
from module.template import ButterflyAdv


class Kimono_Notte(ButterflyAdv):
    conf = {}
    conf["dacl"] = [
        "`ds2, x=3",
        "`ds1, x=3",
    ]

    def prerun(self):
        self.config_butterflies()
        Listener("divinedragon", self.clear_all_butterflies).on()
        Listener("divinedragon_end", self.clear_all_butterflies).on()
        Listener("divinedragon_end", self.ds2_clear).on()
        self.ds2_butterfly_count = 1  # assuming 1 butterfly can hit boss at a time
        self.ds2_timers = []
        Listener("s", self.a1_amp).on()

    def a1_amp(self, _=None):
        if not self.is_set_cd("a1_amp", 8):
            self.add_amp(amp_id="30000", max_level=1)

    @property
    def butterflies_ds1(self):
        return self.butterflies + self.ds2_butterfly_count if self.ds2_timers else 0

    def s1_proc(self, e):
        self.clear_all_butterflies()

    def s2_proc(self, e):
        self.clear_all_butterflies()

    def ds1_proc(self, e):
        self.clear_all_butterflies()
        self.ds2_clear()

    def ds2_extra_hits(self, t):
        for m in t.actmods:
            m.on()
        for _ in range(self.ds2_butterfly_count):
            self.dmg_make(f"{t.name}_extra", 0.72)
            self.add_combo()
        for m in t.actmods:
            m.off()

    def ds2_clear(self, _=None):
        for t in self.ds2_timers:
            t.off()
        self.ds2_timers = []

    def ds2_proc(self, e):
        self.ds2_clear()
        for i in range(0, 27):
            t = Timer(self.ds2_extra_hits)
            t.name = e.name
            t.actmods = self.actmods("ds2")
            t.on(i / 2)
            self.ds2_timers.append(t)


variants = {None: Kimono_Notte}
