from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Lathna

class Lathna(Adv):
    comment = 'cait sith skill damage does not work on s1 extra hits'
    
    conf = {}
    conf['slots.a'] = Dragon_and_Tamer()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), cancel
        `s3, not buff(s3)
        `s2
        `s4
        `s1(all), x=5
        """
    conf['coabs'] = ['Ieyasu','Wand','Forte']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

        
    conf['dragonform'] = {
        'act': 'c3-s-c3-c3-c2-c2-c2',

        'dx1.dmg': 2.31,
        'dx1.startup': 19 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 2.54,
        'dx2.startup': 42 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 3.34,
        'dx3.startup': 68 / 60.0, # c3 frames
        'dx3.recovery': 72 / 60.0, # recovery
        'dx3.hit': 2,

        'ds.recovery': 124 / 60, # skill frames
        'ds.hit': 2,

        'dodge.startup': 41 / 60.0, # dodge frames
    }

    def ds_proc(self):
        dmg = self.dmg_make('ds', 3.64, 's')
        self.afflics.poison('ds',120,0.291,30,dtype='s')
        # self.afflics.poison('ds',120,3.00,30,dtype='s')
        return dmg + self.dmg_make('ds',3.64,'s')

    def prerun(self):
        self.faceless_god = Selfbuff('faceless_god',2.00,-1,'poison_killer','passive')
        Event('dragon').listener(self.a1_on)
        Event('idle').listener(self.a1_off)
    
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = 'all'

    def a1_on(self, e):
        if not self.faceless_god.get():
            self.faceless_god.on()

    def a1_off(self, e):
        if self.faceless_god.get():
            self.faceless_god.off()

    def s(self, n, s1_kind=None):
        if n == 1 and s1_kind == 'all':
            self.current_s['s1'] = s1_kind
        else:
            self.current_s['s1'] = 'default'
        return super().s(n)

    def s1_proc(self, e):
        # reeeeeee fix ur shit cykagames
        with KillerModifier('s1_killer', 'hit', 0.6, ['poison']):
            for _ in range(4):
                self.dmg_make(e.name, 2.37/self.sub_mod('s', 'buff'))
                self.add_hits(1)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
