from core.advbase import *

def module():
    return Laxi

class Laxi(Adv):
    comment = 'a1 proc at 0s'
    
    conf = {}
    conf['slots.a'] = ['Primal_Crisis', 'The_Wyrmclan_Duo']
    conf['slots.d'] = 'Gala_Mars'
    conf['acl'] = '''
        `dragon
        `s3, not buff(s3)
        `s2, not buff(s2)
        `s1,cancel
        `s4,cancel
        `fs, x=5 and charged_in(fs, s2) and not buff(s2)
        '''
    conf['coabs'] = ['Dagger', 'Marth', 'Dagger2']
    conf['share'] = ['Kleimann']

    def prerun(self):  
        self.healed = 0
        self.heal = Action('heal', Conf({'startup': 5.0, 'recovery': 0.1}))
        self.heal.atype = 's' # haxx
        Event('hp').listener(self.a1_heal_proc)

    def a1_heal_proc(self, e):
        if self.healed == 0 and e.delta < 0 and e.hp <= 30:
            self.healed = 1
            self.set_hp(100)
            self.heal()
            for buff in self.all_buffs:
                if buff.source != 'ability':
                    buff.off()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)