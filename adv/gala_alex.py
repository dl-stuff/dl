from core.advbase import *

def module():
    return Gala_Alex


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
    comment = 'see special for bk chain; s2 c4fs [s1 c4fs]*5 & use s1/s2 only when charge>=2'

    conf = {}
    conf['slots.a'] = [
        'The_Shining_Overlord',
        'Flash_of_Genius',
        'Moonlight_Party',
        'The_Plaguebringer',
        'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s=1
        `s3, not buff(s3)
        if fsc
        # use s4/s2 if no poison or if s1 def down has less than 1/3 time left
        if (self.sr.chain_status=1 and buff.timeleft(s1, base1)<5)
        `s4
        `s2
        end
        `s2, not afflics.poison.get()
        `s1, not buff(s1) or self.sr.count > 1
        end
        `fs, x=4
    """
    conf['coabs.base'] = ['Ieyasu','Wand','Delphi']
    conf['coabs.poison'] = ['Ieyasu','Wand','Forte']
    conf['share.base'] = ['Xander']
    conf['afflict_res.poison'] = 0

    def d_coabs(self):
        if self.duration <= 120:
            self.conf['coabs'] = ['Ieyasu','Wand','Heinwald']

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

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
