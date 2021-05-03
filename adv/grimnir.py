from core.advbase import *


class Grimnir(Adv):
    def prerun(self):
        self.brewing_storm = MultiLevelBuff(
            "brewing_storm",
            [
                Selfbuff(f"brewing_storm_lv{lv+1}", buffvalue, 60, "ex", "actdown", source="a1")
                for lv, buffvalue in enumerate((0.15, 0.20, 0.25, 0.30, 0.50))
            ],
        )
        self.ahits = 0
        self.slayed = 0
        Event("slayed").listener(self.slayer_brewing_storm)
        self.vortex = Timer(self.a3_vortex, 3.0, True)
        self.lv5_time = None

    def upgrade_brewing_storm(self):
        self.brewing_storm.on()
        if self.lv5_time is None and self.brewing_storm.level == 5:
            self.vortex.on()
            self.current_s["s1"] = "storm5"
            self.lv5_time = now()

    def a3_vortex(self, t):
        if self.brewing_storm.level >= 5:
            self.dmg_make("#vortex", 0.8, "#")
            self.add_combo()

    def slayer_brewing_storm(self, e):
        self.slayed += e.count
        while self.slayed >= 5:
            self.slayed -= 5
            self.upgrade_brewing_storm()

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        if self.condition("always connect hits"):
            a_hits = self.hits // 100
            if a_hits > 0 and a_hits != self.ahits:
                self.ahits = a_hits
                self.upgrade_brewing_storm()
        return result

    def post_run(self, end):
        if self.lv5_time is not None:
            self.comment += f"lv5 storm at {self.lv5_time:.02f}s"


variants = {None: Grimnir}
