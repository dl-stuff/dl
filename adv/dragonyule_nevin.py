from core.advbase import *
from conf import float_ceil
from module.template import SigilAdv


class Dragonyule_Nevin(SigilAdv):
    DIVINE_DAGGER_ATTR = {"dmg": 2.0, "sp": 30}
    DIVINE_STING_ATTR = {"dmg": 1.0, "sp": 30}
    S1_SP_MOD = 0.2

    def prerun(self):
        self.config_sigil(duration=300, s1=True, s2=True, fs=True)

        self.divine_dagger_timer = Timer(self.divine_dagger_dmg, 2.0, True)
        self.divine_dagger = 0
        self.divine_sting_timer = Timer(self.divine_sting_dmg, 2.9, True)
        self.divine_sting_stacks = []

        self.divine_sting_resdown = Modifier("divine_sting_resdown", f"affres_stormlash", "debuff", 0.0)
        self.divine_sting_resdown.get = lambda: 0.15 * len(self.divine_sting_stacks)
        self.afflics.stormlash.aff_res_mods.append(self.divine_sting_resdown)

    def _add_sp_fn(self, s, name, sp):
        if not self.unlocked and s.name == "s1":
            sp = float_ceil(sp, self.sp_mod(name, target=s.name) * self.S1_SP_MOD)
        else:
            sp = float_ceil(sp, self.sp_mod(name, target=s.name))
        s.charge(sp)
        return sp

    def _prep_sp_fn(self, s, _, percent):
        # this may need to be generalized
        if not self.unlocked and s.name == "s1":
            sp = float_ceil(s.real_sp, percent * self.S1_SP_MOD)
        else:
            sp = float_ceil(s.real_sp, percent)
        s.charge(sp)
        return sp

    @property
    def divine_sting(self):
        return 4 - self.divine_dagger

    def update_divine_dagger(self, count, fs=False):
        old_divine_dagger = self.divine_dagger
        self.divine_dagger = max(min(self.divine_dagger + count, 4), 0)
        if old_divine_dagger != self.divine_dagger:
            log("divine_dagger", f"{count:+}", self.divine_dagger)
            # skip impl. sting decreasing but not returning to 0 since that's not a thing that happens
            if self.divine_sting == 0:
                self.divine_sting_stacks = []
            else:
                while len(self.divine_sting_stacks) < self.divine_sting:
                    self.divine_sting_stacks.append(self.dmg_formula("fs_divine_sting", 1.5, dtype="fs"))

    def fs1_sigil_proc(self, e):
        self.update_divine_dagger(-1)

    def fs2_sigil_proc(self, e):
        self.update_divine_dagger(-2)

    def fs3_sigil_proc(self, e):
        self.update_divine_dagger(-3)

    def fs4_sigil_proc(self, e):
        self.update_divine_dagger(-4)

    @allow_acl
    def fs(self, n=None):
        if self.unlocked and n is not None:
            n = min(n, self.divine_dagger) or 1
        super().fs(n=n)

    def a_sigil_unlock(self):
        self.divine_dagger_timer.on()
        self.divine_sting_timer.on()
        return super().a_sigil_unlock()

    def divine_dagger_dmg(self, t):
        if not self.in_dform():
            for i in range(self.divine_dagger):
                self.hitattr_make("#divine_dagger", "#", "default", i, self.DIVINE_DAGGER_ATTR, dtype="#")

    def divine_sting_dmg(self, t):
        # self.dmg_make("fs_divine_sting", sum(self.divine_sting_stacks), fixed=True)
        count = sum(self.divine_sting_stacks)
        if count > 0:
            log("dmg", "fs_divine_sting", sum(self.divine_sting_stacks), 0)

    def s1_proc(self, e):
        if not self.unlocked:
            self.a_update_sigil(-300)
        self.update_divine_dagger(4)

    def s2_proc(self, e):
        if self.unlocked:
            self.update_divine_dagger(4)


class Dragonyule_Nevin_UNLOCKED(Dragonyule_Nevin):
    SAVE_VARIANT = False

    def prerun(self):
        super().prerun()
        self.a_update_sigil(-300)


variants = {None: Dragonyule_Nevin, "UNLOCKED": Dragonyule_Nevin_UNLOCKED}
