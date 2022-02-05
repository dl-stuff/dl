from core.advbase import *


class Valyx(Adv):
    DEFIANT_SPIRIT_CD = 20
    comment = "defiant spirit once every {}s".format(DEFIANT_SPIRIT_CD)

    def prerun(self):
        self.energy.set_permanent()
        self.defiant_spirit_buff = VarsBuff("defiant_spirit", "defiant_spirit", 1, 20)
        self.a1_defiant_spirit()
        Timer(self.a1_defiant_spirit, Valyx.DEFIANT_SPIRIT_CD, True).on()
        self.last_bravery_listener = Listener("hp", self.a3_last_def_amp)

    def a1_defiant_spirit(self, _=None):
        self.defiant_spirit_buff.on()

    def a3_last_def_amp(self, e):
        if e.hp <= 70 and (e.hp - e.delta) > 70 and not self.is_set_cd("a3_def_amp", 30):
            self.add_amp(amp_id="20000", max_level=2, target=2)


variants = {None: Valyx}
