from core.advbase import *

def module():
    return Lucretia

class Lucretia(Adv):
    
    conf = {}
    conf['slots.a'] = ['Candy_Couriers', 'Proper_Maintenance']
    conf['acl'] = """
        `dragon, energy()>3
        `s3, not buff(s3)
        `s4, s=1
        `s1
        `s2, energy()<3
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Tobias','Peony']
    conf['share'] = ['Summer_Cleo']

    def d_coabs(self):
        if self.duration <= 120:
            self.conf['coabs'] = ['Blade','Bow','Peony']
        
    def s1_proc(self, e):
        if e.name in self.energy.active:
            Teambuff(f'{e.name}_cc',0.1,30,'crit','chance').on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)