from core.advbase import *


class Kimono_Luca(Adv):
    def prerun(self):
        self.mochi_master = 0
        self.a1_hits = 0

    @allow_acl
    def s(self, n, s1_kind=None):
        if self.in_dform():
            return False
        if n == 1 and s1_kind == "all":
            self.current_s["s1"] = "all"
        else:
            self.current_s["s1"] = "default"
        if n == 2 and not self.mochi_master:
            return False
        return super().s(n)

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        if name.startswith("fs") or name.startswith("s1"):
            self.a1_hits += self.echo
        if self.a1_hits >= 9:
            self.mochi_master = min(self.mochi_master + self.a1_hits // 9, 3)
            self.a1_hits %= 9
        return result

    def s2_proc(self, e):
        self.mochi_master = 0


variants = {None: Kimono_Luca}
