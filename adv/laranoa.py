from core.advbase import *

class Laranoa(Adv):
    comment = 'no haste buff for teammates'

    def prerun(self):
        self.ahits = 0

    def add_combo(self, name='#'):
        super().add_combo(name)
        if self.hits // 20 > self.ahits:
            self.ahits = self.hits // 20
            Selfbuff(f'{name}_a1_att',0.02,15,'att','buff', source=None).on()
            Selfbuff(f'{name}_a1_crit',0.01,15,'crit','chance', source=None).on()

variants = {None: Laranoa}
