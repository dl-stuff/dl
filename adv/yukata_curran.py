from core.advbase import *

class Yukata_Curran(Adv):
    conf = {'attenuation.hits': 1}
    def prerun(self):
        self.s1_ehits = 0
        self.comment = f'assume {self.conf.attenuation.hits+1} hits per s1 bullet'

    def add_combo(self, name='#'):
        result = super().add_combo(name)
        if name.startswith('s1'):
            self.s1_ehits += 1
        if self.s1_ehits >= 10:
            self.s1_ehits -= 10
            self.energy.add(5, queue=True)
        return result

class Yukata_Curran_ALL(Yukata_Curran):
    conf = {'attenuation.hits': 5}

variants = {
    None: Yukata_Curran,
    'ALL': Yukata_Curran_ALL
}
