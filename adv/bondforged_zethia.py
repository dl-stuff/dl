from core.advbase import *
from conf import DEFAULT


class Bondforged_Zethia(Adv):
    def prerun(self):
        self.power_of_bonds = ModeManager(
            name="bonds",
            group="bonds",
            s1=True,
            s2=True,
            source="s2",
        )
        self.a1_heal_listener = Listener("hp", self.a1_heal)
        self.bondforged_might = Modifier("bondforged_might", "s", "passive", 0.4, get=self.power_of_bonds.get)

    def a1_heal(self, e):
        if e.hp <= 30 and (e.hp - e.delta) > 30 and not self.is_set_cd("bondforged_auspex", 45):
            self.heal_make("bondforged_auspex", 150, "team" if self.power_of_bonds.get() else "self")

    def set_hp(self, hp, percent=True, can_die=False, ignore_dragon=False, source=None):
        revive = False
        if can_die and self.power_of_bonds.get():
            can_die = False
            revive = True
        super().set_hp(hp, percent, can_die, ignore_dragon, source)
        if self.hp == 1 and revive:
            self.power_of_bonds.off()

    def s2_proc(self, e):
        if e.group == DEFAULT:
            self.power_of_bonds.on()
            self.s2.charge(1)
        else:
            self.power_of_bonds.off()


variants = {None: Bondforged_Zethia}
