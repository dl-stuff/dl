from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Gala_Ranzal

conf_fs_alt = {
    'fs_a.dmg':0.83*2+0.92,
    'fs_a.sp' :330,
    'fs_a.gauge': 350,
    'fs_a.charge': 2/60.0, # needs confirm
    'fs_a.startup':66/60.0,
    'fs_a.x1.startup':75/60.0,
    'fs_a.x2.startup':60/60.0,
    'fs_a.x3.startup':60/60.0,

    'fs_a.recovery':13/60.0,
    'fs_a.x1.recovery':13/60.0,
    'fs_a.x2.recovery':13/60.0,
    'fs_a.x3.recovery':13/60.0,
}

class Gala_Ranzal(Adv):
    comment = 'no s2'

    conf = conf_fs_alt.copy()
    conf['slots.a'] = The_Shining_Overlord()+Primal_Crisis()
    conf['slots.d'] = AC011_Garland()
    conf['acl'] = '''
        `dragon(c3-s-end)
        `s3, not self.s3_buff
        `s1, fsc
        `s4, fsc
        `fs, seq=2 and self.gauges['x'] <= 500
        `fs, seq=3
    '''
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']
    
    #c3 770
    #fs1 802
    #fs3 832
    #fsend 854-9
    #c1 854

    def prerun(self):
        self.ifs1ins2 = 0
        self.gauges = {'x':0, 'fs':0}
        self.fs_alt = FSAltBuff(self, 'a', uses=3)

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

    def s1_proc(self, e):
        try:
            boost = 0
            if self.gauges['x'] >= 1000:
                boost += 1
                self.gauges['x'] = 0
            if self.gauges['fs'] >= 1000:
                boost += 1
                self.gauges['fs'] = 0
            if boost == 1:
                self.dmg_make(f'o_{e.name}_boost',self.conf[f'{e.name}.dmg']*0.2)
            if boost == 2:
                self.dmg_make(f'o_{e.name}_boost',self.conf[f'{e.name}.dmg']*0.8)
            self.ifs1ins2 = 1
        except:
            pass


    def s2_proc(self, e):
        self.fs_alt.on(3)
        self.ifs1ins2 = 0
        Teambuff(e.name+'_defense', 0.10, 10, 'defense').on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
