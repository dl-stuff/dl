from core.advbase import *
from module.template import LowerMCAdv


class Gala_Cleo_52MC(LowerMCAdv):
    MC = 52
    NO_DEPLOY = True


variants = {None: Adv, "50MC": LowerMCAdv, "52MC": Gala_Cleo_52MC}
