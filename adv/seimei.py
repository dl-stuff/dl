from core.advbase import *


class Seimei(Adv):
    def prerun(self):
        self.shikigami_t = Timer(self.shikigami_dmg, 1.05, True).off()
        self.shikigami_lv = 0
        self.shikigami_hits = 0
        self.shikigami_gauge = 100
        self.shikigami = EffectBuff("shikigami", 40, self.shikigami_on, self.shikigami_off)
        self.agauge = 0
        self.acount = 0
        o_s2_check = self.a_s_dict["s2"].check
        self.a_s_dict["s2"].check = lambda: o_s2_check() and (self.shikigami_lv > 0)
        Event("dp").listener(self.dp_shikigami_gauge)
        self.dp_count = 0

    def _add_shikigami_gauge(self, value):
        if not value:
            return
        self.shikigami_gauge = min(100, self.shikigami_gauge + value)
        # log("gauge", "shikigami", value, f"{self.shikigami_gauge}/100")
        log("shikigami", "gauge", self.shikigami_gauge)

    def dp_shikigami_gauge(self, e):
        self.dp_count += e.value
        if self.dp_count >= 100.0:
            self._add_shikigami_gauge(50)
            self.dp_count -= 100.0

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        self._add_shikigami_gauge(attr.get("cp", 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit)

    def shikigami_dmg(self, t):
        if self.in_dform() or isinstance(self.action.getdoing(), S):
            return
        if self.shikigami_lv < 2 and self.shikigami_gauge >= 6:
            self.hitattr_make("#shikigami_lv1", "#", "#", 0, self.conf.s1.shikigami.lv1)
            self.shikigami_hits += self.echo
            if self.shikigami_hits >= 15:
                self.shikigami.on(40)
                self.shikigami_lv = 2
            self._add_shikigami_gauge(-6)
        elif self.shikigami_gauge >= 4:
            self.hitattr_make("#shikigami_lv2", "#", "#", 0, self.conf.s1.shikigami.lv2)
            self._add_shikigami_gauge(-4)

    def shikigami_on(self):
        self.shikigami_t.on()
        self.shikigami_lv = 1

    def shikigami_off(self):
        self.shikigami_t.off()
        self.shikigami_lv = 0
        self.shikigami_hits = 0

    def s1_proc(self, e):
        if self.shikigami_lv < 1:
            self.shikigami.on(40)

    def s2_proc(self, e):
        Timer(lambda e: self.shikigami.off(), 0.8).on()


variants = {None: Seimei}
