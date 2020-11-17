from core.advbase import *
from module.template import RngCritAdv

a3_stack_cap = 10
class Gala_Laxi(Adv):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # human latency penalty on ex combo
        # for xn, xnconf in self.conf.find(r'^x\d+_ex$'):
        #     xnconf['startup'] += 0.05

    def prerun(self):
        self.x_fig_t = Timer(self.x_fig_dmg, 0.33, True).off()
        self.fig = EffectBuff('fig', 20, self.x_fig_on, self.x_fig_off)
        
        self.a1_cp = 0
        self.a1_buffs = {
            33: Selfbuff('a1_defense', 0.20, -1, 'defense', 'buff'),
            66: Selfbuff('a1_sd', 0.15, -1, 's', 'buff'),
            100: Selfbuff('a1_str', 0.15, -1, 'att', 'buff'),
        }
        self.a3_crit_buffs = []
        self.a3_crit_chance = 0
        self.a3_crit_dmg_stack = 0
        self.a3_crit_dmg_buff = Selfbuff('a3_crit_dmg',0.00,-1,'crit','damage')

        self.current_x = 'norm'
        self.deferred_x = 'ex'
        Event('s').listener(self.reset_to_norm, order=0)

        self.crit_mod = self.ev_custom_crit_mod
        self.rngcrit_states = {(None, 0): 1.0}
        self.rngcrit_cd_duration = 1
        self.prev_log_time = 0

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a3_crit_dmg_stack

    def rngcrit_cb(self, mrate=None):
        self.a3_crit_dmg_stack = mrate - 1
        new_value = 0.04*mrate
        if not self.a3_crit_dmg_buff.get():
            self.a3_crit_dmg_buff.set(new_value)
            self.a3_crit_dmg_buff.on()
        else:
            self.a3_crit_dmg_buff.value(new_value)

    def ev_custom_crit_mod(self, name):
        # print(f'{now():.02f}', self.a3_crit_dmg_stack+1, flush=True)
        if name == 'test' or self.a3_crit_dmg_stack >= 9:
            return self.solid_crit_mod(name)
        else:
            chance, cdmg = self.combine_crit_mods()
            t = now()

            new_states = defaultdict(lambda: 0.0)
            for state, state_p in self.rngcrit_states.items():
                if state[1] == a3_stack_cap:
                    new_states[(-1, a3_stack_cap)] += state_p
                elif state[0] is not None and t - state[0] < self.rngcrit_cd_duration:
                    new_states[state] += state_p
                else:
                    miss_rate = 1.0 - chance
                    new_states[state] += miss_rate * state_p
                    new_stack = state[1] + 1
                    new_states[(t, new_stack)] += chance * state_p
            
            new_states[(None, 0)] += 1 - sum(new_states.values())

            mrate = reduce(lambda mv, s: mv + (s[0][1] * s[1]), new_states.items(), 0)
            if self.prev_log_time == 0 or self.prev_log_time < t - self.rngcrit_cd_duration:
                log('rngcrit', mrate)
                self.prev_log_time = t
            self.rngcrit_cb(mrate)
            self.rngcrit_states = new_states

            return chance * (cdmg - 1) + 1

    def norm(self):
        if self.current_x != 'norm':
            self.deferred_x = 'norm'

    def ex(self):
        if self.current_x != 'ex':
            self.deferred_x = 'ex'
    
    def reset_to_norm(self, e):
        self.current_x = 'norm'

    def x(self, x_min=1):
        prev = self.action.getprev()
        if isinstance(prev, X) and (prev.group == self.current_x or 'ex' in (prev.group, self.current_x)):
            if self.deferred_x is not None:
                log('deferred_x', self.deferred_x)
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

    def x_fig_on(self):
        self.x_fig_t.on()
        self.current_s['s1'] = 'eden'
        self.current_s['s2'] = 'eden'

    def x_fig_off(self):
        self.x_fig_t.off()
        self.current_s['s1'] = 'default'
        self.current_s['s2'] = 'default'
        self.a1_update(-100)

    def x_fig_dmg(self, t):
        if any([s_dict.ac.status != -2 for s_dict in self.a_s_dict.values()]):
            return
        if self.dragonform.status != -2:
            return
        self.dmg_make('#fig', 0.333)
        self.add_combo('#fig')

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        self.a1_update(attr.get('cp', 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit)

    def a1_update(self, delta):
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
        kept_combo = super().add_combo(name)
        if not kept_combo:
            for c in self.a3_crit_buffs:
                c.off()
            self.a3_crit_buffs = []
            self.rngcrit_states = {(None, 0): 1.0}
            self.prev_log_time = 0
        a_hits = self.hits // 15
        if len(self.a3_crit_buffs) < 3 and self.condition('always connect hits') and a_hits > len(self.a3_crit_buffs):
            self.a3_crit_buffs.append(Selfbuff('a3_crit_chance',0.04,-1,'crit','chance').on())

    def s2_proc(self, e):
        if e.group == 'default':
            self.fig.on()

variants = {None: Gala_Laxi}
