from core.advbase import *

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
        
    def s1_proc(self, e):
        if e.name in self.energy.active:
            Teambuff(f'{e.name}_cc',0.1,30,'crit','chance').on()

variants = {None: Lucretia}
