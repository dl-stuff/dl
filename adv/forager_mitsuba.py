from core.advbase import *

class Forager_Mitsuba(Adv):
    def prerun(self):
        self.ahits = 0
        self.new_dish = 0
        o_s2_check = self.a_s_dict['s2'].check
        self.a_s_dict['s2'].check = lambda: o_s2_check() and self.new_dish > 0

    def s2_proc(self, e):
        self.new_dish = 0
        log('new_dish', self.new_dish, self.hits)

    def add_combo(self, name='#'):
        result = super().add_combo(name)
        if self.condition('always connect hits'):
            a_hits = self.hits // 15
            if a_hits > 0 and a_hits != self.ahits and self.new_dish < 3:
                self.ahits = a_hits
                self.new_dish += 1
                log('new_dish', self.new_dish, self.hits)
        return result

variants = {None: Forager_Mitsuba}
