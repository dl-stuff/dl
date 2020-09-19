from core.advbase import *

def module():
    return Lathna

class Lathna(Adv):
    comment = 'cat sith skill damage does not work on s1 extra hits'
    
    conf = {}
    conf['slots.a'] = ['Dragon_and_Tamer', 'The_Fires_of_Hate']
    conf['acl'] = """
        `dragon(c3-s-end), cancel
        `s3, not buff(s3)
        `s2
        `s4
        `s1(all), x=5
        """
    conf['coabs'] = ['Ieyasu','Wand','Forte']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']
        
    # conf['dragonform'] = {
    #     'act': 'c3-s-c3-c3-c2-c2-c2',

    #     'dx1.dmg': 2.31,
    #     'dx1.startup': 19 / 60.0, # c1 frames
    #     'dx1.hit': 1,

    #     'dx2.dmg': 2.54,
    #     'dx2.startup': 42 / 60.0, # c2 frames
    #     'dx2.hit': 1,

    #     'dx3.dmg': 3.34,
    #     'dx3.startup': 68 / 60.0, # c3 frames
    #     'dx3.recovery': 72 / 60.0, # recovery
    #     'dx3.hit': 2,

    #     'ds.recovery': 124 / 60, # skill frames
    #     'ds.hit': 2,

    #     'dodge.startup': 41 / 60.0, # dodge frames
    # }

    def prerun(self):
        self.dragonform.shift_mods.append(Modifier('faceless_god', 'poison_killer', 'passive', 2.00))
    
    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = 'all'

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
                self.dmg_make(e.name, 2.37/(1 + self.sub_mod('s', 'buff')))
                self.add_combo(e.name)
        # spaget
        self.last_c = now() + 1

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
