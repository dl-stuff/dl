from core.advbase import *

class Skill_Reservoir(Skill):
    def __init__(self, name=None, altchain=None):
        super().__init__(name)
        self.chain_timer = Timer(self.chain_off)
        self.chain_status = 0
        self.altchain = altchain or 'base'

    def chain_on(self, skill, timeout=3):
        log('debug', 'chain on', f's{skill}')
        self.chain_status = skill
        self.chain_timer.on(timeout)
        self._static.current_s[f's{skill}'] = f'chain{skill}'
        self._static.current_s[f's{3-skill}'] = f'{self.altchain}{3-skill}'

    def chain_off(self, t=None):
        log('debug', 'chain off')
        self.chain_status = 0
        self._static.current_s['s1'] = 'base1'
        self._static.current_s['s2'] = 'base2'

    @property
    def sp(self):
        return 1129

    def charge(self, sp):
        self.charged = min(self.sp*3, self.charged + sp)
        if self.charged >= self.sp*3:
            self.skill_charged()

    @property
    def count(self):
        return self.charged // self.sp

    def __call__(self, call=1):
        self.name = f's{call}'
        casted = super().__call__()
        if casted:
            if self.count == 0 and self.chain_timer.online:
                self.chain_timer.off()
                self.chain_off()
            else:
                self.chain_on(call)
        return casted

class Gala_Alex(Adv):
    comment = 'see special for bk chain'
    def __init__(self, altchain=None, **kwargs):
        super().__init__(**kwargs)
        self.sr = Skill_Reservoir('s1', altchain=altchain)
        self.a_s_dict['s1'] = self.sr
        self.a_s_dict['s2'] = self.sr

    def prerun(self):
        self.current_s['s1'] = 'base1'
        self.current_s['s2'] = 'base2'
        self.sr.enable_phase_up = False

    @allow_acl
    def s(self, n):
        sn = f's{n}'
        if n == 1 or n == 2:
            return self.a_s_dict[sn](call=n)
        else:
            return self.a_s_dict[sn]()

    @property
    def skills(self):
        return (self.sr, self.s3, self.s4)

    def charge_p(self, name, percent, target=None, no_autocharge=False):
        percent = percent / 100 if percent > 1 else percent
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            if no_autocharge and hasattr(s, 'autocharge_timer'):
                continue
            s.charge(self.sp_convert(percent, s.sp))
        log('sp', name if not target else f'{name}->{target}', f'{percent*100:.0f}%', f'{self.sr.charged}/{self.sr.sp} ({self.sr.count}), {self.s3.charged}/{self.s3.sp}, {self.s4.charged}/{self.s4.sp}')
        self.think_pin('prep')

    def charge(self, name, sp, target=None):
        sp = self.sp_convert(self.sp_mod(name), sp)
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            s.charge(sp)
        log('sp', name, sp, f'{self.sr.charged}/{self.sr.sp} ({self.sr.count}), {self.s3.charged}/{self.s3.sp}, {self.s4.charged}/{self.s4.sp}')
        self.think_pin('sp')

class Gala_Alex_BK(Gala_Alex):
    conf = {}
    conf['slots.a'] = [
        'Howling_to_the_Heavens',
        'Memory_of_a_Friend',
        'The_Shining_Overlord',
        'His_Clever_Brother',
        'The_Plaguebringer'
    ]
    conf['acl'] = """
        queue
        `s1; fs, x=4
        `s2; fs, x=4
        `s1; fs, x=4
        `s2;
        `s1;
        end
    """
    conf['coabs'] = ['Ieyasu','Wand','Summer_Patia']
    conf['share'] = ['Fjorm']
    conf['sim_afflict.frostbite'] = 1

    def __init__(self, **kwargs):
        kwargs['equip_key'] = None
        super().__init__(altchain='break', **kwargs)

    def pre_conf(self, equip_key=None):
        print(self.conf_init, flush=True)
        self.conf = Conf(self.conf_default)
        self.conf.update(globalconf.get_adv(self.name))
        self.conf.update(self.conf_init)
        self.conf.update(self.conf_base)
        return None

    def prerun(self):
        super().prerun()
        self.duration = 10
        self.sr.charged = 1129*3
        Selfbuff('agito_s3', 0.30, -1, 'spd', 'passive').on()
        Selfbuff('agito_s3', 0.05, -1, 'crit', 'chance').on()
        self.hits = 100

    def post_run(self, end):
        self.comment = f'{now():.02f}s sim; 3 charges into bk + bk killer chain; no bk def adjustment'

    def build_rates(self, as_list=True):
        rates = super().build_rates(as_list=False)
        rates['break'] = 1.00
        # rates['debuff_def'] = 1.00
        # rates['poison'] = 1.00
        return rates if not as_list else list(rates.items())

variants = {
    None: Gala_Alex,
    'BK': Gala_Alex_BK
}
