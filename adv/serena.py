from core.advbase import *

class Serena(Adv):
    def prerun(self):
        self.a1_dict = {
            'count': 0,
            'buffs': [],
            'threshold': 20,
            'buffargs': ('a1_cd',0.06,-1,'crit','damage')
        }
        self.a3_dict = {
            'count': 0,
            'buffs': [],
            'threshold': 30,
            'buffargs': ('a3_cc',0.03,-1,'crit','chance')
        }

    def update_a(self, a_dict, kept_combo):
        if self.condition('always connect hits') and len(a_dict['buffs']) < 3:
            a_hits = self.hits // a_dict['threshold']
            if a_hits > 0 and a_dict['count'] != a_hits:
                a_dict['buffs'].append(Selfbuff(*a_dict['buffargs']).on())
                a_dict['count'] = a_hits

    def add_combo(self, name='#'):
        kept_combo = super().add_combo(name)
        self.update_a(self.a1_dict, kept_combo)
        self.update_a(self.a3_dict, kept_combo)

variants = {None: Serena}
