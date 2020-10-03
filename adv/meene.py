
from core.advbase import *
from collections import deque

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
        self.act_history = deque(maxlen=6)
        Event('x').listener(self.push_to_act_history, order=0)
        Event('fs').listener(self.push_to_act_history, order=0)
        Event('dodge').listener(self.push_to_act_history, order=0)
        self.hecking_delayed = set()

    def push_to_act_history(self, e):
        self.check_delayed()
        self.act_history.append(e.name)
        log('act_history', str(self.act_history))
        if len(self.act_history) > 5:
            oldest = self.act_history.popleft()
            self.clear_oldest_butterflies(oldest)

    def check_delayed(self):
        for mt, k in self.hecking_delayed.copy():
            if not mt.online:
                self.clear_butterflies(*k, reason='canceled')
                self.hecking_delayed.remove((mt, k))

    def do_hitattr_make(self, e, aseq, attr, pin=None):
        mt = super().do_hitattr_make(e, aseq, attr, pin=pin)
        if attr.get('butterfly'):
            t = Timer(self.l_clear_butterflies)
            t.name = e.name
            t.chaser = attr.get('butterfly')
            t.start = now()
            t.on(9.001+attr.get('iv', 0))
            self.butterfly_timers[(e.name, t.chaser, now())].add(t)
            log('butterflies', 'spawn', self.butterflies)
            if mt:
                self.hecking_delayed.add((mt, (e.name, t.chaser, now())))
        elif mt and attr.get('chaser'):
            self.butterfly_timers[(e.name, attr.get('chaser'), now())].add(mt)
        if self.butterflies >= 6:
            self.current_s['s1'] = 'sixplus'
            self.current_s['s2'] = 'sixplus'

    def s1_before(self, e):
        self.check_delayed()
        log('butterflies', self.butterflies)

    def s2_before(self, e):
        self.check_delayed()
        log('butterflies', self.butterflies)

    def s1_proc(self, e):
        self.clear_all_butterflies()

    def s2_proc(self, e):
        self.clear_all_butterflies()

    def clear_all_butterflies(self):
        for chasers in self.butterfly_timers.values():
            for t in chasers:
                t.off()
        self.butterfly_timers = defaultdict(lambda: set())
        self.current_s['s1'] = 'default'
        self.current_s['s2'] = 'default'
        self.act_history.clear()
        log('butterflies', 'remove all', self.butterflies)

    def clear_oldest_butterflies(self, name):
        seq = [k[2] for k in self.butterfly_timers.keys() if k[0] == name]
        if not seq:
            return
        oldest = min(seq)
        matching = tuple(filter(lambda k: k[0] == name and k[2] == oldest, self.butterfly_timers.keys()))
        for m in matching:
            for mt in self.butterfly_timers[m]:
                mt.off()
            del self.butterfly_timers[m]
        if self.butterflies < 6:
            self.current_s['s1'] = 'default'
            self.current_s['s2'] = 'default'
        log('butterflies', f'remove {name}', self.butterflies)

    def clear_butterflies(self, name, chaser, start, reason='timeout'):
        try:
            key = (name, chaser, start)
            for mt in self.butterfly_timers[key]:
                mt.off()
            del self.butterfly_timers[key]
            if self.butterflies < 6:
                self.current_s['s1'] = 'default'
                self.current_s['s2'] = 'default'
            log('butterflies', f'{reason} {name}-{chaser}', self.butterflies)
        except KeyError:
            pass

    def l_clear_butterflies(self, t):
        self.clear_butterflies(t.name, t.chaser, t.start)

    @property
    def butterflies(self):
        return len(self.butterfly_timers.keys())

    @property
    def butterflies_s1(self):
        return min(10, self.butterflies)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)