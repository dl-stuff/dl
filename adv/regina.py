from core.advbase import *
from module.template import SigilAdv
import random

S2_AFFS = {
    "poison": (110, 0.436),
    "burn": (110, 0.727),
    "flashburn": (110, 0.31),
    "stormlash": (110, 0.31),
    "shadowblight": (110, 0.31),
    "scorchrend": (110, 0.31),
    "paralysis": (110, 0.727),
}


class Regina(SigilAdv):
    comment = "expected value s2 affliction"

    def prerun(self):
        self.config_sigil(duration=300)
        self._protocol = 0
        self.fs_charging_timer = Timer(self.update_protocol, 1.5 - 0.00001, True)
        self._presigil_listeners = (
            Listener("aff_relief", lambda _: self.a_update_sigil(-30)),
            Listener("fs_start", lambda _: self.fs_charging_timer.on(), order=0),
            # unclear if fs action is included, data implies no
            Listener("fs_charged", lambda _: self.fs_charging_timer.off(), order=0),
        )

    def s1_proc(self, e):
        self.a_update_sigil(-9)

    def s2_hit1(self, *args):
        name, dtype = args[0], args[4]
        for aff, affargs in S2_AFFS.items():
            getattr(self.afflics, aff).on(name, *affargs, dtype=dtype, speshul_sandy_sum=2 / len(S2_AFFS))

    def update_protocol(self, e):
        self._protocol = (self._protocol + 1) % 3
        log("protocol", self._protocol, "preservation" if self.preservation_protocol else "restoration" if self.restoration_protocol else "purification")

    @property
    def preservation_protocol(self):
        return self._protocol == 0 or self.unlocked

    @property
    def restoration_protocol(self):
        return self._protocol == 1 or self.unlocked

    @property
    def purification_protocol(self):
        return self._protocol == 2 or self.unlocked


class Regina_RNG(Regina):
    comment = "random s2 affliction"

    def s2_hit1(self, *args):
        name, dtype = args[0], args[4]
        for aff, affargs in random.sample(S2_AFFS.items(), 2):
            getattr(self.afflics, aff).on(name, *affargs, dtype=dtype)


class Regina_UNLOCKED(Regina):
    SAVE_VARIANT = False

    def prerun(self):
        super().prerun()
        self.a_update_sigil(-300)


variants = {None: Regina, "RNG": Regina_RNG, "UNLOCKED": Regina_UNLOCKED}
