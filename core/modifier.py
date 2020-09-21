from collections import defaultdict
from itertools import chain
from functools import reduce
import operator
import copy

from core.timeline import Timer, Event, Listener, now
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

    @staticmethod
    def mod_mult(a, b):
        return a * (1 + b)

    def mod(self, mtype, operator=None, initial=1):
        operator = operator or ModifierDict.mod_mult
        return reduce(operator, [self.sub_mod(mtype, order) for order in self[mtype].keys()], initial)

    def sub_mod(self, mtype, morder):
        mod_sum = sum([modifier.get() for modifier in self[mtype][morder]])
        if morder == 'buff':
            mod_sum = min(mod_sum, 2.00)
        return mod_sum

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

    # @classmethod
    # def mod(cls, mtype, all_modifiers=None, morder=None):
    #     if not all_modifiers:
    #         all_modifiers = cls._static.all_modifiers
    #     if morder:
    #         return 1 + sum([modifier.get() for modifier in all_modifiers[mtype][morder]])
    #     m = defaultdict(lambda: 1)
    #     for order, modifiers in all_modifiers[mtype].items():
    #         m[order] += sum([modifier.get() for modifier in modifiers])
    #     ret = 1.0
    #     for i in m:
    #         ret *= m[i]
    #     return ret

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
        # if modifier.mod_condition is not None:
        #     if not self._static.g_condition(modifier.mod_condition):
        #         return self

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
        return '<%s %s %s %s>' % (self.mod_name, self.mod_type, self.mod_order, self.get())


class KillerModifier(Modifier):
    def __init__(self, name, order, value, killer_condition):
        self.killer_condition = killer_condition
        super().__init__(f'{name}_killer', f"{killer_condition}_killer", order, value)

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
        self.hp_scale = scale
        self.hp_lost = 100 - hp
        if hp < 100:
            self.hp_cond = self._static.g_condition.hp_cond_set(hp)
        else:
            self.hp_cond = False
        super().__init__('mod_{}_crisis'.format(name), 'att', 'crisis', self.c_mod_value())

    def c_mod_value(self):
        return self.hp_scale * (self.hp_lost ** 2) / 10000

    def get(self):
        self.mod_value = self.c_mod_value()
        return self.mod_value

    def on(self):
        if self.hp_cond:
            self.mod_value = self.c_mod_value()
        else:
            self.mod_value = 0
        return super().on()


bufftype_dict = {}
class Buff(object):
    MAXHP_CAP = 1.30
    _static = Static({
        'all_buffs': [],
        'adv': None
    })

    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='att', morder=None, modifier=None, hidden=False):
        self.name = name
        self.__value = value
        self.duration = duration
        self.mod_type = mtype
        self.mod_order = morder or ('chance' if self.mod_type == 'crit' else 'buff')
        self.bufftype = 'misc' if hidden else 'self'

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

        self.hidden = hidden

        self.__stored = 0
        self.__active = 0
        # self.on()

    def logwrapper(self, *args):
        if not self.hidden:
            log('buff', *args)

    def _no_bufftime(self):
        return 1

    def _ex_bufftime(self):
        return 1 + self._static.adv.sub_mod('buff', 'ex')

    def _bufftime(self):
        return self._static.adv.mod('buff', operator=operator.add)

    def _debufftime(self):
        return self._static.adv.mod('debuff', operator=operator.add)

    def no_bufftime(self):
        self.bufftime = self._no_bufftime
        return self

    def ex_bufftime(self):
        self.bufftime = self._ex_bufftime
        return self

    def value(self, newvalue=None):
        if newvalue:
            self.logwrapper(self.name, f'{self.mod_type}({self.mod_order}): {newvalue:.02f}', 'buff value change')
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
        self.logwrapper(self.name, f'{self.mod_type}({self.mod_order}): {self.value():.02f}', 'buff end <timeout>')
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
            self.logwrapper(self.name, f'{self.mod_type}({self.mod_order}): {value:.02f}', f'buff stack <{stack}>')
        self.effect_off()

    def count_team_buff(self):
        base_mods = [
            Modifier('base_cc', 'crit', 'chance', 0.12),
            Modifier('base_killer', 'killer','passive', 0.30)
        ]
        self.dmg_test_event.modifiers = ModifierDict()
        for mod in base_mods:
            self.dmg_test_event.modifiers.append(mod)
        for b in filter(lambda b: b.get() and b.bufftype == 'simulated_def', self._static.all_buffs):
            self.dmg_test_event.modifiers.append(b.modifier)

        self.dmg_test_event()
        no_team_buff_dmg = self.dmg_test_event.dmg

        placeholders = []
        for b in filter(lambda b: b.get() and b.bufftype in ('team', 'debuff'), self._static.all_buffs):
            placehold = None
            if b.modifier.mod_type == 's':
                placehold = Modifier('placehold_sd', 'att', 'sd', b.modifier.get() / 2)
            elif b.modifier.mod_type == 'spd':
                placehold = Modifier('placehold_spd', 'att', 'spd', b.modifier.get())
            elif b.modifier.mod_type.endswith('_killer'):
                placehold = Modifier('placehold_k', 'killer', 'passive', b.modifier.get())
            if placehold:
                self.dmg_test_event.modifiers.append(placehold)
                placeholders.append(placehold)
            else:
                self.dmg_test_event.modifiers.append(b.modifier)

        self.dmg_test_event()
        team_buff_dmg = self.dmg_test_event.dmg
        log('buff', 'team', team_buff_dmg / no_team_buff_dmg - 1)

        for mod in chain(base_mods, placeholders):
            mod.off()


    def on(self, duration=None):
        if self.mod_type == 'maxhp':
            max_hp = self._static.adv.mod('maxhp')
            if max_hp >= Buff.MAXHP_CAP:
                return self
            value = self.__value
            mod_val = min(value, max(Buff.MAXHP_CAP-max_hp, 0))
            self._static.adv.set_hp((self._static.adv.hp*max_hp+value*100)/(max_hp+mod_val))

        d = (duration or self.duration) * self.bufftime()
        if self.__active == 0:
            self.__active = 1
            if self.__stored == 0:
                self._static.all_buffs.append(self)
                self.__stored = 1
            if d >= 0:
                self.buff_end_timer.on(d)
            proc_type = 'start'
        else:
            if d >= 0:
                self.buff_end_timer.on(d)
            proc_type = 'refresh'
            
        self.logwrapper(self.name, f'{self.mod_type}({self.mod_order}): {self.value():.02f}', f'buff {proc_type} <{d:.02f}s>')
        value, stack = self.valuestack()
        if stack > 1:
            log('buff', self.name, f'{self.mod_type}({self.mod_order}): {value:.02f}', f'buff stack <{stack}>')

        if self.mod_type == 'defense':
            Event('defchain').on()
            if self.bufftype == 'team':
                log('buff', 'team_defense', 'proc team doublebuffs')

        if self.mod_type == 'regen':
            # may need to make this part global since game always regen all stacks at same ticks
            self.set_hp_event = Event('set_hp')
            self.set_hp_event.delta = self.get()
            self.regen_timer = Timer(self.hp_regen, 3.9, True)
        else:
            self.effect_on()
        return self

    def hp_regen(self, t):
        self.set_hp_event()

    def off(self):
        if self.__active == 0:
            return
        self.logwrapper(self.name, f'{self.mod_type}({self.mod_order}): {self.value():.02f}', f'buff end <turn off>')
        self.__active = 0
        self.effect_off()
        self.buff_end_timer.off()
        return self

    def timeleft(self):
        return -1 if self.duration == -1 else (self.buff_end_timer.timing-now())

    def add_time(self, delta):
        self.buff_end_timer.add(delta)
    # def __repr__(self):
    #     return f'{self.modifier}({self.buff_end_timer})'


class EffectBuff(Buff):
    def __init__(self, name, duration, effect_on, effect_off):
        super().__init__(name, 1, duration, 'effect')
        self.bufftype = 'self'
        self.effect_on = effect_on
        self.effect_off = effect_off


class ModeAltBuff(Buff):
    def __init__(self, name, duration=-1, hidden=False):
        super().__init__(name, 1, duration, 'effect', hidden=hidden)

    @property
    def adv(self):
        return self._static.adv

class FSAltBuff(ModeAltBuff):
    def __init__(self, name=None, group=None, duration=-1, uses=-1, hidden=False):
        self.default_fs = self.adv.current_fs
        self.group = group
        pattern = r'^fs\d+$' if group is None else f'^fs\d*_{group}$'
        self.fs_list = [fsn for fsn, _ in self.adv.conf.find(pattern)]
        if not self.fs_list:
            if group is None:
                raise ValueError(f'fs[n] not found in conf')
            raise ValueError(f'{self.group} is not an FS')
        super().__init__(self.group or 'fs[n]', duration=duration, hidden=hidden)
        self.enable_fs(False)
        self.base_uses = uses
        self.uses = 0
        self.l_fs = Listener('fs', self.l_off, order=2)

        self.managed = False

    def enable_fs(self, enabled):
        for fsn in self.fs_list:
            self.adv.a_fs_dict[fsn].set_enabled(enabled)

    def effect_on(self):
        # self.logwrapper(f'fs-{self.name} on', self.uses)
        self.enable_fs(True)
        self.adv.current_fs = self.group
        self.adv.alt_fs_buff = self
        self.l_fs.on()

    def effect_off(self):
        # self.logwrapper(f'fs-{self.name} off', self.uses)
        self.enable_fs(False)
        self.adv.current_fs = self.default_fs
        self.adv.alt_fs_buff = None
        self.l_fs.off()

    def on(self, duration=None):
        self.uses = self.base_uses
        return super().on(duration)

    def l_off(self, e):
        if e.group == self.group and self.uses > 0:
            self.uses -= 1
            if self.uses <= 0:
                super().off()
bufftype_dict['fsAlt'] = FSAltBuff


class XAltBuff(ModeAltBuff):
    def __init__(self, name=None, group=None, duration=-1, hidden=False, deferred=False):
        self.default_x = self.adv.current_x
        self.group = group
        self.x_max = self.adv.conf[f'{group}.x_max']
        self.deferred = deferred
        if not self.x_max:
            raise ValueError(f'{self.group} is not a X group')
        super().__init__(group, duration=duration, hidden=hidden)
        self.enable_x(False)

    def enable_x(self, enabled):
        for _, xact in self.adv.a_x_dict[self.group].items():
            xact.enabled = enabled

    def effect_on(self):
        # self.logwrapper(f'x-{self.group} on')
        self.enable_x(True)
        if self.deferred:
            self.adv.deferred_x = self.group
        else:
            self.adv.current_x = self.group

    def effect_off(self):
        # self.logwrapper(f'x-{self.group} off', self.default_x)
        self.enable_x(False)
        self.adv.current_x = self.default_x
bufftype_dict['xAlt'] = XAltBuff


class SAltBuff(ModeAltBuff):
    def __init__(self, name=None, group=None, base=None, duration=-1, hidden=False):
        if base not in ('s1', 's2', 's3', 's4'):
            raise ValueError(f'{base} is not a skill')
        if group not in self.adv.a_s_dict[base].act_dict.keys():
            raise ValueError(f'{base}-{group} is not a skill')
        super().__init__(f'{base}_{group}', duration=duration, hidden=hidden)
        self.base = base
        self.group = group
        self.default_s = self.adv.current_s[base]
        if group == 'ddrive':
            self.l_s = Listener('s', self.l_add_ddrive, order=0).on()
        elif duration != -1:
            self.l_s = Listener('s', self.l_extend_time, order=0).on()
        self.enable_s(True)

    def enable_s(self, enabled):
        for s in self.adv.a_s_dict.values():
            s.enabled = enabled

    def effect_on(self):
        # self.logwrapper(f'{self.name} on')
        self.adv.current_s[self.base] = self.group

    def effect_off(self):
        # self.logwrapper(f'{self.name} off', self.default_s)
        self.adv.current_s[self.base] = self.default_s

    def l_extend_time(self, e):
        if self.get() and e.name != 'ds' and e.base == self.base and e.group == self.group:
            skill = self.adv.a_s_dict[self.base]
            delta = skill.ac.getstartup() + skill.ac.getrecovery()
            self.add_time(delta)
            log('debug', e.name, 'extend', delta)

    def l_add_ddrive(self, e):
        if self.get() and e.base == self.base and e.group == self.group:
            skill = self.adv.a_s_dict[self.base]
            self.adv.dragonform.add_drive_gauge_time(skill.ac.getstartup() + skill.ac.getrecovery(), skill_pause=True)
bufftype_dict['sAlt'] = SAltBuff


class Selfbuff(Buff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='att', morder=None):
        super().__init__(name, value, duration, mtype, morder)
        self.bufftype = 'self'
bufftype_dict['self'] = Selfbuff


class SingleActionBuff(Buff):
    # self buff lasts until the action it is buffing is completed
    def __init__(self, name='<buff_noname>', value=0, uses=1, mtype='att', morder=None):
        super().__init__(name, value, -1, mtype, morder)
        self.bufftype = 'self'
        self.uses = uses
        self.active = set()
        self._static.adv.sab.append(self)

    def on(self, uses=1):
        self.uses = uses
        return super().on(-1)

    def off(self):
        return super().off()

    def effect_on(self):
        pass
    
    def effect_off(self):
        pass

    def act_on(self, e):
        if self.get() and (e.name.startswith(self.mod_type) or (e.name == 'ds' and self.mod_type == 's')) \
           and self.uses > 0 and not e.name in self.active and e.name in self._static.adv.damage_sources:
            self.active.add(e.name)
            self.logwrapper(self.name, e.name, str(self.active), 'act_on')
            self.uses -= 1

    def act_off(self, e):
        if e.name in self.active:
            self.active.discard(e.name)
            self.logwrapper(self.name, e.name, str(self.active), 'act_off')
            if self.uses == 0:
                self.off()

bufftype_dict['next'] = SingleActionBuff


class Teambuff(Buff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='att', morder=None):
        super().__init__(name, value, duration, mtype, morder)
        self.bufftype = 'team'

        self.base_cc_mod = []
        for mod in self.modifier._static.all_modifiers['crit']['chance']:
            if mod.mod_name.startswith('w_') or mod.mod_name.startswith('c_ex'):
                self.base_cc_mod.append(mod)

    def on(self, duration=None):
        super().on(duration)
        self.count_team_buff()
        return self

    def off(self):
        super().off()
        self.count_team_buff()
        return self

    def buff_end_proc(self, e):
        super().buff_end_proc(e)
        self.count_team_buff()
bufftype_dict['team'] = Teambuff


class ElementalTeambuff(Teambuff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='att', morder=None, element=None):
        super().__init__(name, value, duration, mtype, morder)
        self.element = element

    def on(self, duration=0):
        if self._static.adv.slots.c.ele == self.element:
            super().on(duration=duration)
        return self

    def count_team_buff(self):
        if self.modifier._static.g_condition('buff all team'):
            self.bufftype = 'team'
            super().count_team_buff()
        else:
            self.bufftype = 'self'
bufftype_dict['ele'] = ElementalTeambuff


class ZoneTeambuff(Teambuff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='att', morder=None):
        super().__init__(name, value, duration, mtype, morder)
        self.bufftime = self._no_bufftime
        self.name += '_zone'
    
    @property
    def zone_buffs(self):
        return sorted((b for b in self._static.all_buffs if type(b) == ZoneTeambuff and b.get()), key=lambda b: b.timeleft())

    def on(self, duration=0):
        zones = self.zone_buffs
        if len(zones) > 4:
            zones[0].off()
        super().on(duration=duration)
        return self

bufftype_dict['zone'] = ZoneTeambuff


class Spdbuff(Buff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, mtype='spd', wide=None):
        mtype = mtype
        morder = 'passive'
        super().__init__(name, value, duration, mtype, morder)
        if not wide:
            try:
                self.bufftype = name.split('_')[1]
            except:
                self.bufftype = 'self'
        else:
            self.bufftype = wide
        if self.bufftype not in 'self' or 'team':
            self.bufftype = 'self'

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
bufftype_dict['spd'] = Spdbuff


class Debuff(Teambuff):
    def __init__(self, name='<buff_noname>', value=0, duration=0, chance=1.0, mtype='def', morder=None):
        self.val = value
        self.chance = chance
        if self.chance != 1:
            bd = 1.0 / (1.0 + self.val)
            bd = (bd - 1) * self.chance + 1
            self.val = 1 - 1.0 / bd
            self.val = 0 - self.val
        super().__init__(name, self.val, duration, mtype, morder)
        self.bufftype = 'debuff'
        if mtype == 'defb':
            self.bufftime = self._no_bufftime
            self.name += '_zone'
        else:
            self.bufftime = self._debufftime
bufftype_dict['debuff'] = Debuff


class MultiBuffManager:
    def __init__(self, name, buffs, duration=None):
        self.name = name
        self.buffs = buffs or []
        # self.buffs = list(filter(None, self.buffs))
        self.duration = duration
        for b in self.buffs:
            if b.mod_type == 'effect':
                b.hidden = True

    def on(self):
        # print([(b.name, b.get()) for b in self.buffs])
        for b in self.buffs:
            try:
                b.on(duration=self.duration)
            except TypeError:
                b.on()
        # print([(b.name, b.get()) for b in self.buffs])
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

    def timeleft(self):
        return min([b.timeleft for b in self.buffs])


class ModeManager(MultiBuffManager):
    ALT_CLASS = {
        'x': XAltBuff,
        'fs': FSAltBuff,
        's1': SAltBuff,
        's2': SAltBuff
    }
    def __init__(self, name=None, group=None, buffs=None, duration=None, **kwargs):
        buffs = buffs or []
        self.alt = {}
        for k, buffclass in ModeManager.ALT_CLASS.items():
            if kwargs.get(k, False):
                if k in ('s1', 's2'):
                    self.alt[k] = buffclass(group=group, base=k)
                elif k in ('x'):
                    self.alt[k] = buffclass(group=group, deferred=(kwargs.get('deferred', False)))
                else:
                    self.alt[k] = buffclass(group=group)
        buffs.extend(self.alt.values())
        super().__init__(name, buffs, duration)

    def on_except(self, exclude=None):
        for b in self.buffs:
            if exclude and b == self.alt.get(exclude, None):
                continue
            try:
                b.on(duration=self.duration)
            except TypeError:
                b.on()
        return self

    def off_except(self, exclude=None):
        for b in self.buffs:
            if exclude and b == self.alt.get(exclude, None):
                continue
            b.off()
        return self

def init_mode(*args):
    kwargs = {}
    for a in args[2:]:
        kwargs[a] = True
    return ModeManager(args[0], args[1], None, **kwargs)
bufftype_dict['mode'] = init_mode


class ActiveBuffDict(defaultdict):
    def __init__(self):
        super().__init__(lambda: defaultdict(lambda: {}))

    def __call__(self, k, group=None, *args):
        if self.get(k, False):
            subdict = self[k]
            if group is not None:
                if isinstance(group, int):
                    group -= 1
                try:
                    return any(b.get() for b in subdict[group].values())
                except KeyError:
                    return False
            else:
                return any(b.get() for sub in subdict.values() for b in sub.values())
        else:
            return False
    
    def has(self, k, group, seq):
        return k in self and group in self[k] and seq in self[k][group]

    def timeleft(self, k, group='default', seq=0):
        try:
            return self[k][group][seq].timeleft()
        except KeyError:
            return 0

    def add(self, k, group, seq, buff):
        self[k][group][seq] = buff

    def on(self, k, group, seq):
        return self[k][group][seq].on()

    def off(self, k, group='default', seq=0):
        return self[k][group][seq].off()

    def off_all(self, k):
        for g, seq in self[k].items():
            for b in seq.values():
                b.off()
