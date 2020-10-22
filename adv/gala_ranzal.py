from core.advbase import *

gauge_values = {
    'x1': 77,
    'x2': 77,
    'x3': 100,
    'x4': 136,
    'x5': 200,
    'fs': 150,
    'fs_enhanced': 1000
}
class Gala_Ranzal(Adv):
    def prerun(self):
        self.gauges = {'x':0, 'fs':0}

    def charge_gauge(self, source, name):
        self.gauges[source] = min(self.gauges[source] + gauge_values[name], 1000)
        log('gauges', name, f'{self.gauges["x"]}/1000', f'{self.gauges["fs"]}/1000')

    def x_proc(self, e):
        self.charge_gauge('x', e.name)

    def fs_proc(self, e):
        self.charge_gauge('fs', e.name)

    def fs_enhanced_proc(self, e):
        self.charge_gauge('fs', e.name)

    def s1_before(self, e):
        self.s1_boosted_mod = None
        boost = 0
        if self.gauges['x'] >= 1000:
            boost += 1
            self.gauges['x'] = 0
        if self.gauges['fs'] >= 1000:
            boost += 1
            self.gauges['fs'] = 0
        if boost == 0:
            return
        if boost == 1:
            self.s1_boosted_mod = Modifier(e.name, 'att', 'granzal', 0.15).off()
        elif boost == 2:
            self.s1_boosted_mod = Modifier(e.name, 'att', 'granzal', 1.0).off()
        if self.s1_boosted_mod:
            self.extra_actmods.append(self.s1_boosted_mod)

    def s1_proc(self, e):
        if self.s1_boosted_mod:
            self.extra_actmods.remove(self.s1_boosted_mod)
            self.s1_boosted_mod = None

variants = {None: Gala_Ranzal}
