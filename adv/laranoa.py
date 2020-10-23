from core.advbase import *

class Laranoa(Adv):
    comment = 'no haste buff for teammates'

    def prerun(self):
        self.ahits = 0

    def add_combo(self, name='#'):
        super().add_combo(name)
        if self.hits // 20 > self.ahits:
            self.ahits = self.hits // 20
            Selfbuff(f'{name}_a1_crit',0.10,15,'crit','damage', source=name).on()

variants = {None: Laranoa}
