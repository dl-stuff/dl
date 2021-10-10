from collections import defaultdict
from conf import load_json
from itertools import chain
from functools import reduce
import operator
import copy

from core.timeline import Timer, Event, Listener, now
from core.log import log
from core.ctx import Static
from core.acl import allow_acl
from core.afflic import AFFLICT_LIST


class ModifierDict(defaultdict):
    BUFF_CAPS_FOR_TYPE = {"maxhp": 0.3}

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
        return reduce(
            operator,
            [self.sub_mod(mtype, order) for order in self[mtype].keys()],
            initial,
        )

    def sub_mod(self, mtype, morder):
        if morder == "buff":
            capped_sum = 0
            uncapped_sum = 0
            for modifier in self[mtype][morder]:
                if modifier.buff_capped:
                    capped_sum += modifier.get()
                else:
                    uncapped_sum += modifier.get()
            capped_sum = min(capped_sum, ModifierDict.BUFF_CAPS_FOR_TYPE.get(mtype, 2.0))
            return capped_sum + uncapped_sum
        else:
            return sum((modifier.get() for modifier in self[mtype][morder]))


class Modifier(object):
    _static = Static({"all_modifiers": ModifierDict(), "g_condition": None, "damage_sources": set()})

    def __init__(self, name, mtype, order, value, condition=None, get=None):
        self.mod_name = name
        self.mod_type = mtype
        self.mod_order = order
        self.mod_value = value
        self.mod_condition = condition
        if self.mod_condition:
            # initialize cond
            self._static.g_condition(self.mod_condition)
        self.mod_get = get
        self.buff_capped = order == "buff"
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
        return "<%s %s %s %s>" % (
            self.mod_name,
            self.mod_type,
            self.mod_order,
            self.get(),
        )


class KillerModifier(Modifier):
    def __init__(self, name, order, value, killer_condition):
        if "afflicted" in killer_condition:
            self.killer_condition = AFFLICT_LIST
        else:
            self.killer_condition = killer_condition
        super().__init__(f"{name}_killer", f"{killer_condition}_killer", order, value)

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
    def __init__(self, name, modtype, adv):
        self.adv = adv
        self.passive = None
        self.per_hit = None
        super().__init__(name, modtype, "crisis", self.c_mod_value())

    def set_passive(self, value):
        if self.passive is None:
            self.passive = value
        else:
            self.passive = max(self.passive, value)

    def set_per_hit(self, value):
        self.per_hit = value

    def c_mod_value(self):
        mods = []
        if self.passive is not None:
            mods.append(self.passive)
        if self.per_hit is not None:
            mods.append(self.per_hit)
        if mods:
            return (max(mods)) * ((100 - self.adv.hp) ** 2) / 10000
        else:
            return 0

    def get(self):
        self.mod_value = self.c_mod_value()
        return self.mod_value

    def on(self):
        self.mod_value = self.c_mod_value()
        return super().on()


bufftype_dict = {}


class Buff(object):
    _static = Static({"all_buffs": [], "adv": None})
    DB_DURATION = 15  # usual doublebuff effect duration for offensive buffs, note that regen lasts 20s

    def __init__(self, name="<buff_noname>", value=0, duration=0, mtype="att", morder=None, modifier=None, hidden=False, source=None):
        self.name = name
        self._value = value
        try:
            self.duration, self.interval = duration
        except TypeError:
            self.duration, self.interval = duration, 3.9
        self.mod_type = mtype
        self.mod_order = morder or ("chance" if self.mod_type == "crit" else "buff")
        self.bufftype = "misc" if hidden else "self"

        self.source = source
        if self.source is not None and source[0] != "s" and source[0:2] != "ds":
            self.bufftime = self._ex_bufftime
        else:
            self.bufftime = self._bufftime
        self.buff_end_timer = Timer(self.buff_end_proc)
        if modifier:
            self.modifier = modifier
            self.get = self.modifier.get
        elif mtype != "effect":
            self.modifier = Modifier("mod_" + self.name, self.mod_type, self.mod_order, 0)
            self.modifier.get = self.get
        else:
            self.modifier = None
        self.dmg_test_event = Event("dmg_formula")
        self.dmg_test_event.dmg_coef = 1
        self.dmg_test_event.dname = "test"

        self.hidden = hidden

        self.__stored = 0
        self.__active = 0

        self.buffevent = Event("buff")
        self.pause_time = -1
        self.refresh_time = -1

        self.extra_effect_off_list = []
        # self.on()

    def logwrapper(self, *args):
        if not self.hidden:
            log("buff", *args)

    def _no_bufftime(self):
        return 1

    def _ex_bufftime(self):
        return 1 + self._static.adv.sub_mod("buff", "ex")

    def _bufftime(self):
        return self._static.adv.mod("buff", operator=operator.add)

    def _debufftime(self):
        return self._static.adv.mod("debuff", operator=operator.add)

    def any_bufftime(self):
        self.bufftime = self._bufftime
        return self

    def no_bufftime(self):
        self.bufftime = self._no_bufftime
        return self

    def ex_bufftime(self):
        self.bufftime = self._ex_bufftime
        return self

    def value(self, newvalue=None):
        if newvalue is not None:
            self.logwrapper(
                self.name,
                f"{self.mod_type}({self.mod_order}): {newvalue:.02f}",
                "buff value change",
            )
            return self.set(newvalue)
        else:
            return self._value

    @allow_acl
    def get(self):
        if self.__active:
            return self._value
        else:
            return 0

    def set(self, v, d=None):
        self._value = v
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
                    value += i._value
        return value, stack

    def effect_on(self):
        value = self.get()
        if self.mod_type == "defense" and self.mod_order == "buff" and value > 0:
            db = Event("defchain")
            db.source = self.source
            db.on()
            if self.bufftype == "team":
                log("buff", "doublebuff", 15 * self.bufftime())
                if self.bufftime == self._bufftime:
                    self._static.adv.slots.c.set_need_bufftime()
        elif self.mod_type == "maxhp":
            self.modifier.on()
            percent = value * 100
            log("heal", self.name, self._static.adv.max_hp * value, "team" if self.bufftype == "team" else "self")
            self._static.adv.add_hp(percent)
        # FIXME: heal formula 1day twust
        elif self.mod_type == "regen" and value != 0:
            if self.mod_order in ("hp", "buff"):
                self.set_hp_event = Event("set_hp")
                self.set_hp_event.delta = value
                self.set_hp_event.source = "dot"
                self.regen_timer = Timer(self.hp_regen, self.interval, True).on()
            elif self.mod_order in ("sp", "sp%"):
                self.regen_timer = Timer(self.sp_regen, self.interval, True).on()
        elif self.mod_type == "heal" and value != 0:
            self.set_hp_event = Event("heal_make")
            self.set_hp_event.name = self.name
            self.set_hp_event.delta = self._static.adv.heal_formula(self.source, value)
            self.set_hp_event.target = "team" if self.bufftype == "team" else "self"
            self.regen_timer = Timer(self.hp_regen, 2.9, True).on()
        else:
            return self.modifier and self.modifier.on()

    def effect_off(self):
        if self.mod_type in ("regen", "heal"):
            self.regen_timer.off()
        else:
            return self.modifier and self.modifier.off()

    def extra_effect_off(self, callback):
        self.extra_effect_off_list.append(callback)

    def buff_end_proc(self, e):
        self.logwrapper(
            self.name,
            f"{self.mod_type}({self.mod_order}): {self.value():.02f}",
            "buff end <timeout>",
        )
        for extra in self.extra_effect_off_list:
            extra()
        self.effect_off()
        self.__active = 0

        if self.__stored:
            self._static.all_buffs.remove(self)
            self.__stored = 0
        value, stack = self.valuestack()
        if stack > 0:
            self.logwrapper(
                self.name,
                f"{self.mod_type}({self.mod_order}): {value:.02f}",
                f"buff stack <{stack}>",
            )

    def count_team_buff(self):
        if self.bufftype == "self":
            return
        base_mods = [
            Modifier("base_cc", "crit", "chance", 0.12),
            Modifier("base_killer", "killer", "passive", 0.30),
        ]
        self.dmg_test_event.modifiers = ModifierDict()
        for mod in base_mods:
            self.dmg_test_event.modifiers.append(mod)
        for b in filter(lambda b: b.get() and b.bufftype == "simulated_def", self._static.all_buffs):
            self.dmg_test_event.modifiers.append(b.modifier)

        self.dmg_test_event()
        no_team_buff_dmg = self.dmg_test_event.dmg

        placeholders = []
        for b in filter(
            lambda b: b.get() and b.bufftype in ("team", "debuff"),
            self._static.all_buffs,
        ):
            placehold = None
            if b.modifier.mod_type == "s":
                placehold = Modifier("placehold_sd", "att", "sd", b.modifier.get() / 2)
            elif b.modifier.mod_type == "spd":
                placehold = Modifier("placehold_spd", "att", "spd", b.modifier.get())
            elif b.modifier.mod_type.endswith("_killer"):
                placehold = Modifier("placehold_k", "killer", "passive", b.modifier.get())
            if placehold:
                self.dmg_test_event.modifiers.append(placehold)
                placeholders.append(placehold)
            else:
                self.dmg_test_event.modifiers.append(b.modifier)

        self.dmg_test_event()
        team_buff_dmg = self.dmg_test_event.dmg
        log("buff", "team", team_buff_dmg / no_team_buff_dmg - 1)

        for mod in chain(base_mods, placeholders):
            mod.off()

    def on(self, duration=None):
        d = max(-1, (duration or self.duration) * self.bufftime())
        if d != -1 and self.bufftime == self._bufftime:
            self._static.adv.slots.c.set_need_bufftime()
        if self.__active == 0:
            self.__active = 1
            if self.__stored == 0:
                self._static.all_buffs.append(self)
                self.__stored = 1
            if d >= 0:
                self.buff_end_timer.on(d)
            proc_type = "start"
        else:
            if d >= 0:
                if self.buff_end_timer.online:
                    self.buff_end_timer.on(d)
                else:
                    self.refresh_time = d
            else:
                return self
            proc_type = "refresh"

        self.logwrapper(
            self.name,
            f"{self.mod_type}({self.mod_order}): {self.value():.02f}",
            f"buff {proc_type} <{d:.02f}s>",
        )
        value, stack = self.valuestack()
        if stack > 1:
            log(
                "buff",
                self.name,
                f"{self.mod_type}({self.mod_order}): {value:.02f}",
                f"buff stack <{stack}>",
            )

        self.effect_on()

        self.buffevent.buff = self
        self.buffevent.on()

        return self

    def hp_regen(self, t):
        self.set_hp_event.on()

    def sp_regen(self, t):
        if self.mod_order == "sp%":
            self.adv.charge_p("sp_regen", self.value())
        else:
            self.adv.charge("sp_regen", self.value())
            log("sp", "team", self.value())

    def off(self):
        if self.__active == 0:
            return
        self.logwrapper(
            self.name,
            f"{self.mod_type}({self.mod_order}): {self.value():.02f}",
            f"buff end <turn off>",
        )
        self.__active = 0
        self.buff_end_timer.off()
        self.effect_off()
        return self

    @property
    def adv(self):
        return self._static.adv

    @allow_acl
    def timeleft(self):
        return -1 if self.duration == -1 else (self.buff_end_timer.timing - now())

    def add_time(self, delta, capped=False):
        if capped:
            elapsed = self.buff_end_timer.elapsed()
            delta = min(elapsed + delta, self.duration) - elapsed
        self.buff_end_timer.add(delta)

    def pause(self):
        self.pause_time = self.timeleft()
        if self.pause_time > 0:
            log("pause", self.name, self.pause_time)
            self.buff_end_timer.off()

    def resume(self):
        self.pause_time = max(self.pause_time, self.refresh_time)
        if self.pause_time > 0:
            log("resume", self.name, self.pause_time, now() + self.pause_time)
            self.buff_end_timer.on(self.pause_time)
        self.pause_time = -1

    # def __repr__(self):
    #     return f'{self.modifier}({self.buff_end_timer})'


class EffectBuff(Buff):
    def __init__(self, name, duration, effect_on, effect_off, source=None):
        super().__init__(name, 1, duration, "effect", source=source)
        self.bufftype = "self"
        self.effect_on = effect_on
        self.effect_off = effect_off


class ModeAltBuff(Buff):
    def __init__(self, name, duration=-1, uses=None, hidden=False, source=None):
        super().__init__(name, 1, duration, "effect", hidden=hidden, source=source)

    def l_off(self, e):
        if e.group == self.group and self.uses > 0:
            self.uses -= 1
            if self.uses <= 0:
                super().off()


class FSAltBuff(ModeAltBuff):
    def __init__(self, name=None, group=None, duration=-1, uses=-1, hidden=False, source=None):
        self.default_fs = self.adv.current_fs
        self.group = group
        pattern = r"^fs\d+$" if group is None else f"^fs\d*_{group}$"
        self.fs_list = [fsn for fsn, _ in self.adv.conf.find(pattern)]
        if not self.fs_list:
            if group is None:
                raise ValueError(f"fs[n] not found in conf")
            raise ValueError(f"{self.group} is not an FS")
        super().__init__(
            f"fs_{self.group}" if self.group else "fs[n]",
            duration=duration,
            hidden=hidden,
            source=source,
        )
        self.enable_fs(False)
        self.base_uses = uses
        self.uses = 0
        self.l_fs = Listener("fs", self.l_off, order=2)
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
        if self.adv.current_fs == self.group:
            self.adv.current_fs = self.default_fs
            self.adv.alt_fs_buff = None
        self.l_fs.off()

    def on(self, duration=None):
        self.uses = self.base_uses
        return super().on(duration)


bufftype_dict["fsAlt"] = FSAltBuff


class XAltBuff(ModeAltBuff):
    def __init__(self, name=None, group=None, duration=-1, hidden=False, deferred=True, source=None):
        self.default_x = self.adv.current_x
        self.group = group
        self.x_max = self.adv.conf[f"{group}.x_max"]
        self.deferred = deferred
        if not self.x_max:
            raise ValueError(f"{self.group} is not a X group")
        super().__init__(f"x_{self.group}", duration=duration, hidden=hidden, source=source)
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
        if self.adv.current_x == self.group:
            self.adv.current_x = self.default_x


bufftype_dict["xAlt"] = XAltBuff


class SAltBuff(ModeAltBuff):
    def __init__(self, name=None, group=None, base=None, duration=-1, uses=-1, hidden=False, source=None, timed_mode=False):
        if base not in ("s1", "s2", "s3", "s4"):
            raise ValueError(f"{base} is not a skill")
        if group not in self.adv.a_s_dict[base].act_dict.keys():
            raise ValueError(f"{base}-{group} is not a skill")
        super().__init__(f"{base}_{group}", duration=duration, hidden=hidden, source=source)
        self.base = base
        self.group = group
        self.default_s = self.adv.current_s[base]
        if duration != -1 and not timed_mode:
            self.l_s = Listener("s", self.l_pause, order=0).on()
            self.l_s_end = Listener("s_end", self.l_resume, order=0).on()
        self.enable_s(True)
        self.base_uses = uses
        self.uses = 0
        self.l_end = Listener("s", self.l_off, order=2)

    def enable_s(self, enabled):
        self.adv.a_s_dict[self.base].set_enabled(enabled)

    def effect_on(self):
        # self.logwrapper(f'{self.name} on')
        self.adv.current_s[self.base] = self.group
        self.uses = self.base_uses
        self.l_end.on()

    def effect_off(self):
        # self.logwrapper(f'{self.name} off', self.default_s)
        if self.adv.current_s[self.base] == self.group:
            self.adv.current_s[self.base] = self.default_s
        self.l_end.off()

    def l_extend_time(self, e):
        if self.get() and e.name != "ds" and e.base == self.base and e.group == self.group:
            skill = self.adv.a_s_dict[self.base]
            delta = (skill.ac.getstartup() + skill.ac.getrecovery()) / self.adv.speed()
            self.add_time(delta)
            log("debug", e.name, "extend", delta)

    def l_pause(self, e):
        if self.get() and e.base == self.base and e.group == self.group:
            self.pause()

    def l_resume(self, e):
        if self.get() and e.act.base == self.base and e.act.group == self.group:
            self.resume()


bufftype_dict["sAlt"] = SAltBuff


class Selfbuff(Buff):
    def __init__(
        self,
        name="<buff_noname>",
        value=0,
        duration=0,
        mtype="att",
        morder=None,
        source=None,
    ):
        super().__init__(name, value, duration, mtype, morder, source=source)
        self.bufftype = "self"


bufftype_dict["self"] = Selfbuff


class AbilityBuff(Selfbuff):
    def __init__(
        self,
        name="<buff_noname>",
        value=0,
        duration=0,
        mtype="att",
        morder=None,
        source=None,
    ):
        super().__init__(name, value, duration, mtype, morder, source=source)
        self.bufftype = "ability"
        self.bufftime = self._no_bufftime


bufftype_dict["ability"] = AbilityBuff


class SingleActionBuff(Buff):
    # self buff lasts until the action it is buffing is completed
    def __init__(
        self,
        name="<buff_noname>",
        value=0,
        uses=1,
        mtype="att",
        morder=None,
        source=None,
    ):
        super().__init__(name, value, -1, mtype, morder)
        self.bufftype = "self"
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
        if self.get() and (e.name.startswith(self.mod_type) or (e.name == "ds" and self.mod_type == "s")) and self.uses > 0 and not e.name in self.active and e.name in self._static.adv.damage_sources:
            self.active.add(e.name)
            self.logwrapper(self.name, e.name, str(self.active), "act_on")
            self.uses -= 1

    def act_off(self, e):
        if e.name in self.active:
            self.active.discard(e.name)
            self.logwrapper(self.name, e.name, str(self.active), "act_off")
            if self.uses == 0:
                self.off()


bufftype_dict["next"] = SingleActionBuff


class Teambuff(Buff):
    def __init__(
        self,
        name="<buff_noname>",
        value=0,
        duration=0,
        mtype="att",
        morder=None,
        source=None,
    ):
        super().__init__(name, value, duration, mtype, morder, source=source)
        self.bufftype = "team"

        self.base_cc_mod = []
        for mod in self.modifier._static.all_modifiers["crit"]["chance"]:
            if mod.mod_name.startswith("w_") or mod.mod_name.startswith("c_ex"):
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


bufftype_dict["team"] = Teambuff
bufftype_dict["nearby"] = Teambuff


class ElementalTeambuff(Teambuff):
    def __init__(
        self,
        name="<buff_noname>",
        value=0,
        duration=0,
        mtype="att",
        morder=None,
        element=None,
        source=None,
    ):
        super().__init__(name, value, duration, mtype, morder, source=source)
        self.element = element

    def on(self, duration=0):
        if self._static.adv.slots.c.ele == self.element:
            super().on(duration=duration)
        return self

    def count_team_buff(self):
        if self.modifier._static.g_condition("buff all team"):
            self.bufftype = "team"
            super().count_team_buff()
        else:
            self.bufftype = "self"


bufftype_dict["ele"] = ElementalTeambuff


class ZoneTeambuff(Teambuff):
    def __init__(
        self,
        name="<buff_noname>",
        value=0,
        duration=0,
        mtype="att",
        morder=None,
        source=None,
    ):
        super().__init__(name, value, duration, mtype, morder, source=source)
        self.bufftime = self._no_bufftime
        self.name += "_zone"

    @property
    def zone_buffs(self):
        return sorted(
            (b for b in self._static.all_buffs if type(b) == ZoneTeambuff and b.get()),
            key=lambda b: b.timeleft(),
        )

    def on(self, duration=0):
        zone_buffs = {(b.timeleft(), b.source): b for b in self._static.all_buffs if type(b) == ZoneTeambuff and b.get()}
        if len(zone_buffs) > 4:
            sorted(zone_buffs.items())[0][1].off()
        super().on(duration=duration)
        return self


bufftype_dict["zone"] = ZoneTeambuff


class Spdbuff(Buff):
    def __init__(
        self,
        name="<buff_noname>",
        value=0,
        duration=0,
        mtype="spd",
        wide=None,
        source=None,
    ):
        mtype = mtype
        morder = "passive"
        super().__init__(name, value, duration, mtype, morder, source=source)
        if not wide:
            try:
                self.bufftype = name.split("_")[1]
            except:
                self.bufftype = "self"
        else:
            self.bufftype = wide
        if self.bufftype not in "self" or "team":
            self.bufftype = "self"

    def on(self, duration=None):
        Buff.on(self, duration)
        if self.bufftype == "team":
            self.count_team_buff()
        return self

    def off(self):
        Buff.off(self)
        if self.bufftype == "team":
            self.count_team_buff()
        return self

    def buff_end_proc(self, e):
        Buff.buff_end_proc(self, e)
        if self.bufftype == "team":
            self.count_team_buff()


bufftype_dict["spd"] = Spdbuff


class Debuff(Teambuff):
    def __init__(
        self,
        name="<buff_noname>",
        value=0,
        duration=0,
        chance=1.0,
        mtype="def",
        morder=None,
        source=None,
    ):
        self.val = value
        self._chance = chance
        super().__init__(name, self.ev_val(), duration, mtype, morder)
        self.bufftype = "debuff"
        self.is_zone = False
        if mtype in ("defb", "adpt", "attb"):
            self.bufftime = self._no_bufftime
            self.name += "_zone"
            self.is_zone = True
        else:
            if self.bufftime == self._ex_bufftime:
                self.bufftime = self._no_bufftime
            else:
                self.bufftime = self._debufftime

    @property
    def chance(self):
        return max(min(1, self._chance + self._static.adv.sub_mod("debuff_rate", "passive")), 0)

    def ev_val(self):
        ev_val = self.val
        if self.chance != 1:
            bd = 1.0 / (1.0 + ev_val)
            bd = (bd - 1) * self.chance + 1
            ev_val = 1 - 1.0 / bd
            ev_val = 0 - ev_val
        return ev_val

    def value(self, newvalue=None, newchance=None):
        if newvalue or newchance:
            self.val = newvalue or self.val
            self._chance = newchance or self._chance
            return super().value(self.ev_val())
        else:
            return super().value()


bufftype_dict["debuff"] = Debuff


class AffResDebuff(Buff):
    def __init__(self, name, value=0, duration=0, affname=None, source=None):
        super().__init__(name, value, duration, "effect", source=source)
        self.afflic = getattr(self._static.adv.afflics, affname)
        if self.bufftime == self._ex_bufftime:
            self.bufftime = self._no_bufftime
        else:
            self.bufftime = self._debufftime

    def effect_on(self):
        self.afflic.set_res_mod(self.value())

    def effect_off(self):
        self.afflic.set_res_mod(-self.value())


bufftype_dict["affres"] = AffResDebuff


class AffEdgeBuff(Buff):
    def __init__(self, name, value=0, duration=0, affname=None, source=None):
        super().__init__(name, value, duration, "effect", source=source)
        self.aff_edge_mods = getattr(self._static.adv.afflics, affname).aff_edge_mods
        self.mod_object = Modifier(name, "edge", affname, value)

    def effect_on(self):
        self.aff_edge_mods.append(self.mod_object)

    def effect_off(self):
        self.aff_edge_mods.remove(self.mod_object)


bufftype_dict["affup"] = AffEdgeBuff


class EchoBuff(Buff):
    def __init__(self, name, value=0, duration=0, source=None):
        super().__init__(name, 1, duration, "effect", source=source)
        self.echo_mod = value

    def on(self, duration=None):
        if self._static.adv.enable_echo(self.name, mod=self.echo_mod):
            return super().on(duration)

    def effect_off(self):
        super().effect_off()
        self._static.adv.disable_echo()


bufftype_dict["echo"] = EchoBuff


class DrainBuff(Buff):
    def __init__(self, name, value=0, duration=0, source=None):
        super().__init__(name, 1, duration, "effect", source=source)
        self.drain = value
        self.drain_listener = Listener("dmg_made", self.l_drain)

    def effect_on(self):
        self.drain_listener.on()

    def effect_off(self):
        self.drain_listener.off()

    def l_drain(self, e):
        if e.name != "echo":
            self._static.adv.add_hp(self.drain * e.count, percent=False)


bufftype_dict["drain"] = DrainBuff


class SelfAffliction(Buff):
    def __init__(self, name="<buff_noname>", value=0, duration=0, rate=100, affname=None, mtype="regen", morder="hp", source=None):
        super().__init__(name, value, duration, mtype, morder, source=source)
        self.name = affname
        self.bufftype = "misc"
        self.affname = affname
        self._rate = rate
        self.affevent = Event("selfaff")
        self.affevent.atype = affname

    @property
    def rate(self):
        affres = self.adv.adv_affres(self.affname)
        return (0 if affres >= 100 else min(100, max(0, self._rate - affres))) / 100

    def on(self, duration=None):
        self.affevent.rate = self.rate
        self.affevent()
        if self.rate > 0:
            return super().on(duration)

    def effect_on(self):
        super().effect_on()
        self.adv.dragonform.set_disabled(self.name)
        for t in self.adv.tension:
            t.has_stack.off()
            t.stack = 0
            log(t.name, "reset", "stack <{}>".format(int(t.stack)))
            t.set_disabled(self.affname)
        try:
            self.regen_timer.on(2.9)
        except AttributeError:
            pass

    def effect_off(self):
        super().effect_off()
        self.adv.dragonform.unset_disabled(self.name)
        for t in self.adv.tension:
            t.unset_disabled(self.affname)

    @allow_acl
    def get(self):
        return super().get() * self.rate


bufftype_dict["selfaff"] = SelfAffliction


class VarsBuff(Buff):
    def __init__(self, name, variable, value=0, duration=-1, limit=1, source=None):
        super().__init__(name, value, duration, "effect", hidden=True, source=source)
        self.variable = variable
        self.limit = limit

    def get(self):
        try:
            return self.adv.__dict__[self.variable]
        except KeyError:
            return 0

    def effect_on(self):
        self.adv.__dict__[self.variable] = min(self.limit, self.get() + self._value)

    def effect_off(self):
        self.adv.__dict__[self.variable] = max(0, self.get() - self._value)


bufftype_dict["vars"] = VarsBuff


class MultiBuffManager:
    def __init__(self, name, buffs, duration=None, timed_mode=False):
        self.name = name
        self.buffs = buffs or []
        # self.buffs = list(filter(None, self.buffs))
        self.duration = duration
        self.skill_buffs = set()
        for b in self.buffs:
            if b.mod_type == "effect":
                b.hidden = True

    def extra_effect_off(self, effect_off):
        for b in self.buffs:
            b.extra_effect_off(effect_off)

    def on(self, duration=None):
        # print([(b.name, b.get()) for b in self.buffs])
        for b in self.buffs:
            try:
                b.on(duration=duration or self.duration)
            except TypeError:
                b.on()
        # print([(b.name, b.get()) for b in self.buffs])
        return self

    def off(self):
        for b in self.buffs:
            b.off()
        return self

    @allow_acl
    def get(self):
        return all(map(lambda b: b.get(), self.buffs))

    def add_time(self, delta):
        for b in self.buffs:
            b.add_time(delta)
        return self

    def pause(self, e=None):
        self.pause_time = self.timeleft()
        if self.pause_time > 0:
            for b in self.buffs:
                b.buff_end_timer.off()
            log("pause", self.pause_by, self.pause_time)

    def resume(self, e=None):
        if self.pause_time > 0:
            for b in self.buffs:
                self.pause_time = max(self.pause_time, b.refresh_time)
            for b in self.buffs:
                b.buff_end_timer.on(self.pause_time)
            log("resume", self.pause_by, self.pause_time, now() + self.pause_time)
        self.pause_time = -1

    def timeleft(self):
        return min([b.timeleft() for b in self.buffs])


class ModeManager(MultiBuffManager):
    ALT_CLASS = {"x": XAltBuff, "fs": FSAltBuff, "s1": SAltBuff, "s2": SAltBuff}

    def __init__(self, name=None, group=None, buffs=None, duration=-1, **kwargs):
        buffs = buffs or []
        self.group = group
        self.alt = {}
        pause = kwargs.get("pause")
        timed_mode = bool(duration != -1 and pause)
        for k, buffclass in ModeManager.ALT_CLASS.items():
            if kwargs.get(k, False):
                if k in ("s1", "s2"):
                    self.alt[k] = buffclass(group=group, duration=duration, base=k, timed_mode=timed_mode, hidden=True)
                elif k in ("x"):
                    self.alt[k] = buffclass(group=group, duration=duration, deferred=(kwargs.get("deferred", False)), hidden=True)
                else:
                    self.alt[k] = buffclass(group=group, duration=duration, hidden=True)
        buffs.extend(self.alt.values())
        super().__init__(name, buffs, duration, timed_mode=timed_mode)
        if timed_mode:
            self.pause_by = group
            if "s" in pause:
                self.l_s = Listener("s", self.pause, order=0).on()
                self.l_s_end = Listener("s_end", self.resume, order=0).on()
            if "dragon" in pause:
                self.l_dragon = Listener("dragon", self.pause, order=0).on()
                self.l_dragon_end = Listener("dragon_end", self.resume, order=0).on()
            if not kwargs.get("source"):
                for b in self.buffs:
                    b.no_bufftime()
            else:
                for b in self.buffs:
                    b.source = kwargs.get("source")

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


def init_mode(*args, source=None):
    kwargs = {}
    for a in args[2:]:
        kwargs[a] = True
    return ModeManager(args[0], args[1], None, **kwargs)


bufftype_dict["mode"] = init_mode


class MultiLevelBuff:
    def __init__(self, name, buffs):
        self.name = name
        self.buffs = buffs or []
        for buff in self.buffs:
            buff.extra_effect_off(self.effect_off)

    def effect_off(self):
        level = self.level - 2
        if level >= 0:
            self.buffs[level].on()

    @property
    def level(self):
        level = -1
        for idx, b in enumerate(self.buffs):
            if b.get():
                level = idx
        return min(level + 1, len(self.buffs))

    def on(self, duration=None):
        level = self.level
        if level == len(self.buffs):
            level -= 1
        for idx, b in enumerate(self.buffs):
            if idx == level:
                b.on()
            else:
                b.off()
        return self

    def off(self):
        for b in self.buffs:
            b.off()
        return self

    @allow_acl
    def get(self):
        if self.level > 0:
            return self.buffs[self.level - 1].get()
        return False

    def add_time(self, delta):
        self.buffs[self.level - 1].add_time(delta)

    def pause(self, e=None):
        self.pause_time = self.timeleft()
        if self.pause_time > 0:
            self.buffs[self.level - 1].buff_end_timer.off()
            log("pause", self.pause_by, self.pause_time)

    def resume(self, e=None):
        if self.pause_time > 0:
            self.pause_time = max(self.pause_time, self.buffs[self.level - 1].refresh_time)
            self.buffs[self.level - 1].buff_end_timer.on(self.pause_time)
            log("resume", self.pause_by, self.pause_time, now() + self.pause_time)
        self.pause_time = -1

    @allow_acl
    def timeleft(self, level=None):
        level = level or self.level
        if len(self.buffs) + 1 > level > 0:
            return self.buffs[level - 1].timeleft()
        return 0


class AmpBuff:
    SELF_AMP = "self"
    TEAM_AMP = "team"
    TYPE_BUFFARGS = {
        1: ("maxhp", "buff"),
        2: ("att", "buff"),
        3: ("defense", "passive"),
        4: ("crit", "damage"),
    }

    def __init__(self, amp_id):
        self.amp_id = amp_id
        amp_data = load_json("amp.json")[amp_id]
        self.publish_level = amp_data["publish"] - 1
        self.max_team_level = 2
        self.extend = amp_data["extend"]
        self.amp_type = amp_data["type"]
        self.mod_type, self.mod_order = AmpBuff.TYPE_BUFFARGS[amp_data["type"]]
        self.buffs = []
        self.name = f"{self.mod_type}_amp"
        for idx, buffargs in enumerate(amp_data["values"]):
            buff = Teambuff(f"{self.name}_seq{idx}", *buffargs, self.mod_type, self.mod_order, source="amp").no_bufftime()
            buff.hidden = True
            buff.modifier.buff_capped = False
            self.buffs.append(buff)
        self.max_len = self.publish_level + self.max_team_level
        self.amp_event = Event("amp")
        self.amp_event.source = self

    def iterate_buffs(self, kind=None, adjust=True):
        base = 0
        if kind == AmpBuff.SELF_AMP:
            idx_range = range(0, self.publish_level)
        elif kind == AmpBuff.TEAM_AMP:
            idx_range = range(self.publish_level, self.publish_level + self.max_team_level)
            base = self.publish_level if adjust else 0
        else:
            idx_range = range(0, self.max_len)
        for idx in idx_range:
            yield idx - base, self.buffs[idx]

    def level(self, kind=None, adjust=True):
        level = -1
        for idx, buff in self.iterate_buffs(kind, adjust=adjust):
            if buff.get():
                level = idx
        return min(level + 1, len(self.buffs))

    def toggle_buffs(self, kind, level, own_max_level=None):
        buff_value = 0
        buff_time = 0
        for idx, b in self.iterate_buffs(kind):
            if idx == level:
                b.bufftype = kind
                if kind == AmpBuff.TEAM_AMP and own_max_level < level:
                    if b.get():
                        b.add_time(self.extend)
                    else:
                        b.on()
                else:
                    b.on()
                buff_value = b.get()
                buff_time = b.timeleft()
            else:
                b.off()

        if level < 0:
            return " lv0"
        else:
            return f" lv{level + 1}({buff_value:.2f}/{buff_time:.2f}s)"

    def on(self, own_max_level, target=0, fleet=0):
        # update max team level to new incoming amp
        self.max_team_level = max(own_max_level, self.max_team_level)

        self_level = self.level(AmpBuff.SELF_AMP)
        team_level = self.level(AmpBuff.TEAM_AMP)
        if target == 2:
            # direct team amp
            publish = True
            team_level += fleet
            team_level = min(team_level, self.max_team_level - 1)
            team_description = self.toggle_buffs(AmpBuff.TEAM_AMP, team_level, own_max_level=own_max_level - 1)
            if self_level == 0:
                self_description = f" lv0"
            else:
                buff = self.buffs[self_level]
                self_description = f" lv{self_level}({buff.get():.2f}/{buff.timeleft():.2f}s)"
        else:
            publish = self_level >= self.publish_level
            if publish:
                self_level = -1
                # more amp from fleet
                team_level += fleet
                team_level = min(team_level, self.max_team_level - 1)
                team_description = self.toggle_buffs(AmpBuff.TEAM_AMP, team_level, own_max_level=own_max_level - 1)
            else:
                if team_level > 0:
                    buff_value = self.buffs[self.publish_level + team_level - 1].get()
                    buff_time = self.buffs[self.publish_level + team_level - 1].timeleft()
                    team_description = f" lv{team_level}({buff_value:.2f}/{buff_time:.2f}s)"
                else:
                    team_description = " lv0"
            self_description = self.toggle_buffs(AmpBuff.SELF_AMP, self_level)
        log("amp", self.name, f"self{self_description}", f"team{team_description}", publish)
        self.amp_event.publish = publish
        self.amp_event()
        return self

    def off(self):
        for _, b in self.iterate_buffs():
            b.off()
        return self

    @allow_acl
    def get(self, kind=TEAM_AMP):
        level = self.level(kind, adjust=False)
        if level > 0:
            return self.buffs[level - 1].get()
        return False

    @allow_acl
    def timeleft(self, kind=TEAM_AMP):
        level = self.level(kind, adjust=False)
        if level > 0:
            return self.buffs[level - 1].timeleft()
        return 0


class ActiveBuffDict(defaultdict):
    def __init__(self):
        super().__init__(lambda: defaultdict(lambda: {}))
        self.overwrite_buffs = {}
        self.amp_buffs = {}

    def check(self, k, group=None, seq=None, *args):
        if self.get(k, False):
            subdict = self[k]
            if group is not None:
                if isinstance(group, int):
                    group -= 1
                if seq is not None:
                    try:
                        return subdict[group][seq].get()
                    except KeyError:
                        return False
                else:
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

    def timeleft(self, k, group="default", seq=None):
        if seq is None:
            try:
                return max((b.timeleft() for b in self[k][group].values()))
            except KeyError:
                pass
            except ValueError:
                return 0
        try:
            return self[k][group][seq].timeleft()
        except KeyError:
            return 0

    def add(self, k, group, seq, buff):
        self[k][group][seq] = buff

    def on(self, k, group, seq):
        return self[k][group][seq].on()

    def off(self, k, group="default", seq=0):
        return self[k][group][seq].off()

    def off_all(self, k, seq=None):
        for g, gbuffs in self[k].items():
            try:
                gbuffs[seq].off()
            except KeyError:
                pass

    def get_overwrite(self, overwrite_group):
        # print(self.overwrite_buffs[overwrite_group], overwrite_group)
        return self.overwrite_buffs[overwrite_group]

    def add_overwrite(self, k, group, seq, buff, overwrite_group):
        self[k][group][seq] = buff
        self.overwrite_buffs[overwrite_group] = buff

    def add_amp(self, k, group, seq, buff, amp_id):
        self[k][group][seq] = buff
        self.amp_buffs[amp_id] = buff

    def get_amp(self, amp_id):
        try:
            amp_id = {
                "maxhp": 1,
                "att": 2,
                "defense": 3,
                "crit_dmg": 4,
            }[amp_id.lower()]
        except (KeyError, AttributeError):
            pass
        if isinstance(amp_id, int):
            # search amp types
            # might lead to shenanigans if multiple id of same type exist
            for amp_buff in self.amp_buffs.values():
                if amp_buff.amp_type == amp_id:
                    return amp_buff
            raise ValueError(f"no amp of type {amp_id}")
        else:
            try:
                return self.amp_buffs[amp_id]
            except KeyError:
                self.amp_buffs[amp_id] = AmpBuff(amp_id)
                return self.amp_buffs[amp_id]

    def check_amp_cond(self, amp_type, target, comp, count):
        level = 0
        target = AmpBuff.TEAM_AMP if target == 2 else AmpBuff.SELF_AMP
        for amp_buff in self.amp_buffs.values():
            if not amp_type or amp_buff.amp_type == amp_type:
                level += amp_buff.level(target)
        # bad chu
        return eval("{}{}{}".format(level, comp, count))
