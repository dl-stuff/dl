from conf import DEFAULT
from core.advbase import *


class Halloween_Sylas(Adv):
    comment = "s2 always maxhp buff; proc a3 by s2 only"

    def prerun(self):
        self.sample_buffs = {
            "x": Selfbuff("sample_x", 1.0, -1, "effect", "buff"),
            "fs": Selfbuff("sample_fs", 1.0, -1, "effect", "buff"),
            "dash": Selfbuff("sample_dash", 1.0, -1, "effect", "buff"),
        }
        Listener("x", self.add_sample)
        Listener("fs", self.add_sample)
        Listener("dash", self.add_sample)
        Listener("s", self.reset_samples)
        Listener("s", self.a3_proc)
        self.a3_buff = Selfbuff("a3_shadow_att", 0.2, -1, "shadow", "ele")

    @allow_acl
    def sample(self, key):
        return self.sample_buffs[key].get()

    @property
    def all_samples(self):
        return all((b.get() for b in self.sample_buffs.values()))

    def add_sample(self, e):
        if e.name[0] == "x":
            self.sample_buffs["x"].on()
        else:
            try:
                self.sample_buffs[e.name].on()
            except KeyError:
                return
        if self.all_samples:
            self.current_s["s1"] = "enhanced"
            self.current_s["s2"] = "enhanced"

    def reset_samples(self, e):
        if e.name in ("s1_enhanced", "s2_enhanced"):
            for b in self.sample_buffs.values():
                b.off()
            self.current_s["s1"] = DEFAULT
            self.current_s["s2"] = DEFAULT

    def a3_proc(self, e):
        if e.name == "s2":
            self.a3_buff.on()
            if not self.is_set_cd("a3", 10.0):
                self.add_amp(amp_id="20000", max_level=2)
                self.charge_p("a3", 15.0, target=("s1", "s2"))


variants = {None: Halloween_Sylas}
