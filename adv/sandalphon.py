from conf import DEFAULT
from core.advbase import *
from module.template import Adv_DDAMAGE, Adv_INFUTP

S2_AFFS = {
    "poison": (110, 0.436),
    "burn": (110, 0.727),
    "flashburn": (110, 0.31),
    "stormlash": (110, 0.31),
    "shadowblight": (110, 0.31),
    "scorchrend": (110, 0.31),
    "paralysis": (110, 0.727),
}

# need to check the weird ass c9
class Sandalphon(Adv):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sr = ReservoirSkill(name="s1", true_sp=3450, maxcharge=3)
        self.a_s_dict["s1"] = self.sr
        self.a_s_dict["s2"] = self.sr

    def prerun(self):
        self._protocol = 0
        self.fs_charging_timer = Timer(self.update_protocol, 1.5 - 0.00001, True)
        Listener("fs_start", lambda _: self.fs_charging_timer.on(), order=0),
        Listener("fs_charged", lambda _: self.fs_charging_timer.off(), order=0)
        Listener("s", self.a1_amp)
        self.heal_event.listener(self.a3_healed_utp)

    def ds2_hit4(self, *args):
        name, dtype = args[0], args[4]
        for aff, affargs in S2_AFFS.items():
            getattr(self.afflics, aff).on(name, *affargs, dtype=dtype, speshul_sandy_sum=1 / len(S2_AFFS))

    @property
    def skills(self):
        return (self.sr, self.s3, self.s4)

    @allow_acl
    def s(self, n):
        if self.in_dform():
            return False
        if n == 1 or n == 2:
            return self.sr(call=n)
        else:
            return self.a_s_dict[f"s{n}"]()

    def update_protocol(self, e):
        self._protocol = (self._protocol + 1) % 2
        log("protocol", self._protocol, "coordination" if self.coordination_protocol else "concentration")
        if self.concentration_protocol:
            self.current_s["s1"] = "concentration"
            self.current_s["s2"] = "concentration"
        else:
            self.current_s["s1"] = DEFAULT
            self.current_s["s2"] = DEFAULT

    @property
    def coordination_protocol(self):
        return self._protocol == 0

    @property
    def concentration_protocol(self):
        return self._protocol == 1

    def a1_amp(self, e):
        if not self.is_set_cd("a1_amp", 20):
            self.add_amp(amp_id="20000", max_level=3)

    def a3_healed_utp(self, e):
        if not self.is_set_cd("a3_utp", 10):
            self.dragonform.charge_utp("a3_utp", 150)


class Sandalphon_RNG(Sandalphon):
    def ds2_hit4(self, *args):
        name, dtype = args[0], args[4]
        aff, affargs = random.sample(S2_AFFS.items(), 1)[0]
        getattr(self.afflics, aff).on(name, *affargs, dtype=dtype)


class Sandalphon_DDAMAGE(Sandalphon, Adv_DDAMAGE):
    pass


class Sandalphon_INFUTP(Sandalphon, Adv_INFUTP):
    pass


variants = {None: Sandalphon, "RNG": Sandalphon_RNG, "DDAMAGE": Sandalphon_DDAMAGE, "INFUTP": Sandalphon_INFUTP}
