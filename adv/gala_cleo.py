from core.advbase import *
from module.template import LowerMCAdv


class Gala_Cleo_54MC(LowerMCAdv):
    MC = 54
    NO_DEPLOY = True
    SAVE_VARIANT = False


variants = {None: Adv, "50MC": LowerMCAdv, "54MC": Gala_Cleo_54MC}
