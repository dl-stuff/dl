from core.advbase import *


class Gala_Elisanne(Adv):
    def prerun(self):
        self.s2.autocharge_init(self.s2_autocharge).on()
        self.divine_revelation = Selfbuff("divine_revelation", 1, 13, "kb", "res", source="a1")
        self.ahits = 0
        Event("fs").listener(self.dr_proc)
        Event("s").listener(self.dr_proc)

    def dr_proc(self, e):
        self.divine_revelation.on()

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        a_hits = self.hits // 10
        if a_hits > 0 and a_hits != self.ahits:
            self.ahits = a_hits
            self.divine_revelation.on()
        return result

    def s2_autocharge(self, t):
        if self.divine_revelation.get():
            log("sp", "s2_autocharge", 960)
            self.s2.charge(960)  # 2496 - 1536
        elif self.s2.charged < self.s2.sp:
            self.s2.charge(-1536)


class Gala_Elisanne_70MC(Gala_Elisanne):
    def prerun(self):
        super().prerun()
        # procs doublebuff for some reason kms
        self.divine_revelation = Selfbuff("divine_revelation", 0.2, 13, "defense", "buff", source="a1")
        self.s2_timer = Timer(self.s2_cd_end, 30)

    def s2_cd_end(self):
        self.s2_cd = False

    def s2_proc(self, e):
        if not self.s2_cd:
            # y tho
            self.add_one_att_amp()
            self.s2_cd = True
            self.s2_timer.on()

    SAVE_VARIANT = False
    comment = "70MC"
    conf = {
        "c": {
            "name": "Gala Elisanne",
            "icon": "100002_13_r05",
            "att": 618,
            "hp": 893,
            "ele": "water",
            "wt": "axe",
            "spiral": True,
            "a": [
                ["resself_burn_att", 0.15, 10.0, 15.0],
                ["resself_stun_att", 0.15, 10.0, 15.0],
                ["affres_burn", 100.0],
                ["affres_stun", 100.0],
                ["primed_att", 0.15],
            ],
        },
        "s1": {
            "sp": 4377,
            "startup": 0.1,
            "recovery": 1.23333,
            "attr": [
                {"buff": [["team", 1.2, 15.0, "heal", "buff"], ["ele", 0.15, 15.0, "att", "buff", "water"]], "coei": 1, "iv": 0.5},
                {"buff": ["ele", 0.15, 15.0, "att", "buff", "water"], "iv": 0.5},
            ],
            "energizable": True,
        },
        "s2": {
            "sp": 38400,
            "startup": 0.1,
            "recovery": 2.06667,
            "attr": [{"dmg": 13.75, "iv": 0.2}, {"dmg": 13.75, "iv": 0.53333}, {"dmg": 13.75, "iv": 1.43333}, {"buff": ["energy", 3], "iv": 1.43333}],
        },
    }


variants = {None: Gala_Elisanne, "70MC": Gala_Elisanne_70MC}
