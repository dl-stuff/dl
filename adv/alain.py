from core.advbase import *
from core.ability import Last_Buff


class Alain(Adv):
    def prerun(self):
        Last_Buff.HEAL_TO = 50


variants = {None: Alain}
