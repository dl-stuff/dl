from core.advbase import *

def module():
    return Gala_Ranzal

class Gala_Ranzal(Adv):
    comment = 'no s2'

    conf = {}
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['slots.d'] = 'Vayu'
    conf['acl'] = '''
        `dragon(c3-s-end), s1.check()
        `s3, not buff(s3)
        `s1
        `s4, fsc
        `fs, x=2
    '''
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Akasha']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']

    def prerun(self):
        self.gauges = {'x':0, 'fs':0}

    def dmg_proc(self, name, amount):
        if name == 'x1':
            self.gauges['x'] += 77
        elif name == 'x2':
            self.gauges['x'] += 77
        elif name == 'x3':
            self.gauges['x'] += 100
        elif name == 'x4':
            self.gauges['x'] += 136
        elif name == 'x5':
            self.gauges['x'] += 200
        elif name == 'fs':
            self.gauges['fs'] += 150
        log('gauges', name, self.gauges['x'], self.gauges['fs'])

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
            self.s1_boosted_mod = Modifier(f'{e.name}_boost', 'att', 'granzal', 0.20)
        if boost == 2:
            self.s1_boosted_mod = Modifier(f'{e.name}_boost', 'att', 'granzal', 0.80)
        self.s1_boosted_mod.on()

    def s1_proc(self, e):
        if self.s1_boosted_mod:
            self.s1_boosted_mod.off()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
