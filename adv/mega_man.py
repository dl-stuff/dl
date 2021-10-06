from core.advbase import *


class Skill_Ammo(Skill):
    def __init__(self, name=None, acts=None):
        super().__init__(name, acts)
        self.c_ammo = 0

    @property
    def ammo(self):
        return self.ac.conf.ammo

    @property
    def cost(self):
        return self.ac.conf.cost

    def check(self):
        if self._static.silence == 1:
            return False
        return self.c_ammo >= self.cost

    @allow_acl
    def check_full(self):
        if self._static.silence == 1:
            return False
        return self.c_ammo >= self.ammo

    def charge_ammo(self, ammo):
        self.c_ammo = min(self.ammo, self.c_ammo + ammo)


class Mega_Man(Adv):
    comment = "16 hits leaf shield (max 32 hits)"
    conf = {"mbleed": False}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.a_s_dict["s1"] = Skill_Ammo("s1")
        self.a_s_dict["s2"] = Skill_Ammo("s2")

    def prerun(self):
        self.leaf = 2  # number of hits per leaf rotation
        self.s1.charge_ammo(2000)
        self.s2.charge_ammo(4000)

    @property
    def skills(self):
        return self.s3, self.s4

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None, dtype=None):
        ammo = attr.get("ammo", 0)
        if ammo > 0:
            for s in (self.s1, self.s2):
                s.charge_ammo(ammo)
        elif ammo < 0:
            s = self.s1 if group == "metalblade" else self.s2
            s.charge_ammo(ammo)
            if s.c_ammo <= 0:
                self.current_x = "default"
        if ammo != 0:
            log(
                "ammo",
                name,
                ammo,
                " ".join(f"{s.c_ammo}/{s.ammo}" for s in (self.s1, self.s2)),
            )
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit, dtype=dtype)

    def s1_proc(self, e):
        if self.current_x != "metalblade":
            self.current_x = "metalblade"
        else:
            self.current_x = "default"

    def s2_proc(self, e):
        if self.current_x != "leafshield":
            self.current_x = "leafshield"
        else:
            self.current_x = "default"


variants = {None: Mega_Man, "mass": Mega_Man}
