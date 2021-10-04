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


class Joker_PERSONA(Adv):
    SAVE_VARIANT = False
    comment = "infinite persona gauge"

    def prerun(self):
        self.dragonform.utp_infinite = True


variants = {None: Adv, "PERSONA": Joker_PERSONA}
