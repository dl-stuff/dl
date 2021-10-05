from core.advbase import *
from module.template import LowerMCAdv


class Gala_Cleo_52MC(LowerMCAdv):
    MC = 52
    NO_DEPLOY = True
    SAVE_VARIANT = False


variants = {None: Adv, "50MC": LowerMCAdv, "52MC": Gala_Cleo_52MC}
