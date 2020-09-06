import operator
import sys
import random
from functools import reduce
from itertools import product
from collections import OrderedDict

from ability import Ability
from core import *
from core.timeline import *
from core.log import *
from core.afflic import *
from core.dummy import Dummy, dummy_function
import core.acl_old
import conf as globalconf
import slot
from ctypes import c_float
from math import ceil
from core.condition import Condition


class ModifierDict(defaultdict):
    def __init__(self, *args, **kwargs):
        if args:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(lambda: defaultdict(lambda: []))

    def append(self, modifier):
        self[modifier.mod_type][modifier.mod_order].append(modifier)

    def remove(self, modifier):
        self[modifier.mod_type][modifier.mod_order].remove(modifier)


class Modifier(object):
    _static = Static({
        'all_modifiers': ModifierDict(),
        'g_condition': None,
        'damage_sources': set()
    })

    def __init__(self, name, mtype, order, value, condition=None, get=None):
        self.mod_name = name
        self.mod_type = mtype
        self.mod_order = order
        self.mod_value = value
        self.mod_condition = condition
        self.mod_get = get
        self._mod_active = 0
        self.on()
        # self._static.all_modifiers.append(self)
        # self.__active = 1

    @classmethod
    def mod(cls, mtype, all_modifiers=None, morder=None):
        if not all_modifiers:
            all_modifiers = cls._static.all_modifiers
        if morder:
            return 1 + sum([modifier.get() for modifier in all_modifiers[mtype][morder]])
        m = defaultdict(lambda: 1)
        for order, modifiers in all_modifiers[mtype].items():
            m[order] += sum([modifier.get() for modifier in modifiers])
        ret = 1.0
        for i in m:
            ret *= m[i]
        return ret

    def get(self):
        if callable(self.mod_get) and not self.mod_get():
            return 0
        if self.mod_condition is not None and not self._static.g_condition(self.mod_condition):
            return 0
        return self.mod_value

    def on(self, modifier=None):
        if self._mod_active == 1:
            return self
        if modifier == None:
            modifier = self
        # if modifier.mod_condition:
        #     if not m_condition.on(modifier.mod_condition):
        #         return self
        if modifier.mod_condition is not None:
            if not self._static.g_condition(modifier.mod_condition):
                return self

        self._static.all_modifiers.append(self)
        self._mod_active = 1
        return self

    def off(self, modifier=None):
        if self._mod_active == 0:
            return self
        self._mod_active = 0
        if modifier == None:
            modifier = self
        self._static.all_modifiers.remove(self)
        return self

    def __enter__(self):
        self.on()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.off()

    def __repr__(self):
        return '<%s %s %s %s>' % (self.mod_name, self.mod_type, self.mod_order, self.mod_value)


class KillerModifier(Modifier):
    def __init__(self, name, order, value, killer_condition):
        self.killer_condition = killer_condition
        super().__init__(name, f"{killer_condition}_killer", order, value)

    def on(self, modifier=None):
        if self._mod_active == 1:
            return self
        if modifier == None:
            modifier = self
        if modifier.mod_condition is not None:
            if not self._static.g_condition(modifier.mod_condition):
                return self

        for kcondition in self.killer_condition:
            self._static.all_modifiers[f"{kcondition}_killer"][self.mod_order].append(modifier)
        self._mod_active = 1
        return self

    def off(self, modifier=None):
        if self._mod_active == 0:
            return self
        self._mod_active = 0
        if modifier == None:
            modifier = self
        for kcondition in self.killer_condition:
            self._static.all_modifiers[f"{kcondition}_killer"][self.mod_order].remove(self)
        return self


class CrisisModifier(Modifier):
    def __init__(self, name, scale, hp):
        super().__init__('mod_{}_crisis'.format(name), 'att', 'hit', 0)
        self.hp_scale = scale
        self.hp_lost = 100 - hp
        if hp < 100:
            self.hp_cond = self._static.g_condition.hp_cond_set(hp)
        else:
            self.hp_cond = False

    def get(self):
        if self.hp_cond:
            self.mod_value = self.hp_scale * (self.hp_lost ** 2) / 10000
        else:
            self.mod_value = 0
        return self.mod_value


class MultiBuffManager:
    def __init__(self, buffs):
        self.buffs = buffs

    def on(self):
        for b in self.buffs:
            b.on()
        return self

    def off(self):
        for b in self.buffs:
            b.off()
        return self

    def get(self):
        return all(map(lambda b: b.get(), self.buffs))


class Buff(object):
    _static = Static({
        'all_buffs': [],
        'bufftime': lambda: 1,
        'debufftime': lambda: 1
    })

    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='att', morder=None, modifier=None):
        self.name = name
        self.__value = value
        self.duration = duration
        self.mod_type = mtype
        self.mod_order = morder or ('chance' if self.mod_type == 'crit' else 'buff')
        self.bufftype = 'self'

        self.bufftime = self._bufftime if self.duration > 0 else self._no_bufftime
        self.buff_end_timer = Timer(self.buff_end_proc)
        if modifier:
            self.modifier = modifier
            self.get = self.modifier.get
        else:
            self.modifier = Modifier('mod_' + self.name, self.mod_type, self.mod_order, 0)
            self.modifier.get = self.get
        self.dmg_test_event = Event('dmg_formula')
        self.dmg_test_event.dmg_coef = 1
        self.dmg_test_event.dname = 'test'

        self.__stored = 0
        self.__active = 0
        # self.on()

    def _no_bufftime(self):
        return 1

    def _bufftime(self):
        return self._static.bufftime()

    def _debufftime(self):
        return self._static.debufftime()

    def no_bufftime(self):
        self.bufftime = self._no_bufftime
        return self

    def zone(self):
        self.bufftime = self._no_bufftime
        self.name += '_zone'
        return self

    def value(self, newvalue=None):
        if newvalue:
            return self.set(newvalue)
        else:
            return self.get()

    def get(self):
        if self.__active:
            return self.__value
        else:
            return 0

    def set(self, v, d=None):
        self.__value = v
        if d != None:
            self.duration = d
        return self

    def stack(self):
        stack = 0
        for i in self._static.all_buffs:
            if i.name == self.name:
                if i.__active != 0:
                    stack += 1
        return stack

    def valuestack(self):
        stack = 0
        value = 0
        for i in self._static.all_buffs:
            if i.name == self.name:
                if i.__active != 0:
                    stack += 1
                    value += i.__value
        return value, stack

    def effect_on(self):
        return self.modifier.on()

    def effect_off(self):
        return self.modifier.off()

    def buff_end_proc(self, e):
        log('buff', self.name, f'{self.mod_type}({self.mod_order}): {self.value():.02f}', f'{self.name} buff end <timeout>')
        self.__active = 0

        if self.__stored:
            idx = len(self._static.all_buffs)
            while 1:
                idx -= 1
                if idx < 0:
                    break
                if self == self._static.all_buffs[idx]:
                    self._static.all_buffs.pop(idx)
                    break
            self.__stored = 0
        value, stack = self.valuestack()
        if stack > 0:
            log('buff', self.name, f'{self.mod_type}({self.mod_order}): {value:.02f}', f'{self.name} buff stack <{stack}>')
        self.effect_off()

    def count_team_buff(self):
        self.dmg_test_event.modifiers = ModifierDict()

        base_mods = [
            Modifier('base_cc', 'crit', 'chance', 0.12),
            Modifier('base_killer', 'killer','passive', 0.50)
        ]

        for mod in base_mods:
            self.dmg_test_event.modifiers.append(mod)

        for i in self._static.all_buffs:
            if i.name == 'simulated_def':
                self.dmg_test_event.modifiers.append(i.modifier)
        self.dmg_test_event()
        no_team_buff_dmg = self.dmg_test_event.dmg
        sd_mods = 1
        spd = 0
        for i in self._static.all_buffs:
            if i.bufftype == 'team' or i.bufftype == 'debuff':
                if i.modifier.mod_type == 's':
                    sd_mods += i.get() * 1 / 2
                elif i.modifier.mod_type == 'spd':
                    spd += i.get()
                else:
                    if i.modifier.mod_type.endswith('_killer'):
                        mod_copy = copy.copy(i.modifier)
                        mod_copy.mod_type = 'killer'
                        self.dmg_test_event.modifiers.append(i.modifier)
                    else:
                        self.dmg_test_event.modifiers.append(i.modifier)
        self.dmg_test_event()
        team_buff_dmg = self.dmg_test_event.dmg * sd_mods
        team_buff_dmg += team_buff_dmg * spd
        log('buff', 'team', team_buff_dmg / no_team_buff_dmg - 1)

        for mod in base_mods:
            mod.off()

    def on(self, duration=None):
        if duration == None:
            d = self.duration * self.bufftime()
        else:
            d = duration * self.bufftime()
        if self.__active == 0:
            self.__active = 1
            if self.__stored == 0:
                self._static.all_buffs.append(self)
                self.__stored = 1
            if d >= 0:
                self.buff_end_timer.on(d)
            log('buff', self.name, f'{self.mod_type}({self.mod_order}): {self.value():.02f}', f'{self.name} buff start <{d:.02f}s>')
        else:
            if d >= 0:
                self.buff_end_timer.on(d)
                log('buff', self.name, f'{self.mod_type}({self.mod_order}): {self.value():.02f}', f'{self.name} buff refresh <{d:.02f}s>')

        value, stack = self.valuestack()
        if stack > 1:
            log('buff', self.name, f'{self.mod_type}({self.mod_order}): {value:.02f}', f'{self.name} buff stack <{stack}>')


        if self.mod_type == 'defense':
            Event('defchain').on()
            if self.bufftype == 'team':
                log('buff', 'team_defense', 'proc team doublebuffs')

        if self.mod_type == 'regen':
            # may need to make this part global since game always regen all stacks at same ticks
            self.set_hp_event = Event('set_hp')
            self.set_hp_event.delta = self.get()
            self.modifier = Timer(self.hp_regen, 3.9, True) # hax

        self.effect_on()
        return self

    def hp_regen(self, t):
        self.set_hp_event()

    def off(self):
        if self.__active == 0:
            return
        log('buff', self.name, f'{self.mod_type}({self.mod_order}): {self.value():.02f}', f'{self.name} buff end <turn off>')
        self.__active = 0
        self.modifier.off()
        self.buff_end_timer.off()
        return self


class EffectBuff(Buff):
    def __init__(self, name, duration, effect_on, effect_off):
        Buff.__init__(self, name, 1, duration, 'special', 'effect')
        self.bufftype = 'self'
        self.effect_on = effect_on
        self.effect_off = effect_off


class Selfbuff(Buff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='att', morder=None):
        Buff.__init__(self, name, value, duration, mtype, morder)
        self.bufftype = 'self'


class SingleActionBuff(Buff):
    # self buff lasts until the action it is buffing is completed
    def __init__(self, name='<buff_noname>', value=0, casts=1, mtype='att', morder=None, event=None, end_proc=None):
        super().__init__(name, value, -1, mtype, morder)
        self.bufftype = 'self'
        self.casts = casts
        self.end_event = event if event is not None else mtype
        self.end_proc = end_proc
        if isinstance(self.end_event, str):
            Listener(self.end_event, self.l_off, after=True).on()
        else:
            for e in self.end_event:
                Listener(e, self.l_off, after=True).on()

    def on(self, casts=1):
        self.casts = casts
        return super().on(-1)

    def l_off(self, e):
        if (e.name in self.modifier._static.damage_sources
            or (e.name.startswith('fs') and 'fs' in self.modifier._static.damage_sources)
            or (hasattr(e, 'damage') and e.damage)):
            self.casts -= 1
            if self.casts <= 0:
                result = super().off()
                if self.end_proc is not None:
                    self.end_proc(e)
                return result
            else:
                return self


class Teambuff(Buff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='att', morder=None):
        Buff.__init__(self, name, value, duration, mtype, morder)
        self.bufftype = 'team'

        self.base_cc_mod = []
        for mod in self.modifier._static.all_modifiers['crit']['chance']:
            if mod.mod_name.startswith('w_') or mod.mod_name.startswith('c_ex'):
                self.base_cc_mod.append(mod)

    def on(self, duration=None):
        Buff.on(self, duration)
        self.count_team_buff()
        return self

    def off(self):
        Buff.off(self)
        self.count_team_buff()
        return self

    def buff_end_proc(self, e):
        Buff.buff_end_proc(self, e)
        self.count_team_buff()


class Spdbuff(Buff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='spd', morder=None, wide='self'):
        mtype = mtype
        morder = 'passive'
        Buff.__init__(self, name, value, duration, mtype, morder)
        self.bufftype = wide

    def on(self, duration=None):
        Buff.on(self, duration)
        if self.bufftype == 'team':
            self.count_team_buff()
        return self

    def off(self):
        Buff.off(self)
        if self.bufftype == 'team':
            self.count_team_buff()
        return self

    def buff_end_proc(self, e):
        Buff.buff_end_proc(self, e)
        if self.bufftype == 'team':
            self.count_team_buff()


class Debuff(Teambuff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, chance=1.0, mtype='def', morder=None):
        self.val = 0 - value
        self.chance = chance
        if self.chance != 1:
            bd = 1.0 / (1.0 + self.val)
            bd = (bd - 1) * self.chance + 1
            self.val = 1 - 1.0 / bd
            self.val = 0 - self.val
        Teambuff.__init__(self, name, self.val, duration, mtype, morder)
        self.bufftype = 'debuff'
        self.bufftime = self._debufftime


class Skill(object):
    _static = Static({
        's_prev': '<nop>',
        'first_x_after_s': 0,
        'silence': 0,
    })
    charged = 0
    sp = 0
    silence_duration = 1.9
    name = '_Skill'
    owner = None # indicates self/weapon skill

    def __init__(self, name=None, conf=None, ac=None):
        self.charged = 0
        self.name = name
        self.conf = conf
        self.ac = ac or S(self.name, self.conf)

        self._static.silence = 0
        self.silence_end_timer = Timer(self.cb_silence_end)
        self.silence_end_event = Event('silence_end')
        self.skill_charged = Event('{}_charged'.format(self.name))
        self.init()

    @property
    def sp(self):
        return self.conf.sp

    def __call__(self):
        return self.cast()

    def init(self):
        pass

    def charge(self, sp):
        self.charged = max(min(self.sp, self.charged + sp), 0)
        if self.charged >= self.sp:
            self.skill_charged()

    def cb_silence_end(self, e):
        if loglevel >= 2:
            log('silence', 'end')
        self._static.silence = 0
        self.silence_end_event()

    def check(self):
        if self.sp == 0:
            return 0
        elif self._static.silence == 1:
            return 0
        elif self.charged >= self.sp:
            return 1
        else:
            return 0

    def cast(self):
        if not self.check():
            return 0
        else:
            if not self.ac():
                return 0
            self.charged -= self.sp
            self._static.s_prev = self.name
            # Even if animation is shorter than 1.9, you can't cast next skill before 1.9
            self.silence_end_timer.on(self.silence_duration)
            self._static.silence = 1
            if loglevel >= 2:
                log('silence', 'start')
            return 1

    def autocharge_init(self, sp, iv=1):
        if callable(sp):
            self.autocharge_timer = Timer(sp, iv, 1)
        else:
            if sp < 1:
                sp = int(sp * self.sp)
            def autocharge(t):
                if self.charged < self.sp:
                    self.charge(sp)
                    log('sp', self.name+'_autocharge', int(sp))
            self.autocharge_timer = Timer(autocharge, iv, 1)
        return self.autocharge_timer


class Action(object):
    _static = Static({
        'prev': 0,
        'doing': 0,
        'spd_func': 0,
        'c_spd_func': 0,
    })
    OFF = -2
    STARTUP = -1
    DOING = 0
    RECOVERY = 1

    name = '_Action'
    index = 0
    recover_start = 0
    startup_start = 0
    status = -2
    idle = 0

    class Nop(object):
        name = '__idle__'
        index = 0
        status = -2
        idle = 1

    nop = Nop()

    def __init__(self, name=None, conf=None, act=None):  ## can't change name after self
        if name != None:
            if type(name) == tuple:
                self.name = name[0]
                self.index = name[1]
            else:
                self.name = name
                self.index = 0
            self.atype = self.name

        self.conf = conf

        if act != None:
            self.act = act

        if not self._static.spd_func:
            self._static.spd_func = self.nospeed
        if not self._static.c_spd_func:
            self._static.c_spd_func = self.nospeed
        if not self._static.doing:
            self._static.doing = self.nop
        if not self._static.prev:
            self._static.prev = self.nop

        self.cancel_by = []
        self.interrupt_by = []

        self.startup_timer = Timer(self._cb_acting)
        self.recovery_timer = Timer(self._cb_act_end)
        self.idle_event = Event('idle')
        self.act_event = Event(self.name)
        self.realtime()

    def __call__(self):
        return self.tap()

    def getdoing(self):
        return self._static.doing

    def _setdoing(self):
        self._static.doing = self

    def getprev(self):
        return self._static.prev

    def _setprev(self):
        self._static.prev = self._static.doing

    def rt_tap(self):
        if self.rt_name != self.name:
            if self.atype == self.rt_name:
                self.atype = self.name
            self.rt_name = self.name
            self.act_event = Event(self.name)
        return self.o_tap()

    def realtime(self):
        self.rt_name = self.name
        self.tap, self.o_tap = self.rt_tap, self.tap

    @property
    def _startup(self):
        return self.conf.startup

    @property
    def _recovery(self):
        return self.conf.recovery

    def getrecovery(self):
        return self._recovery / self.speed()

    def getstartup(self):
        return self._startup / self.speed()

    def nospeed(self):
        return 1

    def speed(self):
        return self._static.spd_func()

    def _cb_acting(self, e):
        if self.getdoing() == self:
            self.status = 0
            self._act(1)
            self.status = Action.RECOVERY
            self.recover_start = now()
            self.recovery_timer.on(self.getrecovery())

    def _cb_act_end(self, e):
        if self.getdoing() == self:
            if loglevel >= 2:
                log('ac_end', self.name)
            self.status = Action.OFF
            self._setprev()  # turn self from doing to prev
            self._static.doing = self.nop
            self.idle_event()

    def _act(self, partidx):
        self.idx = partidx
        if loglevel >= 2:
            log('act', self.name)
        self.act(self)

    def act(self, action):
        self.act_event.name = self.name
        self.act_event.idx = self.idx
        self.act_event()

    def tap(self):
        doing = self._static.doing

        if doing.idle:
            if loglevel >= 2:
                log('tap', self.name, self.atype, f'idle {doing.status}')
        else:
            if loglevel >= 2:
                log('tap', self.name, self.atype, f'doing {doing.name}:{doing.status}')

        if doing == self:  # self is doing
            return 0

        # if doing.idle # idle
        #    pass
        if not doing.idle:  # doing != self
            if doing.status == Action.STARTUP:  # try to interrupt an action
                if self.atype in doing.interrupt_by:  # can interrupt action
                    doing.startup_timer.off()
                    log('interrupt', doing.name, f'by {self.name}', f'after {now() - doing.startup_start:.2f}s')
                else:
                    return 0
            elif doing.status == Action.RECOVERY:  # try to cancel an action
                if self.atype in doing.cancel_by:  # can interrupt action
                    doing.recovery_timer.off()
                    log('cancel', doing.name, f'by {self.name}', f'after {now() - doing.recover_start:.2f}s')
                else:
                    return 0
            elif doing.status == 0:
                raise Exception(f'Illegal action {doing} -> {self}')
            self._setprev()
        self.status = Action.STARTUP
        self.startup_start = now()
        self.startup_timer.on(self.getstartup())
        self._setdoing()
        if now() <= 3:
            log('debug', 'tap', 'startup', self.getstartup())
        return 1


class X(Action):
    def __init__(self, name, conf, act=None):
        Action.__init__(self, name, conf, act)
        self.atype = 'x'
        self.interrupt_by = ['fs', 's', 'dodge']
        self.cancel_by = ['fs', 's', 'dodge']

    def realtime(self):
        self.act_event = Event('x')
        self.act_event.name = self.name
        self.rt_name = self.name
        self.tap, self.o_tap = self.rt_tap, self.tap

    def rt_tap(self):
        if self.rt_name != self.name:
            if self.atype == self.rt_name:
                self.atype = self.name
            self.rt_name = self.name
            self.act_event.name = self.name
        return self.o_tap()


class Fs(Action):
    def __init__(self, name, conf, act=None):
        Action.__init__(self, name, conf, act)
        self.atype = 'fs'
        self.interrupt_by = ['s']
        self.cancel_by = ['s', 'dodge']

    @property
    def _charge(self):
        return self.conf.charge

    def charge_speed(self):
        return self._static.c_spd_func()

    def getstartup(self):
        return (self._charge / self.charge_speed()) + (self._startup / self.speed())

    def realtime(self):
        self.act_event = Event('fs')
        self.act_event.name = self.name


class Fs_group(object):
    def __init__(self, name, conf, act=None):
        self.actions = {}
        self.conf = conf
        fsconf = conf[name]
        xnfsconf = {}

        self.add('default', Fs(name, fsconf, act))
        for i in range(1, conf.x_max+1):
            xnfs = f'x{i}{name}'
            if self.conf[xnfs] is not None:
                xnfsconf = fsconf+(self.conf[xnfs])
            else:
                xnfsconf = fsconf
            self.add(f'x{i}', Fs(name, xnfsconf, act))
        if 'dfs' in self.conf:
            dfsconf = fsconf+self.conf.dfs
            self.add('dodge', Fs(name, dfsconf, act))

    def add(self, name, action):
        self.actions[name] = action

    def __call__(self, before):
        if before in self.actions:
            return self.actions[before]()
        else:
            return self.actions['default']()


class FS_MH(Action):
    def __init__(self, name, conf, act=None):
        Action.__init__(self, name, conf, act)
        self.atype = 'fs'
        self.interrupt_by = ['s']
        self.cancel_by = ['s','dodge']
        self._charge = self.conf.charge

    def act(self, action):
        self.act_event.name = self.name
        self.act_event.idx = self.idx
        self.act_event()

    def getstartup(self):
        return self._charge + (self._startup / self.speed())


class S(Action):
    def __init__(self, name, conf, act=None):
        Action.__init__(self, name, conf, act)
        self.atype = 's'
        self.interrupt_by = []
        self.cancel_by = []

    def realtime(self):
        self.act_event = Event('s')
        self.act_event.name = self.name


class Dodge(Action):
    def __init__(self, name, conf, act=None):
        Action.__init__(self, name, conf, act)
        self.atype = 'dodge'
        self.cancel_by = ['fs', 's']

    def realtime(self):
        self.act_event = Event('dodge')
        self.act_event.name = self.name

    def getstartup(self):
        return self._startup

    def getrecovery(self):
        return self._recovery


class Adv(object):
    Timer = Timer
    Event = Event
    Listener = Listener
    # vvvvvvvvv rewrite self to provide advanced tweak vvvvvvvvvv
    name = None

    def s1_proc(self, e):
        pass

    def s2_proc(self, e):
        pass

    def s3_proc(self, e):
        pass

    def s4_proc(self, e):
        pass

    def s_proc(self, e):
        pass

    def x_proc(self, e):
        pass

    def fs_proc(self, e):
        pass

    def dmg_proc(self, name, amount):
        pass

    def s1_before(self, e):
        pass

    def s2_before(self, e):
        pass

    def s3_before(self, e):
        pass

    def s4_before(self, e):
        pass

    def s_before(self, e):
        pass

    def x_before(self, e):
        pass

    def fs_before(self, e):
        pass

    def dmg_before(self, name, amount):
        pass

    def speed(self):
        return 1

    def init(self):
        pass

    def d_coabs(self):
        pass

    def d_slots(self):
        pass

    def d_skillshare(self):
        pass

    def slot_backdoor(self):
        pass

    def prerun(self):
        pass

    @staticmethod
    def prerun_skillshare(adv, dst):
        pass

    # ^^^^^^^^^ rewrite these to provide advanced tweak ^^^^^^^^^^

    comment = ''
    conf = None
    a1 = None
    a2 = None
    a3 = None

    skill_default = {'dmg': 0, 'hit': 0, 'recovery': 1.8, 'sp': 0, 'startup': 0.1}
    conf_default = {
        # Latency represents the human response time, between when an event
        # triggers a "think" event, and when the human actually triggers
        # the input.  Right now it's set to zero, which means "perfect"
        # response time (which is unattainable in reality.)
        'latency.x': 0,
        'latency.sp': 0,
        'latency.default': 0,
        'latency.idle': 0,

        'x_max': 5,

        's1': skill_default,
        's2': skill_default,
        's3': skill_default,
        's4': skill_default,

        'acl': '`s1;`s2;`s3'
    }

    def doconfig(self):

        # set buff
        self.action = Action()
        self.action._static.spd_func = self.speed
        self.action._static.c_spd_func = self.c_speed
        # set buff
        self.buff = Buff()
        self.all_buffs = []
        self.buff._static.all_buffs = self.all_buffs
        self.buff._static.bufftime = lambda: self.mod('buff')
        self.buff._static.debufftime = lambda: self.mod('debuff')
        # set modifier
        self.modifier = Modifier(0, 0, 0, 0)
        self.all_modifiers = ModifierDict()
        self.modifier._static.all_modifiers = self.all_modifiers
        self.modifier._static.g_condition = self.condition

        # init actions
        for n in range(1, self.conf.x_max+1):
            xn = f'x{n}'
            xconf = self.conf[xn]
            if xconf is not None:
                self.__setattr__(xn, X((xn, n), self.conf[xn]))

        self.a_fs = Fs_group('fs', self.conf)
        self.a_fsf = Fs('fsf', self.conf.fsf)
        self.a_fsf.act_event = Event('none')

        self.a_dodge = Dodge('dodge', self.conf.dodge)

        # skill init
        self.s1 = Skill('s1', self.conf.s1)
        self.s2 = Skill('s2', self.conf.s2)
        self.s3 = Skill('s3', self.conf.s3)
        self.s4 = Skill('s4', self.conf.s4)

        if self.conf.xtype == 'ranged':
            self.l_x = self.l_range_x
            self.l_fs = self.l_range_fs
        elif self.conf.xtype == 'melee':
            self.l_x = self.l_melee_x
            self.l_fs = self.l_melee_fs

        # set cmd
        self.fsf = self.a_fsf
        self.dodge = self.a_dodge
        # try:
        #     self.x5ex = X(('x5ex', 5), self.conf.x5ex)
        #     self.x5ex.atype = 'x'
        #     self.x5ex.interrupt_by = ['fs', 's', 'dodge']
        #     self.x5ex.cancel_by = ['fs', 's', 'dodge']
        #     self.x4.cancel_by.append('x')
        # except:
        #     pass

        self.hits = 0
        self.hp = 100
        self.hp_event = Event('hp')
        self.dragonform = None

        from module.tension import Energy, Inspiration
        self.energy = Energy()
        self.inspiration = Inspiration()
        self.tension = [self.energy, self.inspiration]

        self.disable_echo()

    def l_set_hp(self, e):
        try:
            self.set_hp(self.hp+e.delta)
        except AttributeError:
            self.set_hp(e.hp)

    def set_hp(self, hp):
        old_hp = self.hp
        hp = round(hp*10)/10
        self.hp = max(min(hp, 100), 0)
        if self.hp != old_hp:
            delta = self.hp-old_hp
            if self.hp == 0:
                log('hp', f'=1', f'{delta/100:.0%}')
            else:
                log('hp', f'{self.hp/100:.0%}', f'{delta/100:.0%}')
            self.condition.hp_cond_set(self.hp)
            self.hp_event.hp = self.hp
            self.hp_event.delta = delta
            self.hp_event()
            if 'hp' in self.conf and self.hp != self.conf['hp']:
                self.set_hp(self.conf['hp'])

    def buff_max_hp(self, name='<hp_buff>', value=0, team=False):
        max_hp = self.mod('maxhp')
        mod_val = min(value, max(1.30-max_hp, 0))
        if mod_val > 0:
            if team:
                buff = Teambuff(name, mod_val, -1, 'maxhp', 'buff').on()
            else:
                buff = Selfbuff(name, mod_val, -1, 'maxhp', 'buff').on()
        else:
            buff = None
        self.set_hp((self.hp*max_hp+value*100)/(max_hp+mod_val))
        return buff

    def afflic_condition(self):
        if 'afflict_res' in self.conf:
            res_conf = self.conf.afflict_res
            for afflic in AFFLICT_LIST:
                if afflic in res_conf and 0 <= res_conf[afflic] <= 100:
                    if self.condition('{} {} res'.format(res_conf[afflic], afflic)):
                        vars(self.afflics)[afflic].resist = res_conf[afflic]
                    else:
                        vars(self.afflics)[afflic].resist = 100

    def sim_affliction(self):
        if 'sim_afflict' in self.conf:
            for aff_type in AFFLICT_LIST:
                aff = vars(self.afflics)[aff_type]
                if self.conf.sim_afflict[aff_type]:
                    aff.get_override = min(self.conf.sim_afflict[aff_type], 1.0)
                    self.sim_afflict.add(aff_type)

    def sim_buffbot(self):
        if 'sim_buffbot' in self.conf:
            if 'def_down' in self.conf.sim_buffbot:
                value = -self.conf.sim_buffbot.def_down
                if self.condition('boss def {:+.0%}'.format(value)):
                    buff = self.Selfbuff('simulated_def', value, -1, mtype='def')
                    buff.chance = 1
                    buff.val = value
                    buff.on()
            if 'str_buff' in self.conf.sim_buffbot:
                if self.condition('team str {:+.0%}'.format(self.conf.sim_buffbot.str_buff)):
                    self.Selfbuff('simulated_att', self.conf.sim_buffbot.str_buff, -1).on()
            if 'critr' in self.conf.sim_buffbot:
                if self.condition('team crit rate {:+.0%}'.format(self.conf.sim_buffbot.critr)):
                    self.Selfbuff('simulated_crit_rate', self.conf.sim_buffbot.critr, -1, 'crit', 'rate').on()
            if 'critd' in self.conf.sim_buffbot:
                if self.condition('team crit dmg {:+.0%}'.format(self.conf.sim_buffbot.critd)):
                    self.Selfbuff('simulated_crit_dmg', self.conf.sim_buffbot.critd, -1, 'crit', 'dmg').on()
            if 'echo' in self.conf.sim_buffbot:
                if self.condition('echo att {:g}'.format(self.conf.sim_buffbot.echo)):
                    self.enable_echo(fixed_att=self.conf.sim_buffbot.echo)
            if 'doublebuff_interval' in self.conf.sim_buffbot:
                interval = round(self.conf.sim_buffbot.doublebuff_interval, 2)
                if self.condition('team doublebuff every {:.2f} sec'.format(interval)):
                    Event('defchain').on()
                    Timer(lambda t: Event('defchain').on(), interval, True).on()

    def config_slots(self):
        for s in ('c', 'd', 'w', 'a'):
            self.slots.__dict__[s] = self.cmnslots.__dict__[s]

        if self.conf['slots']:
            if not self.conf['flask_env']:
                self.d_slots()
            for s in ('c', 'd', 'w', 'a'):
                if self.conf.slots[s]:
                    # TODO: make this bit support string names
                    self.slots.__dict__[s] = self.conf.slots[s]
            if self.conf['flask_env']:
                return

        if self.sim_afflict:
            from conf.slot_common import ele_punisher
            aff, wpa = ele_punisher[self.slots.c.ele]
            wp1 = self.slots.a.__class__
            wp2 = wpa
            if wp1 != wp2:
                self.slots.a = wp1()+wp2()
            if self.conf[f'slots.{aff}']:
                afflic_slots = self.conf[f'slots.{aff}']
                for s in ('d', 'w', 'a'):
                    if afflic_slots[s]:
                        self.slots.__dict__[s] = afflic_slots[s]

    def pre_conf(self):
        tmpconf = Conf(self.conf_default)
        tmpconf.update(globalconf.get(self.name))
        tmpconf.update(self.conf)
        tmpconf.update(self.conf_init)
        self.conf = tmpconf

    def default_slot(self):
        from conf import slot_common
        self.cmnslots = slot.Slots()
        self.cmnslots.c.att = self.conf.c.att
        self.cmnslots.c.wt = self.conf.c.wt
        self.cmnslots.c.stars = self.conf.c.stars
        self.cmnslots.c.ele = self.conf.c.ele
        self.cmnslots.c.name = self.name
        self.slot_common = slot_common.set
        self.slot_common(self.cmnslots)
        self.slots = self.cmnslots

    def __init__(self, conf={}, cond=None):
        if not self.name:
            self.name = self.__class__.__name__

        self.Event = Event
        self.Buff = Buff
        self.Debuff = Debuff
        self.Selfbuff = Selfbuff
        self.Teambuff = Teambuff
        self.Modifier = Modifier
        self.Conf = Conf

        self.conf_init = conf
        self.ctx = Ctx().on()
        self.condition = Condition(cond)
        self.duration = 180

        self.s3_buff_list = []
        self.s3_buff = None

        self.damage_sources = set()
        self.phase = {}
        self.Modifier._static.damage_sources = self.damage_sources

        self.pre_conf()

        # set afflic
        self.afflics = Afflics()
        self.sim_afflict = set()
        self.afflic_condition()
        self.sim_affliction()

        self.default_slot()

        self.crit_mod = self.solid_crit_mod
        # self.crit_mod = self.rand_crit_mod

        self.skill = Skill()
        # self._acl = None

        # self.classconf = self.conf
        self.init()

        # self.ctx.off()

    def dmg_mod(self, name):
        mod = 1
        scope = name.split('_')
        if scope[0] == 'o':
            scope = scope[1]
        else:
            scope = scope[0]

        if scope[0] == 's':
            try:
                mod = 1 if self.__getattribute__(scope).owner is None else self.skill_share_att
            except:
                pass
            return mod * self.mod('s')
        elif scope[0:2] == 'fs':
            return mod * self.mod('fs')
        elif scope[0] == 'x':
            return mod * self.mod('x')
        else:
            return mod

    def mod(self, mtype):
        return reduce(operator.mul, [self.sub_mod(mtype, order) for order in self.all_modifiers[mtype].keys()], 1)

    def sub_mod(self, mtype, morder):
        mod_sum = sum([modifier.get() for modifier in self.all_modifiers[mtype][morder]])
        if morder == 'buff':
            mod_sum = min(mod_sum, 2.00)
        return 1 + mod_sum

    def speed(self):
        return min(self.mod('spd'), 1.50)

    def c_speed(self):
        return min(self.mod('cspd'), 1.50)

    def enable_echo(self, mod=None, fixed_att=None):
        self.echo = 2
        self.echo_att = fixed_att or (mod * self.base_att * self.modifier.mod('att'))
        log('debug', 'echo_att', self.echo_att)

    def disable_echo(self):
        self.echo = 1
        self.echo_att = 0

    def dmg_formula_echo(self, coef):
        # so 5/3(Bonus Damage amount)/EnemyDef +/- 5%
        armor = 10 * self.def_mod()
        return 5/3 * (self.echo_att * coef) / armor

    def crit_mod(self):
        return 1

    def combine_crit_mods(self):
        m = {'chance': 0, 'dmg': 0, 'damage': 0, 'passive': 0, 'rate': 0 }
        for order, modifiers in self.all_modifiers['crit'].items():
            for modifier in modifiers:
                if order in m:
                    m[order] += modifier.get()
                else:
                    raise ValueError(f"Invalid crit mod order {order}")

        rate_list = self.build_rates()
        for mask in product(*[[0, 1]] * len(rate_list)):
            p = 1.0
            modifiers = defaultdict(lambda: set())
            for i, on in enumerate(mask):
                cond = rate_list[i]
                cond_name = cond[0]
                cond_p = cond[1]
                if on:
                    p *= cond_p
                    for order, mods in self.all_modifiers[f'{cond_name}_crit'].items():
                        for mod in mods:
                            modifiers[order].add(mod)
                else:
                    p *= 1 - cond_p
            # total += p * reduce(operator.mul, [1 + sum([mod.get() for mod in order]) for order in modifiers.values()], 1.0)
            for order, values in modifiers.items():
                m[order] += p * sum([mod.get() for mod in values])

        chance = min(m['chance'] + m['passive'] + m['rate'], 1)
        cdmg = m['dmg'] + m['damage'] + 1.7

        return chance, cdmg

    def solid_crit_mod(self, name=None):
        chance, cdmg = self.combine_crit_mods()
        average = chance * (cdmg - 1) + 1
        return average

    def rand_crit_mod(self, name=None):
        chance, cdmg = self.combine_crit_mods()
        r = random.random()
        if r < chance:
            return cdmg
        else:
            return 1

    def att_mod(self, name=None):
        att = self.mod('att')
        cc = self.crit_mod(name)
        k = self.killer_mod(name)
        return cc * att * k

    def build_rates(self):
        rates = {}
        for afflic in AFFLICT_LIST:
            rate = vars(self.afflics)[afflic].get()
            if rate > 0:
                rates[afflic] = rate

        debuff_rates = {}
        for buff in self.all_buffs:
            if buff.get() and (buff.bufftype == 'debuff' or buff.name == 'simulated_def') and buff.val < 0:
                dkey = f'debuff_{buff.mod_type}'
                try:
                    debuff_rates[dkey] *= (1 - buff.chance)
                except:
                    debuff_rates[dkey] = 1 - buff.chance
                try:
                    debuff_rates['debuff'] *= (1 - buff.chance)
                except:
                    debuff_rates['debuff'] = 1 - buff.chance
        for dkey in debuff_rates.keys():
            debuff_rates[dkey] = 1 - debuff_rates[dkey]
        rates.update(debuff_rates)

        return list(rates.items())

    def killer_mod(self, name=None):
        total = self.mod('killer') - 1
        rate_list = self.build_rates()
        for mask in product(*[[0, 1]] * len(rate_list)):
            p = 1.0
            modifiers = defaultdict(lambda: set())
            for i, on in enumerate(mask):
                cond = rate_list[i]
                cond_name = cond[0]
                cond_p = cond[1]
                if on:
                    p *= cond_p
                    for order, mods in self.all_modifiers[f"{cond_name}_killer"].items():
                        for mod in mods:
                            modifiers[order].add(mod)
                else:
                    p *= 1 - cond_p
            total += p * reduce(operator.mul, [1 + sum([mod.get() for mod in order]) for order in modifiers.values()], 1.0)
        return total

    def def_mod(self):
        return max(self.mod('def'), 0.5)

    def sp_mod(self, name):
        sp_mod = 1
        for order, modifiers in self.all_modifiers['sp'].items():
            if order == 'fs':
                if name.startswith('fs'):
                    sp_mod += sum([modifier.get() for modifier in modifiers])
            else:
                sp_mod += sum([modifier.get() for modifier in modifiers])
        return sp_mod

    def sp_val(self, param):
        if isinstance(param, str):
            return self.sp_convert(self.sp_mod(param), self.conf[param + '.sp'])
        elif isinstance(param, int) and 0 < param:
            return sum([self.sp_convert(self.sp_mod('x{}'.format(x)), self.conf['x{}.sp'.format(x)]) for x in range(1, param + 1)])

    def have_buff(self, name):
        for b in self.all_buffs:
            if b.name.startswith(name) and b.get():
                return True
        return False

    @property
    def buffcount(self):
        buffcount = reduce(lambda s, b: s+int(b.get() and b.bufftype in ('self', 'team')), self.all_buffs, 0)
        if self.conf['sim_buffbot.count'] is not None:
            buffcount += self.conf.sim_buffbot.count
        return buffcount

    def l_idle(self, e):
        """
        Listener that is called when there is nothing to do.
        """
        self.think_pin('idle')
        prev = self.action.getprev()
        if prev.name[0] == 's':
            self.think_pin(prev.name)
        if self.skill._static.first_x_after_s:
            self.skill._static.first_x_after_s = 0
            s_prev = self.skill._static.s_prev
            self.think_pin('%s-x' % s_prev)
        self.x()

    def getprev(self):
        prev = self.action.getprev()
        return prev.name, prev.index, prev.status

    def fs(self):
        doing = self.action.getdoing()
        return self.a_fs(doing.name)

    def x(self):
        prev = self.action.getprev()
        x_next = 1
        if prev.name[0] == 'x':
            if prev.index != self.conf.x_max:
                x_next = prev.index + 1
        return getattr(self, 'x%d' % x_next)()

    def l_range_x(self, e):
        xseq = e.name
        if xseq == f'x{self.conf.x_max}':
            log('x', xseq, 0, f'-------------------------------------c{self.conf.x_max}')
        else:
            log('x', xseq, 0)
        self.x_before(e)
        try:
            missile_iv = self.conf[f'missile_iv.{xseq}']
        except KeyError:
            missile_iv = 0
        missile_timer = Timer(self.cb_missile, missile_iv)
        # missile_timer.dname = '%s_missile' % xseq
        missile_timer.dname = xseq
        missile_timer.conf = self.conf[xseq]
        missile_timer()
        self.x_proc(e)
        self.think_pin('x')

    def cb_missile(self, t):
        self.add_hits(t.conf['hit'])
        self.dmg_make(t.dname, t.conf.dmg)
        self.charge(t.dname, t.conf.sp)

    def l_melee_x(self, e):
        xseq = e.name
        dmg_coef = self.conf[xseq].dmg
        sp = self.conf[xseq].sp
        hit = self.conf[xseq].hit
        if xseq == f'x{self.conf.x_max}':
            log('x', xseq, 0, f'-------------------------------------c{self.conf.x_max}')
        else:
            log('x', xseq, 0)
        self.x_before(e)
        self.add_hits(hit)
        self.dmg_make(xseq, dmg_coef)
        self.x_proc(e)
        self.think_pin('x')
        self.charge(xseq, sp)

    def dodge(self):
        return self.a_dodge()

    def l_dodge(self, e):
        log('dodge', '-')
        self.think_pin('dodge')

    def add_hits(self, hit):
        if hit is None:
            raise ValueError('none type hit')
        if hit >= 0:
            delta = hit*self.echo
            self.hits += hit*self.echo
            return delta
        self.hits = 0
        return 0

    def load_aff_conf(self, key):
        return self.conf[key] or []

    def config_coabs(self):
        if not self.conf['flask_env']:
            self.d_coabs()
        self.coab_list = self.load_aff_conf('coabs')
        from conf import coability_dict
        try:
            self_coab = list(self.slots.c.coabs.keys())[0]
        except:
            self_coab = self.__class__.__name__
        for name in self.coab_list:
            try:
                self.slots.c.coabs[name] = coability_dict(self.slots.c.ele)[name]
            except KeyError:
                raise ValueError(f'No such coability: {name}')
        self.coab_list = list(self.slots.c.coabs.keys())
        try:
            self.coab_list.remove(self_coab)
        except:
            pass

    def rebind_function(self, owner, src, dst=None):
        dst = dst or src
        self.__setattr__(dst, getattr(owner, src).__get__(self, self.__class__))

    @property
    def skills(self):
        return self.s1, self.s2, self.s3, self.s4

    def config_skillshare(self):
        if not self.conf['flask_env']:
            self.d_skillshare()
        preruns = {}
        self.skillshare_list = self.load_aff_conf('share')
        try:
            self.skillshare_list.remove(self.__class__.__name__)
        except ValueError:
            pass
        self.skillshare_list = list(OrderedDict.fromkeys(self.skillshare_list))
        if len(self.skillshare_list) > 2:
            self.skillshare_list = self.skillshare_list[:2]
        if len(self.skillshare_list) < 2:
            self.skillshare_list.insert(0, 'Weapon')
        from conf import advconfs, skillshare
        from core.simulate import load_adv_module
        share_limit = 10
        sp_modifier = 1
        self.skill_share_att = 0.7
        try:
            self_data = skillshare[self.__class__.__name__]
            try:
                share_limit = self_data['limit']
            except KeyError:
                pass
            try:
                sp_modifier = self_data['mod_sp']
            except KeyError:
                pass
            try:
                self.skill_share_att = self_data['mod_att']
            except KeyError:
                pass
        except KeyError:
            pass
        share_costs = 0
        for idx, owner in enumerate(self.skillshare_list):
            dst_key = f's{idx+3}'
            if owner == 'Weapon':
                self.conf.s3.update(self.slots.w.s3)
            else:
                # I am going to spaget hell for this
                sdata = skillshare[owner]
                try:
                    share_costs += sdata['cost']
                except KeyError:
                    # not allowed to share skill
                    continue
                if share_limit < share_costs:
                    raise ValueError(f'Skill share exceed cost {(*self.skillshare_list, share_costs)}.')
                src_key = f's{sdata["s"]}'
                shared_sp = self.sp_convert(sdata['sp'], sp_modifier)
                try:
                    owner_conf = Conf(advconfs[owner])
                    owner_conf[src_key].sp = shared_sp
                    self.conf[dst_key] = Conf(owner_conf[src_key])
                    s = Skill(dst_key, self.conf[dst_key])
                    s.owner = owner
                    self.__setattr__(dst_key, s)
                    owner_module = load_adv_module(owner)
                    preruns[dst_key] = owner_module.prerun_skillshare
                    self.rebind_function(owner_module, f'{src_key}_before', f'{dst_key}_before')
                    self.rebind_function(owner_module, f'{src_key}_proc', f'{dst_key}_proc')
                except:
                    self.conf[dst_key].sp = shared_sp
                    self.__getattribute__(dst_key).owner = owner
        return preruns

    def run(self, d=300):
        self.duration = d
        global loglevel
        if not loglevel:
            loglevel = 0

        self.ctx.on()
        self.doconfig()
        logreset()

        self.l_idle = Listener('idle', self.l_idle)
        self.l_x = Listener('x', self.l_x)
        self.l_dodge = Listener('dodge', self.l_dodge)
        self.l_fs = Listener('fs', self.l_fs)
        self.l_s = Listener('s', self.l_s)
        # self.l_x           = Listener(['x','x1','x2','x3','x4','x5'],self.l_x)
        # self.l_fs          = Listener(['fs','x1fs','x2fs','x3fs','x4fs','x5fs'],self.l_fs)
        # self.l_s           = Listener(['s','s1','s2','s3'],self.l_s)
        self.l_silence_end = Listener('silence_end', self.l_silence_end)
        self.l_dmg_make = Listener('dmg_make', self.l_dmg_make)
        self.l_true_dmg = Listener('true_dmg', self.l_true_dmg)
        self.l_dmg_formula = Listener('dmg_formula', self.l_dmg_formula)
        self.l_set_hp = Listener('set_hp', self.l_set_hp)

        self.ctx.on()
        
        # for ab in (self.a1, self.a2, self.a3):
        #     if ab:
        #         if isinstance(ab, list):
        #             self.slots.c.a.extend(ab)
        #         else:
        #             self.slots.c.a.append(ab)
        if self.conf.c.a:
            self.slots.c.a = list(self.conf.c.a)

        self.config_slots()
        self.slot_backdoor()

        self.config_coabs()
        preruns_ss = self.config_skillshare()

        self.base_att = 0

        self.sim_buffbot()

        self.base_att = int(self.slots.att(globalconf.halidom))
        self.slots.oninit(self)

        for dst_key, prerun in preruns_ss.items():
            prerun(self, dst_key)
        self.prerun()

        self.hp = self.condition.prev_hp
        if 'hp' in self.conf:
            self.set_hp(self.conf['hp'])

        if 'dragonbattle' in self.conf and self.conf['dragonbattle']:
            self.conf['acl'] = '`dragon'
            self.dragonform.set_dragonbattle(self.duration)

        self._acl = core.acl_old.acl_build(self.conf.acl)
        self._acl.prep(self)
        
        # if not self._acl:
        #     self._acl_str, self._acl = core.acl_old.acl_func_str(self.conf.acl)

        self.displayed_att = int(self.base_att * self.mod('att'))

        # from pprint import pprint
        # pprint(self.conf)

        Event('idle')()
        end, reason = Timeline.run(d)
        log('sim', 'end', reason)

        self.post_run()

        for aff, up in self.afflics.get_uptimes().items():
            if up > 0.10:
                if len(self.comment) > 0:
                    self.comment += '; '
                self.comment += '{:.0%} {} uptime'.format(up, aff)

        if g_logs.team_doublebuffs > 0:
            if len(self.comment) > 0:
                self.comment += '; '
            self.comment += f'{d/g_logs.team_doublebuffs:.2f}s team doublebuff interval'

        self.logs = copy.deepcopy(g_logs)

        return end

    def post_run(self):
        pass

    def debug(self):
        pass

    def think_pin(self, pin):
        # pin as in "signal", says what kind of event happened
        def cb_think(t):
            if loglevel >= 2:
                log('think', t.pin, t.dname, t.dstat, t.didx)
            self._acl(self, t)

        if pin in self.conf.latency:
            latency = self.conf.latency[pin]
        else:
            latency = self.conf.latency.default

        t = Timer(cb_think).on(latency)
        doing = self.action.getdoing()
        t.pin = pin
        t.dname = doing.name
        t.dstat = doing.status
        t.didx = doing.index

    def l_silence_end(self, e):
        doing = self.action.getdoing()
        sname = self.skill._static.s_prev
        if doing.name[0] == 'x':
            self.skill._static.first_x_after_s = 1
        else:
            self.think_pin(sname + '-x')  # best choice
        self.think_pin(sname)
        # if doing.name[0] == 's':
        #   no_deed_to_do_anythin

    # DL uses C floats and round SP up, which leads to precision issues
    @staticmethod
    def sp_convert(haste, sp):
        sp_hasted = c_float(c_float(haste).value * sp).value
        sp_int = int(sp_hasted)
        return sp_int if sp_int == sp_hasted else sp_int + 1

    def charge_p(self, name, percent, target=None):
        percent = percent / 100 if percent > 1 else percent
        if not target:
            for s in self.skills:
                s.charge(self.sp_convert(percent, s.sp))
        else:
            try:
                skill = self.__dict__[target]
                if hasattr(skill, 'autocharge_timer'):
                    return
                skill.charge(self.sp_convert(percent, skill.sp))
            except:
                return
        log('sp', name, f'{percent*100:.0f}%', ', '.join([f'{s.charged}/{s.sp}' for s in self.skills]))

        if percent == 1:
            self.think_pin('prep')

    def charge(self, name, sp):
        # sp should be integer
        sp = self.sp_convert(self.sp_mod(name), sp)
        for s in self.skills:
            s.charge(sp)
        self.think_pin('sp')
        log('sp', name, sp, ', '.join([f'{s.charged}/{s.sp}' for s in self.skills]))

    def l_dmg_formula(self, e):
        name = e.dname
        dmg_coef = e.dmg_coef
        if hasattr(e, 'dtype'):
            name = e.dtype
        if 'modifiers' in e.__dict__:
            if e.modifiers != None and e.modifiers != 0:
                self.all_modifiers = e.modifiers
        e.dmg = self.dmg_formula(name, dmg_coef)
        self.all_modifiers = self.modifier._static.all_modifiers
        e.ret = e.dmg
        return

    def dmg_formula(self, name, dmg_coef):
        dmg_mod = self.dmg_mod(name)
        att = 1.0 * self.att_mod(name) * self.base_att
        armor = 10 * self.def_mod()
        ele = self.mod(self.slots.c.ele) + 0.5
        # return float(dmg_coef) * self.dmg_mod(name) * self.att_mod() / self.def_mod()
        # return float(dmg_coef) * self.dmg_mod(name) * self.def_mod()
        return 5.0 / 3 * dmg_coef * dmg_mod * att / armor * ele  # true formula
        # return att/armor * dmg_coef * self.dmg_mod(name)

    def l_true_dmg(self, e):
        log('dmg', e.dname, e.count, e.comment)

    def l_dmg_make(self, e):
        if 'dtype' in vars(e):
            self.dmg_make(e.dname, e.dmg_coef, e.dtype)
        else:
            self.dmg_make(e.dname, e.dmg_coef)

    def dmg_make(self, name, dmg_coef, dtype=None, fixed=False, attenuation=None):
        if attenuation is not None:
            rate, pierce = attenuation
            coef = dmg_coef*(rate**pierce)
            if coef < 0.01:
                return 0
        else:
            coef = dmg_coef
            if coef <= 0:
                return 0
        self.damage_sources.add(name)
        for t in self.tension:
            t.check(name)
        if dtype == None:
            dtype = name
        count = self.dmg_formula(dtype, coef) if not fixed else coef
        log('dmg', name, count)
        self.dmg_proc(name, count)
        if self.echo > 1:
            echo_count = self.dmg_formula_echo(coef)
            self.dmg_proc(name, echo_count)
            log('dmg', 'echo', echo_count, f'from {name}')
            count += echo_count
        return count

    def l_melee_fs(self, e):
        log('cast', e.name)
        fs_conf = self.conf[e.name] or self.conf['fs']
        self.fs_before(e)
        self.add_hits(fs_conf['hit'])
        self.dmg_make('fs', fs_conf.dmg)
        self.fs_proc(e)
        self.think_pin('fs')
        self.charge(e.name, fs_conf.sp)

    def l_range_fs(self, e):
        log('cast', e.name)
        self.fs_before(e)
        fs_conf = self.conf[e.name] or self.conf['fs']
        missile_timer = Timer(self.cb_missile, self.conf['missile_iv']['fs'])
        missile_timer.dname = 'fs'
        # missile_timer.dname = 'fs_missile'
        missile_timer.conf = fs_conf
        missile_timer()
        self.fs_proc(e)
        self.think_pin('fs')

    def l_s(self, e):
        if e.name == 'ds':
            return

        s_conf = self.conf[e.name]
        self.add_hits(s_conf['hit'])

        prev = self.action.getprev().name
        log('cast', e.name, f'after {prev}', ', '.join([f'{s.charged}/{s.sp}' for s in self.skills]))

        dmg_coef = s_conf['dmg']
        func = e.name + '_before'
        tmp = getattr(self, func)(e)
        self.s_before(e)
        if tmp != None:
            dmg_coef = tmp
        if dmg_coef:
            self.dmg_make(e.name, dmg_coef)

        if s_conf['buff'] is not None:
            buffarg = s_conf['buff']
            if e.name == 's3' and self.s3.owner is None:
                if len(self.s3_buff_list) == 0:
                    for ba in buffarg:
                        if ba is not None:
                            buff = self.do_buff(e, ba)
                            self.s3_buff_list.append(buff)
                        else:
                            self.s3_buff_list.append(None)
                    if self.s3_buff_list[0] is not None:
                        self.s3_buff_list[0].on()
                        self.s3_buff = self.s3_buff_list[0]
                else:
                    idx = (self.s3_buff_list.index(self.s3_buff) + 1) % len(self.s3_buff_list)
                    try:
                        self.s3_buff.off()
                        self.s3_buff = self.s3_buff_list[idx].on()
                    except:
                        self.s3_buff = None
            else:
                self.do_buff(e, buffarg).on()

        func = e.name + '_proc'
        getattr(self, func)(e)
        self.s_proc(e)

    @staticmethod
    def do_buff(e, buffarg):
        if not isinstance(buffarg[0], tuple):
            buffarg = [buffarg]
        buffs = []
        for ba in buffarg:
            wide = ba[0]
            ba = ba[1:]
            if wide == 'team':
                buff = Teambuff(e.name, *ba)
            elif wide == 'self':
                buff = Selfbuff(e.name, *ba)
            elif wide == 'debuff':
                buff = Debuff(e.name, *ba)
            elif wide == 'spd':
                buff = Spdbuff(e.name, *ba)
            else:
                buff = Buff(e.name, *ba)
            buffs.append(buff)
        if len(buffs) > 1:
            return MultiBuffManager(buffs)
        else:
            return buffs[0]

    def stop(self):
        doing = self.action.getdoing()
        if doing.status == Action.RECOVERY or doing.status == Action.OFF:
            Timeline.stop()
            return True
        return False

