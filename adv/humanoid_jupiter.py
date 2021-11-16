from core.advbase import *
from conf import DEFAULT


class Humanoid_Jupiter(Adv):
    def prerun(self):
        self.a1_hjp = Listener("dragon", self.a1_on, order=0)
        self.overcharged_time = (60.0, 45.0, 30.0, 15.0)
        self.overcharged = 0
        self.overcharged_dmg = 0
        self.overcharged_timer = Timer(self.overcharged_expire)

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
        self.overcharged = min(self.overcharged + count, len(self.overcharged_time))
        self.overcharged_dmg = self.dmg_formula("s", 15.0)
        self.overcharged_timer.on(self.overcharged_time[self.overcharged-1])

    def overcharged_expire(self, e):
        self.overcharged -= 1
        if self.overcharged > 0:
            self.overcharged_timer.on(self.overcharged_time[self.overcharged-1])

    def overcharged_EXPLODE(self):
        self.dmg_make("overcharged_EXPLODE", self.overcharged_dmg, fixed=True)
        self.afflics.paralysis.on("overcharged", 1.1, 0.727)
        self.afflics.stun.on("overcharged", 1.0, 5.5)
        self.overcharged_timer.off()
        self.overcharged_dmg = 0
        self.overcharged = 0
        self.dragonform.charge_dprep(20)
        self.heal_make("overcharged", 80)

    @allow_acl
    def s(self, n, s2_kind=None):
        if self.in_dform():
            return False
        if n == 2:
            if s2_kind in (DEFAULT, "counter"):
                self.current_s["s2"] = s2_kind
            elif self.condition("s2 always counter"):
                self.current_s["s2"] = "counter"
            else:
                self.current_s["s2"] = DEFAULT
        return super().s(n)

    def s1_hit7(self, *args):
        self.overcharged_EXPLODE()

    def s2_proc(self, e):
        if e.group == "counter":
            self.overcharged_upgrade(4)
        else:
            self.overcharged_upgrade()


class Humanoid_Jupiter_DODGE(Humanoid_Jupiter):
    comment = "dodge always proc a1"

    def prerun(self):
        super().prerun()
        Event("dodge").listener(self.dodge_proc)

    def dodge_proc(self, e):
        if not self.is_set_cd("a1_dodge", 10.0):
            self.overcharged_upgrade()
            self.add_amp(max_level=1)


variants = {None: Humanoid_Jupiter, "DODGE": Humanoid_Jupiter_DODGE}
