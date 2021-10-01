from core.advbase import *


# public enum ServantActionCommand
# {
#     None = 0,
#     Combo1 = 1,
#     Combo2 = 2,
#     Combo3 = 3,
#     Combo4 = 4,
#     Combo5 = 5,
#     Skill1 = 6,
#     Skill2 = 7
# }


class Joker(Adv):
    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(group="ddrive", x=True, fs=True, s1=True, s2=True), drain=75)

    def fs_ddrive_proc(self, e):
        self.dmg_make("x_arsene", 2.9)

    def x_ddrive_proc(self, e):
        if e.base in ("x3", "x6"):
            self.dmg_make("x_arsene", 2.56)


class Joker_PERSONA(Joker):
    SAVE_VARIANT = False
    comment = "infinite persona gauge"

    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(group="ddrive", x=True, fs=True, s1=True, s2=True), drain=75, infinite=True)
        self.dragonform.charge_gauge(3000, utp=True, dhaste=False)


variants = {None: Joker, "PERSONA": Joker_PERSONA}
