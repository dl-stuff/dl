from core.advbase import *


class Humanoid_Jupiter(Adv):
    def prerun(self):
        if self.condition("s2 always counter"):
            self.current_s["s2"] = "counter"
        self.a1_hjp = Listener("dragon", self.a1_on, order=0)
        self.overcharged_params = (
            (60.0, 8.0),
            (45.0, 10.0),
            (30.0, 12.0),
            (15.0, 15.0),
        )
        self.overcharged = 0
        self.overcharged_timer = Timer(self.overcharged_EXPLODE)

    def a1_on(self, e):
        if self.dshift_count == 2:
            for act in self.dragonform.conf.values():
                try:
                    if act["attr"] and act["attr_HAS"]:
                        act["attr"] = act["attr_HAS"]
                except TypeError:
                    pass
            self.a1_hjp.off()

    def overcharged_upgrade(self, count=1):
        self.overcharged = min(self.overcharged + count, len(self.overcharged_params))
        self.overcharged_timer.on(self.overcharged_params[self.overcharged-1][0])

    def overcharged_EXPLODE(self, e):
        self.dmg_make(f"overcharged_lvl{self.overcharged}", self.overcharged_params[self.overcharged-1][1], "pursuit")
        if self.overcharged == len(self.overcharged_params):
            self.afflics.paralysis.on("overcharged", 1.1, 0.727)
            self.afflics.stun.on("overcharged", 1.0, 5.5)
        self.overcharged_timer.off()
        self.overcharged = 0
        self.dragonform.charge_dprep(20)
        self.heal_make("overcharged", 80)

    def s1_hit7(self, *args):
        self.overcharged_EXPLODE(args)

    def s2_proc(self, e):
        if e.group == "counter":
            self.overcharged_upgrade(4)
        else:
            self.overcharged_upgrade()


class Humanoid_Jupiter_DODGE(Humanoid_Jupiter):
    comment = "dodge always proc a1"

    def prerun(self):
        super().prerun()
        Event("dodge_proc").listener(self.dodge)

    def dodge_proc(self, e):
        if not self.is_set_cd("a1_dodge", 10.0):
            self.overcharged_upgrade()
            self.add_amp(max_level=1)


variants = {None: Humanoid_Jupiter, "DODGE": Humanoid_Jupiter_DODGE}
