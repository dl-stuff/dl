from core.advbase import *
from functools import partial


class Saiga(Adv):
    def prerun(self):
        self.enemy_insight = 0
        self.calculated_shots = EffectBuff(
            "calculated_shots",
            30,
            partial(self.extra_actmods.append, self.get_saiga_x_mods),
            partial(self.extra_actmods.remove, self.get_saiga_x_mods),
        )
        self.saiga_x_mods = [
            Modifier("saiga_x_dmg", "x", "passive", 0.1).off(),
            Modifier("saiga_x_cc", "crit", "chance", 0.1).off(),
            Modifier("saiga_x_sp", "sp", "passive", 0.1).off(),
        ]
        self.saiga_fs_odaccel = Modifier("saiga_fs_odaccel", "odaccel", "passive", 3).off()
        self.extra_actmods.append(self.get_saiga_fs_odaccel)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.enemy_insight = 0

    def get_saiga_x_mods(self, name, base, group, aseq, attr):
        if name.startswith("x"):
            return self.saiga_x_mods
        return None

    def get_saiga_fs_odaccel(self, name, base, group, aseq, attr):
        if name.startswith("fs") and self.enemy_insight == 3:
            return self.saiga_fs_odaccel
        return None

    def s1_proc(self, e):
        if self.enemy_insight < 3:
            self.enemy_insight += 1
        else:
            self.enemy_insight = 0

    def s2_proc(self, e):
        if self.enemy_insight < 3:
            self.enemy_insight += 1
        else:
            self.enemy_insight = 0
            self.calculated_shots.on()

    def fs_proc(self, e):
        if self.enemy_insight == 3:
            self.enemy_insight = 0


variants = {None: Saiga}
