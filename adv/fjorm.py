from core.advbase import *

class Fjorm(Adv):
    comment = 'last bravery once at start'
    def prerun(self):
        Teambuff('last_bravery',0.3,15).on()
        Teambuff('last_bravery_defense', 0.40, 15, 'defense').on()

variants = {None: Fjorm}
