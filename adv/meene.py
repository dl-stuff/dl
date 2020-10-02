
from core.advbase import *

def module():
    return Meene

class Meene(Adv):
    conf = {}
    conf['slots.a'] = [
        'Forest_Bonds',
        'Flash_of_Genius',
        'Dear_Diary',
        'The_Plaguebringer',
        'Chariot_Drift'
    ]
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s1
        `s2, fsc
        `s4
        `fs, x=3
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Akasha']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0

    def prerun(self):
        self.butterfly_timers = defaultdict(lambda: set())

    def do_hitattr_make(self, e, aseq, attr, pin=None):
        mt = super().do_hitattr_make(e, aseq, attr, pin=None)
        if attr.get('butterfly'):
            t = Timer(self.clear_butterflies)
            t.name = e.name
            t.chaser = attr.get('butterfly')
            t.start = now()
            t.on(9.001+attr.get('iv', 0))
            self.butterfly_timers[(e.name, t.chaser, now())].add(t)
        elif mt and attr.get('chaser'):
            self.butterfly_timers[(e.name, attr.get('chaser'), now())].add(mt)
        if self.butterflies >= 6:
            self.current_s['s1'] = 'sixplus'
            self.current_s['s2'] = 'sixplus'
    
    def s1_before(self, e):
        log('debug', 'butterflies', self.butterflies)

    def s2_before(self, e):
        log('debug', 'butterflies', self.butterflies)

    def s1_proc(self, e):
        self.clear_all_butterflies()

    def s2_proc(self, e):
        self.clear_all_butterflies()

    def clear_all_butterflies(self)
        for chasers in self.butterfly_timers.values():
            for t in chasers:
                t.off()
        self.butterfly_timers = defaultdict(lambda: set())
        self.current_s['s1'] = 'default'
        self.current_s['s2'] = 'default'

    def clear_butterflies(self, t):
        del self.butterfly_timers[(t.name, t.chaser, t.start)]
        if self.butterflies < 6: 
            self.current_s['s1'] = 'default'
            self.current_s['s2'] = 'default'

    @property
    def butterflies(self):
        return min(10, len(self.butterfly_timers.keys())

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)