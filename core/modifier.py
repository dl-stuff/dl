from collections import defaultdict
import copy

from core.timeline import Timer, Event, Listener
from core.log import log
from core.ctx import Static


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
        elif mtype != 'effect':
            self.modifier = Modifier('mod_' + self.name, self.mod_type, self.mod_order, 0)
            self.modifier.get = self.get
        else:
            self.modifier = None
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
        return self.modifier and self.modifier.on()

    def effect_off(self):
        return self.modifier and self.modifier.off()

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
                        self.dmg_test_event.modifiers.append(mod_copy)
                    else:
                        self.dmg_test_event.modifiers.append(i.modifier)
        self.dmg_test_event()
        team_buff_dmg = self.dmg_test_event.dmg * sd_mods
        team_buff_dmg += team_buff_dmg * spd
        log('buff', 'team', team_buff_dmg / no_team_buff_dmg - 1)

        for mod in base_mods:
            mod.off()

    def on(self, duration=None):
        d = (duration or self.duration) * self.bufftime()
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
        self.effect_off()
        self.buff_end_timer.off()
        return self

    def add_time(self, delta):
        self.buff_end_timer.add(delta)


class EffectBuff(Buff):
    def __init__(self, name, duration, effect_on, effect_off):
        super().__init__(name, 1, duration, 'effect')
        self.bufftype = 'self'
        self.effect_on = effect_on
        self.effect_off = effect_off


class FSAltBuff(Buff):
    def __init__(self, adv, fs_name=None, duration=-1, uses=-1, hidden=False):
        self.adv = adv
        self.fs_name = fs_name
        pattern = r'^fs\d+$' if fs_name is None else f'^fs\d*_{fs_name}$'
        self.prev_fs = self.adv.alt_fs
        self.fs_list = [fsn for fsn, _ in adv.conf.find(pattern)]
        if not self.fs_list:
            if fs_name is None:
                raise ValueError(f'fs[n] not found in conf')
            raise ValueError(f'{self.fs_name} is not an FS')
        super().__init__(fs_name or 'alt', 1, duration, 'effect')
        self.enable_fs(False)
        self.base_uses = uses
        self.uses = 0
        Listener('fs', self.l_off, after=True).on()
        self.bufftype = 'misc' if hidden else 'self'

    def enable_fs(self, enabled):
        for fsn in self.fs_list:
            self.adv.a_fs_dict[fsn].enabled = enabled

    def effect_on(self):
        log('debug', f'fs {self.fs_name} on', self.uses)
        self.enable_fs(True)
        self.prev_fs = self.adv.alt_fs
        self.adv.alt_fs = self.fs_name

    def effect_off(self):
        log('debug', f'fs {self.fs_name} off', self.uses)
        self.enable_fs(False)
        self.adv.alt_fs = self.prev_fs

    def on(self, duration=None):
        self.uses = self.base_uses
        return super().on(duration)

    def l_off(self, e):
        self.uses -= 1
        if self.uses <= 0:
            self.off()


class XAltBuff(Buff):
    def __init__(self, adv, fs_name=None, duration=-1, uses=-1, hidden=False):
        self.adv = adv
        self.fs_name = fs_name or 'alt'
        pattern = r'^fs\d+$' if fs_name is None else f'^fs\d*_{fs_name}$'
        self.prev_fs = self.adv.alt_fs
        self.fs_list = [fsn for fsn, _ in adv.conf.find(pattern)]
        if not self.fs_list:
            raise ValueError(f'{self.fs_name} is not an FS')
        super().__init__(fs_name, 1, duration, 'effect')
        self.enable_fs(False)
        self.base_uses = uses
        self.uses = 0
        Listener('fs', self.l_off, after=True).on()
        self.bufftype = 'misc' if hidden else 'self'

    def enable_fs(self, enabled):
        for fsn in self.fs_list:
            self.adv.a_fs_dict[fsn].enabled = enabled

    def effect_on(self):
        log('debug', f'fs {self.fs_name} on', self.uses)
        self.enable_fs(True)
        self.prev_fs = self.adv.alt_fs
        self.adv.alt_fs = self.fs_name

    def effect_off(self):
        log('debug', f'fs {self.fs_name} off', self.uses)
        self.enable_fs(False)
        self.adv.alt_fs = self.prev_fs

    def on(self, duration=None):
        self.uses = self.base_uses
        return super().on(duration)

    def l_off(self, e):
        self.uses -= 1
        if self.uses <= 0:
            self.off()


class Selfbuff(Buff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='att', morder=None):
        super().__init__(name, value, duration, mtype, morder)
        self.bufftype = 'self'


class SingleActionBuff(Buff):
    # self buff lasts until the action it is buffing is completed
    def __init__(self, name='<buff_noname>', value=0, casts=1, mtype='att', morder=None, event=None, end_proc=None):
        super().__init__(name, value, -1, mtype, morder)
        self.bufftype = 'self'
        self.casts = casts
        self.end_event = event if event is not None else mtype
        self.end_proc = end_proc
        Listener(self.end_event, self.l_off, after=True).on()

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
        super().__init__(name, value, duration, mtype, morder)
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
        super().__init__(name, value, duration, mtype, morder)
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
        super().__init__(name, self.val, duration, mtype, morder)
        self.bufftype = 'debuff'
        self.bufftime = self._debufftime


class MultiBuffManager:
    def __init__(self, buffs, duration=None):
        self.buffs = buffs
        self.duration = duration

    def on(self):
        for b in self.buffs:
            try:
                b.on(duration=self.duration)
            except ValueError:
                b.on()
        return self

    def off(self):
        for b in self.buffs:
            b.off()
        return self

    def get(self):
        return all(map(lambda b: b.get(), self.buffs))

    def add_time(self, delta):
        for b in self.buffs:
            b.add_time(delta)
        return self
