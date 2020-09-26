from core.advbase import *
from module.template import RngCritAdv

def module():
    return Gala_Laxi

class Gala_Laxi(RngCritAdv):    
    conf = {}
    conf['slots.a'] = [
    'Twinfold_Bonds',
    'Flash_of_Genius',
    'Me_and_My_Bestie',
    'His_Clever_Brother',
    'A_Passion_for_Produce'
    ]
    conf['acl'] = """
        # `norm
        `ex
        `dragon,s=2
        queue prep
        `s2;s1;s4
        end
        `s3, not buff(s3) and x=4
        `s2
        `s1
        `s4
        """
    conf['afflict_res.burn'] = 0
    conf['coabs'] = ['Halloween_Mym', 'Serena', 'Yuya']
    conf['share'] = ['Xander']

    def __init__(self, conf=None, cond=None):
        super().__init__(conf=conf, cond=cond)
        self.slots.c.coabs = {'Dagger2': [None, 'dagger2']}
        # human latency penalty on ex combo
        for xn, xnconf in self.conf.find(r'^x\d+_ex$'):
            xnconf['startup'] += 0.05

    def prerun(self):
        self.fig_t = Timer(self.fig_dmg, 0.33, True).off()
        self.fig = EffectBuff('fig', 20, self.fig_on, self.fig_off)
        
        self.a1_cp = 0
        self.a1_buffs = {
            33: Selfbuff('a1_defense', 0.20, -1, 'defense', 'buff'),
            66: Selfbuff('a1_sd', 0.15, -1, 's', 'buff'),
            100: Selfbuff('a1_str', 0.15, -1, 'att', 'buff'),
        }
        self.a3_crit_chance = 0
        self.a3_crit_dmg = 0
        self.config_rngcrit(cd=1)

        self.current_x = 'norm'
        self.deferred_x = 'ex'
        Event('s').listener(self.reset_to_norm, order=0)

    def norm(self):
        self.deferred_x = 'norm'

    def ex(self):
        self.deferred_x = 'ex'
    
    def reset_to_norm(self, e):
        self.current_x = 'norm'

    def rngcrit_skip(self):
        return self.a3_crit_dmg > 9

    def rngcrit_cb(self):
        self.a3_crit_dmg += 1
        return Selfbuff('a3_crit_dmg',0.04,-1,'crit','damage').on()

    def x(self, x_min=1):
        prev = self.action.getprev()
        if isinstance(prev, X) and (prev.group == self.current_x or 'ex' in (prev.group, self.current_x)):
            if self.deferred_x is not None:
                log('x', 'deferred_x on', self.deferred_x)
                self.current_x = self.deferred_x
                self.deferred_x = None
            if prev.index < self.conf[prev.group].x_max:
                x_next = self.a_x_dict[self.current_x][prev.index+1]
            else:
                x_next = self.a_x_dict[self.current_x][x_min]
            if x_next.enabled:
                return x_next()
            else:
                self.current_x = 'default'
        return self.a_x_dict[self.current_x][x_min]()

    def fig_on(self):
        self.fig_t.on()
        self.current_s['s1'] = 'eden'
        self.current_s['s2'] = 'eden'

    def fig_off(self):
        self.fig_t.off()
        self.current_s['s1'] = 'default'
        self.current_s['s2'] = 'default'
        self.update_a1(-100)

    def fig_dmg(self, t):
        if any([self.a_s_dict[sn].ac.status != -2 for sn in ('s1', 's2')]):
            return
        self.dmg_make('x_fig', 1.00, 'x')
        self.add_combo('x_fig')

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        self.update_a1(attr.get('cp', 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=None)

    def update_a1(self, delta):
        if delta != 0 and not self.fig.get() and self.a1_cp < 100:
            next_cp = max(min(self.a1_cp+delta, 100), 0)
            delta = next_cp - self.a1_cp
            if delta == 0:
                return
            if delta > 0:
                for thresh, buff in self.a1_buffs.items():
                    if self.a1_cp < thresh and next_cp >= thresh:
                        buff.on()
            else:
                for thresh, buff in self.a1_buffs.items():
                    if next_cp < thresh:
                        buff.off()
            self.a1_cp = next_cp
            log('galaxi', 'cp', self.a1_cp)

    def add_combo(self, name='#'):
        super().add_combo(name)
        if self.a3_crit_chance < 3 and self.condition('always connect hits') and self.hits // 15 > self.a3_crit_chance:
            self.a3_crit_chance = self.hits // 15
            Selfbuff('a3_crit_chance',0.04,-1,'crit','chance').on()

    def s2_proc(self, e):
        if e.group == 'default':
            self.fig.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
