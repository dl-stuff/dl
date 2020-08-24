from core.advbase import Fs_group, Fs, X, Event
from core.timeline import Listener, Timer, now
from core.log import log
from core.config import Conf
from core.dragonform import DragonForm
import re

class Fs_alt:
    def __init__(self, adv, conf, fs_proc=None):
        # Note: Do not run this in adv init, as it will copy premature conf.
        # TODO add l_fs_alt to better handle before and after when needed; maybe fsnf 
        self.patterns = [
            re.compile(r'^a_fs(?!f).*'),
            re.compile(r'^conf$'),
            re.compile(r'^fs.*proc$')
        ]
        self.pattern_fsn = re.compile(r'^f.*(?<!f)$')
        self.adv = adv
        self.conf_alt = adv.conf + Conf(conf)
        self.fs_proc_alt_temp = fs_proc
        self.uses = 0
        self.has_fsf = False
        self.do_config(self.conf_alt)
        if 'fsf' in conf:
            self.a_fsf_og = adv.a_fsf
            self.a_fsf_alt = Fs('fsf', conf.fsf)
            self.a_fsf_alt.act_event = Event('none')
            self.has_fsf = True

    def fs_proc_alt(self, e):
        if callable(self.fs_proc_alt_temp):
            self.fs_proc_alt_temp(e)
        if self.uses != -1:
            self.uses -= 1
            if self.uses == 0:
                self.off()

    def on(self, uses = 1):
        log('debug', 'fs_alt on', uses)
        self.uses = uses
        # self.adv.a_fs = self.a_fs_alt
        # self.adv.conf = self.conf_alt
        # self.adv.fs_proc = self.fs_proc
        for pattern in self.patterns:
            self._replace(pattern)
        if self.has_fsf:
            self.adv.fsf = self.a_fsf_alt

    def off(self):
        log('debug', 'fs_alt off', 0)
        self.uses = 0
        # self.adv.a_fs = self.a_fs_og
        # self.adv.conf = self.conf_og
        # self.adv.fs_proc = self.fs_proc_og
        for pattern in self.patterns:
            self._restore(pattern)
        if self.has_fsf:
            self.adv.fsf = self.a_fsf_og

    def get(self):
        return self.uses

    def do_config(self, conf):
        # fsns = [n for n, c in conf.items() if self.pattern_fsn.match(n)]
        fsns = list(filter(self.pattern_fsn.match, conf.keys()))
        for fsn in fsns:
            self._set_attr_f(fsn, conf)
        if len(fsns) > 1:
            self.a_fs_alt = lambda before: None
        for pattern in self.patterns:
            self._back_up(pattern)

    def _back_up(self, pattern):
        self._copy_attr(pattern, self, self.adv, '_og', '')

    def _replace(self, pattern):
        self._copy_attr(pattern, self.adv, self, '', '_alt')

    def _restore(self, pattern):
        self._copy_attr(pattern, self.adv, self, '', '_og')
    
    def _copy_attr(self, pattern, dest, orig, d_sfx, o_sfx):
        attrs = list(filter(pattern.match, dir(self.adv)))
        for attr in attrs:
            setattr(dest, f'{attr}{d_sfx}', getattr(orig, f'{attr}{o_sfx}'))

    def _set_attr_f(self, n, conf):
        if not hasattr(self.adv, n):
            setattr(self.adv, f'a_{n}', lambda before: None)
            # setattr(self.adv, f'{n}_before', lambda e:)
            # setattr(self.adv, f'{n}_after', lambda e:)
            setattr(self.adv, n, lambda:getattr(self.adv, f'a_{n}')(self.adv.action.getdoing().name))
        setattr(self, f'a_{n}_alt', Fs_group(n, conf))
            
class X_alt:
    def __init__(self, adv, name, conf, x_proc=None, no_fs=False, no_dodge=False):
        self.conf = Conf(conf)
        self.adv = adv
        self.name = name
        self.x_og = adv.x
        self.a_x_alt = {}
        self.x_proc = x_proc or self.x_proc_default
        self.l_x_alt = Listener('x', self.l_x).off()
        self.no_fs = no_fs
        self.no_dodge = no_dodge
        self.fs_og = adv.fs
        self.dodge_og = adv.dodge
        self.xmax = 1
        n = 'x{}'.format(self.xmax)
        while n in self.conf:
            self.a_x_alt[self.xmax] = X((n, self.xmax), self.conf[n])
            self.xmax += 1
            n = 'x{}'.format(self.xmax)
        self.xmax -= 1
        self.active = False
        self.xstart = None
        self.zeroed = None

    def x_alt(self):
        x_prev = self.adv.action.getprev()
        if x_prev in self.a_x_alt.values() and x_prev.index < self.xmax:
            x_seq = x_prev.index+1
        else:
            x_seq = 1
        return self.a_x_alt[x_seq]()

    def x_proc_default(self, e):
        xseq = e.name
        dmg_coef = self.conf[xseq].dmg
        sp = self.conf[xseq].sp
        hit = self.conf[xseq].hit
        log('x', xseq, self.name)
        self.adv.hits += hit
        self.adv.dmg_make(xseq, dmg_coef)
        self.adv.charge(xseq, sp)

    def l_x(self, e):
        self.x_proc(e)
        self.adv.think_pin('x')

    def act_off(self):
        return False

    def on_t(self, t):
        log('debug', '{} x_alt on'.format(self.name))
        self.active = True
        self.adv.x = self.x_alt
        if self.l_x_alt:
            self.adv.l_x.off()
            self.l_x_alt.on()
        if self.no_fs:
            self.adv.fs = self.act_off
        if self.no_dodge:
            self.adv.dodge = self.act_off
    
    def on(self):
        if not self.active:
            if self.zeroed is not None:
                self.zeroed[0].index = self.zeroed[1]
                self.zeroed = None

            act = self.a_x_alt[1]
            doing = act._static.doing
            delay = 0
            if not doing.idle:
                try:
                    if doing.status == -1:
                        delay = doing.startup_timer.timing - now()
                    elif doing.status == 0:
                        delay = doing.getrecovery()
                    elif doing.status == 1:
                        delay = doing.recovery_timer.timing - now()
                except:
                    pass
            Timer(self.on_t).on(delay)
                
    def off(self):
        if self.active:
            log('debug', '{} x_alt off'.format(self.name))
            self.active = False
            self.adv.x = self.x_og
            if self.l_x_alt:
                self.l_x_alt.off()
                self.adv.l_x.on()
            if self.no_fs:
                self.adv.fs = self.fs_og
            if self.no_dodge:
                self.adv.dodge = self.dodge_og

            doing = self.a_x_alt[1]._static.doing
            self.zeroed = (doing, doing.index)
            doing.index = 0

    def switch_t(self, t):
        prev_x = t.prev_x_alt
        log('debug', '{} x_alt off'.format(prev_x.name))
        if prev_x.active:
            doing = prev_x.a_x_alt[1]._static.doing
            prev_x.zeroed = (doing, doing.index)
            doing.index = 0
            prev_x.active = False
            if prev_x.l_x_alt:
                prev_x.l_x_alt.off()
                prev_x.adv.l_x.on()
            if prev_x.no_fs:
                prev_x.adv.fs = prev_x.fs_og
            if prev_x.no_dodge:
                prev_x.adv.dodge = prev_x.dodge_og
        
        log('debug', '{} x_alt on'.format(self.name))
        self.active = True
        self.adv.x = self.x_alt
        if self.l_x_alt:
            self.adv.l_x.off()
            self.l_x_alt.on()
        if self.no_fs:
            self.adv.fs = self.act_off
        if self.no_dodge:
            self.adv.dodge = self.act_off

    def switch(self, prev_x_alt):
        if not self.active:
            if self.zeroed is not None:
                self.zeroed[0].index = self.zeroed[1]
                self.zeroed = None

            act = self.a_x_alt[1]
            doing = act._static.doing
            delay = 0
            if not doing.idle and isinstance(doing, X):
                try:
                    if doing.status == -1:
                        delay = doing.startup_timer.timing - now()
                    elif doing.status == 0:
                        delay = doing.getrecovery()
                    elif doing.status == 1:
                        delay = doing.recovery_timer.timing - now()
                except:
                    pass
            t = Timer(self.switch_t)
            t.prev_x_alt = prev_x_alt
            t.on(delay)
