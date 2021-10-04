from core.advbase import *


class Summer_Sinoa(Adv):
    def prerun(self):
        self.overload = 0
        self.overload_sp = Modifier("overload_sp", "sp_s1", "passive", 0.0)
        self.overload_sp.get = self.overload_sp_mod
        self.ssinoa_determination = Modifier("determination", "s", "passive", 0.0)
        self.extra_actmods.append(self.get_ssinoa_determination)

    def get_ssinoa_determination(self, name, base, group, aseq, attr):
        if self.overload > 0 and base in ("s1", "ds1"):
            self.ssinoa_determination.mod_value = 0.15 + 0.05 * self.overload
            return self.ssinoa_determination
        return None

    def overload_sp_mod(self):
        if self.overload == -1:
            return 0
        return self.overload * -0.3

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.overload = -1

    def s2_proc(self, e):
        if not self.nihilism:
            if self.overload == 3:
                self.inspiration.add(2, team=True)
                Teambuff("s2_crit_rate", 0.20, 30, "crit", "chance").on()
                Teambuff("s2_crit_dmg", 0.15, 30, "crit", "damage").on()
            else:
                buffs = [
                    lambda: self.inspiration.add(2),
                    lambda: Selfbuff("s2_crit_rate", 0.20, 30, "crit", "chance").on(),
                    lambda: Selfbuff("s2_crit_dmg", 0.15, 30, "crit", "damage").on(),
                ]
                log("debug", "overload", self.overload)
                for _ in range(max(1, self.overload)):
                    buff = random.choice(buffs)
                    buff()
                    buffs.remove(buff)
        self.overload = 0


variants = {None: Summer_Sinoa}
