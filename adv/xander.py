from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Xander

# identical to granzal FS in frames
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

class Xander(Adv):
    conf = conf_fs_alt.copy()
    conf['slots.a'] = The_Shining_Overlord()+His_Clever_Brother()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        if self.born_ruler_1.get() and not self.born_ruler_2.get()
        `s3 
        `s4
        `s2
        `s1
        else
        `dragon(c3-s-end), fsc
        `s3, fsc or s
        `s2, fsc or s
        `s1, fsc or s
        `fs, x=2
        end
    """
    conf['coabs'] = ['Blade', 'Yurius', 'Hunter_Sarisse']
    conf['share'] = ['Gala_Elisanne', 'Hunter_Sarisse']

    def fs_proc(self, e):
        if self.born_ruler_2.get():
            with KillerModifier('fs_killer', 'hit', 0.30, ['frostbite']):
                self.dmg_make('fs', 6.66)
        else:
            self.dmg_make('fs', 3.26)
        self.conf['s1'].dmg = 8.32
        self.born_ruler.off()
        self.born_ruler_1.off()
        self.born_ruler_2.off()

    def prerun(self):
        self.fs_alt = FSAltBuff('a', hidden=True)
        self.born_ruler = Selfbuff('born_ruler', 0.05, -1, 'att', 'buff')
        self.born_ruler_1 = Selfbuff('born_ruler_1', 1, -1, 'xunder', 'buff')
        self.born_ruler_2 = Selfbuff('born_ruler_2', 1, -1, 'xunder', 'buff')
    
    def s1_proc(self, e):
        boost = 0.05*self.buffcount
        self.afflics.frostbite(e.name,120,0.41*(1+boost))
        try:
            if self.born_ruler_2.get():
                # phase 3
                self.dmg_make(f'o_{e.name}_boost',self.conf[e.name].dmg*boost)
                self.conf[e.name].dmg = 8.32
                self.fs_alt.off()
                self.born_ruler.off()
                self.born_ruler_1.off()
                self.born_ruler_2.off()
            elif self.born_ruler_1.get():
                # phase 2
                self.dmg_make(f'o_{e.name}_boost',self.conf[e.name].dmg*boost)
                self.conf[e.name].dmg = 8.40
                self.born_ruler_2.on()
            else:
                self.fs_alt.on()
                self.born_ruler.on()
                self.born_ruler_1.on()
                # phase 1
                self.dmg_make(f'o_{e.name}_boost',self.conf[e.name].dmg*boost)
                self.conf[e.name].dmg = 8.37
        except:
            self.dmg_make(f'o_{e.name}_boost',self.conf[e.name].dmg*boost)
        log('debug', 'xander_s1_boost', f'x{self.buffcount} = {self.conf[e.name].dmg*(1+boost):.2%}')

    def s2_proc(self, e):
        boost = 0.05*self.buffcount
        self.dmg_make(f'o_{e.name}_boost',self.conf[e.name].dmg*boost)
        log('debug', 'xander_s2_boost', f'x{self.buffcount} = {self.conf[e.name].dmg*(1+boost):.2%}')

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
