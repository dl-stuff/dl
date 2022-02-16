from collections import UserDict, defaultdict
from functools import reduce
import operator
import random

from conf import GENERIC_TARGET, SELF, TEAM, ENEMY, AFFLICTION_LIST, AFFRES_PROFILES, load_json, wyrmprints_meta

from core.timeline import Event, Timer, Listener, now
from core.log import log, g_logs
from core.acl import allow_acl


### modifiers

EV_THRESHOLD = 0.00001


class ModifierDict(defaultdict):
    BUFF_LIMITS = {"maxhp": 0.3}

    def __init__(self, *args, **kwargs):
        if args:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(lambda: defaultdict(lambda: []))

    def append(self, modifier):
        self[modifier.mod_type][modifier.mod_order].append(modifier)

    def remove(self, modifier):
        try:
            self[modifier.mod_type][modifier.mod_order].remove(modifier)
        except ValueError:
            pass

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
        capped_sum = 0
        uncapped_sum = 0
        wp_limits = {}
        for modifier in self[mtype][morder]:
            if modifier.limit_group:
                if not modifier.limit_group in wp_limits and modifier.limit_group in wyrmprints_meta["lim_groups"]:
                    lim_group_data = wyrmprints_meta["lim_groups"][modifier.limit_group]
                    wp_limits[modifier.limit_group] = lim_group_data["max"]
                modifier_value = min(wp_limits[modifier.limit_group], modifier.get())
                wp_limits[modifier.limit_group] -= modifier_value
                uncapped_sum += modifier_value
            elif morder == "buff":
                capped_sum += modifier.get()
            else:
                uncapped_sum += modifier.get()
        capped_sum = min(capped_sum, ModifierDict.BUFF_LIMITS.get(mtype, 2.0))
        return capped_sum + uncapped_sum


class Modifier(object):
    MODS = {
        SELF: ModifierDict(),
        TEAM: ModifierDict(),
        ENEMY: ModifierDict(),
    }
    SELF = MODS[SELF]
    TEAM = MODS[TEAM]
    ENEMY = MODS[ENEMY]

    def __init__(self, mtype, order, value, get=None, target="MYSELF"):
        self.mod_value = value
        self.mod_type = mtype
        self.mod_order = order
        self.mod_get = get
        self.target = target
        self.limit_group = None
        self._mod_active = 0
        self.on()

    def all_mod_dicts(self):
        return (self._static.self_mods, self._static.team_mods, self._static.enemy_mods)

    def get(self):
        if self.mod_get is not None:
            return self.mod_value * self.mod_get()
        return self.mod_value

    def on(self):
        if self._mod_active == 1:
            return self

        for generic_target in GENERIC_TARGET[self.target]:
            self.MODS[generic_target].append(self)

        self._mod_active = 1
        return self

    def off(self):
        if self._mod_active == 0:
            return self
        self._mod_active = 0
        for mod_dict in self.MODS.values():
            try:
                mod_dict.remove(self)
            except ValueError:
                pass
        return self

    def __enter__(self):
        self.on()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.off()

    def same_kind(self, other):
        return self.target == other.target and self.mod_type == other.mod_type and self.mod_order == other.mod_order

    def __ge__(self, other):
        if not self.same_kind(other):
            raise ValueError(f"Cannot compare {self} and {other}")
        if self.target == ENEMY:
            return self.mod_value <= other.mod_value
        else:
            return self.mod_value >= other.mod_value

    def __repr__(self):
        if self.limit_group:
            return "<{} {} {} {} lg{}>".format(
                self.target,
                self.mod_type,
                self.mod_order,
                self.get(),
                self.limit_group,
            )
        return "<{} {} {} {}>".format(
            self.target,
            self.mod_type,
            self.mod_order,
            self.get(),
        )


class KillerModifier(Modifier):
    def __init__(self, value, killer_states, order="hit", get=None, target="MYSELF"):
        if "afflicted" in killer_states:
            self.killer_states = AFFLICTION_LIST
        else:
            self.killer_states = killer_states
        self._killer_mtypes = [f"killer_{kstate}" for kstate in killer_states]
        super().__init__(f"combined_{killer_states}", order, value, get=get, target=target)

    def on(self):
        if self._mod_active == 1:
            return self

        for kmtype in self._killer_mtypes:
            for generic_target in GENERIC_TARGET[self.target]:
                self.MODS[generic_target][kmtype][self.mod_order].append(self)

        self._mod_active = 1
        return self

    def off(self):
        if self._mod_active == 0:
            return self

        for kmtype in self._killer_mtypes:
            for generic_target in GENERIC_TARGET[self.target]:
                self.MODS[generic_target][kmtype][self.mod_order].remove(self)

        self._mod_active = 0
        return self

    def __repr__(self):
        return "<{} {} {} {}>".format(
            self.target,
            self.killer_states,
            self.mod_order,
            self.get(),
        )


class CrisisModifier(Modifier):
    def __init__(self, get_hp, mtype, order="crisis", target="MYSELF"):
        self.get_hp = get_hp
        self.passive = None
        self.per_hit = None
        super().__init__(mtype, order, 1, get=self.c_mod_value, target=target)

    def set_passive(self, value):
        if self.passive is None:
            self.passive = value
        else:
            self.passive = max(self.passive, value)

    def set_per_hit(self, value):
        self.per_hit = value

    def c_mod_value(self):
        max_mod = 0
        if self.passive is not None:
            max_mod = max(max_mod, self.passive)
        if self.per_hit is not None:
            max_mod = max(max_mod, self.per_hit)
        if max_mod > 0:
            return max_mod * ((100 - self.get_hp()) ** 2) / 10000
        else:
            return 0


class AffEV:
    def __init__(self, allaff, aff, tolerance) -> None:
        self._allaff = allaff
        self.aff = aff
        self._edge_mtype = f"edge_{self.aff}"
        self._affres_mtype = f"affres_{self.aff}"
        self.aff_event = Event("aff")
        self.aff_event.atype = self.aff
        self.tolerance = tolerance
        self.get_override = None
        self.reset(0.0)

    def reset(self, resist):
        self.resist = resist
        self._res_states = self._init_state()
        self._res_states[self.resist] = 1.0
        self._stacks = {}
        self._get = 0
        self._uptime = (0, 0)

    def get(self):
        return self.get_override or self._get

    @staticmethod
    def _mul_no_p(acc, value):
        return acc * max(0, 1.0 - value[1])

    def uptime(self):
        next_r = self.get()
        next_t = now()
        prev_r, prev_t = self._uptime
        rate = prev_r + next_r * (next_t - prev_t)
        self._uptime = (rate, next_t)
        if next_t > 0 and rate > 0:
            log(
                "uptime",
                self.aff,
                "{:.2f}/{:.2f}".format(rate, next_t),
                "{:.2%}".format(rate / next_t),
            )

    def update(self, slip_dmg=None):
        self.uptime()
        exist_p = 1.0 - reduce(AffEV._mul_no_p, self._stacks.values(), 1.0)
        if slip_dmg is not None:
            slip_dmg.on(ev=exist_p)
        self._get = exist_p

    def _init_state(self):
        return defaultdict(float)

    def edge_mod(self):
        return Modifier.SELF.mod(self._edge_mtype, operator=operator.add, initial=0.0) + Modifier.SELF.mod("edge_all", operator=operator.add, initial=0.0)

    def affres_mod(self):
        return Modifier.ENEMY.mod(self._affres_mtype, operator=operator.add, initial=0.0) + Modifier.SELF.mod("affres_all", operator=operator.add, initial=0.0)

    def on(self, actcond, stack_key, extra_p=1.0, slip_dmg=None):
        total_success_p = 0.0
        rate = actcond._rate
        rate = rate + self.edge_mod()
        n_states = self._init_state()
        for res, state_p in self._res_states.items():
            res = max(0, res + self.affres_mod())
            if res >= rate or res >= 1:
                n_states[res] += state_p
            else:
                rate_after_res = min(1.0, rate - res) * extra_p
                success_p = state_p * rate_after_res
                fail_p = state_p * (1.0 - rate_after_res)
                total_success_p += success_p
                n_states[res + self.tolerance] += success_p
                if fail_p > 0:
                    n_states[res] += fail_p
        if total_success_p > EV_THRESHOLD:
            self._res_states = n_states
            self._stacks[stack_key] = (actcond, total_success_p)
            self.update(slip_dmg=slip_dmg)
            self.aff_event.ev = self._get
            self.aff_event()
            return total_success_p
        else:
            self._get = 0
            return 0.0

    def off(self, stack_key):
        del self._stacks[stack_key]
        self.update()


class AffEVCapped(AffEV):
    def __init__(self, allaff, aff, tolerance, group=None) -> None:
        self.group = group
        super().__init__(allaff, aff, tolerance)

    def on(self, rate, stack_key, extra_p=1.0, slip_dmg=None):
        if self.group:
            no_stack_p = 1.0
            for aff in self.group:
                no_stack_p *= 1.0 - self._allaff[aff].get()
        else:
            no_stack_p = 1.0 - self._allaff[self.aff].get()
        return super().on(rate, stack_key, extra_p=(extra_p * no_stack_p))


class Afflictions(UserDict):
    UNCAPPED = ("poison", "burn", "paralysis", "frostbite", "flashburn", "shadowblight", "stormlash", "scorchrend")
    CAPPED_SCC = ("bog", "blind")
    CAPPED_CC = ("freeze", "stun", "sleep")

    def __init__(self) -> None:
        super().__init__()
        for aff in Afflictions.UNCAPPED:
            self[aff] = AffEV(self, aff, 0.05)
        for aff in Afflictions.CAPPED_CC:
            self[aff] = AffEVCapped(self, aff, 0.2, Afflictions.CAPPED_CC)
        self["bog"] = AffEVCapped(self, "bog", 0.2)
        self["blind"] = AffEVCapped(self, "blind", 0.1)

    def set_resist(self, profile):
        for aff, initial in AFFRES_PROFILES[profile].items():
            self[aff].reset(initial)

    def get_uptimes(self):
        uptimes = {}
        for atype, aff in self.items():
            aff.uptime()
            rate, t = aff._uptime
            if rate > 0:
                uptimes[atype] = rate / t
        return uptimes.items()


class Bleed:
    CAP = 3

    def __init__(self, adv) -> None:
        self._adv = adv
        self.slip_timer = None
        self._stacks = {}
        self._dmg_by_source = defaultdict(list)
        self._mod = 0

    def tick(self, t):
        for source, values in self._dmg_by_source.items():
            log("dmg", f"{source[0]}_bleed", self._mod * sum(values), self._mod, "+".join((f"{value:.2f}" for value in values)))

    def update(self):
        self._mod = 0.5 + len(self._stacks) / 2
        self._dmg_by_source = defaultdict(list)
        for stack_key, value in self._stacks.items():
            self._dmg_by_source[stack_key[1]].append(value[1])

    def on(self, actcond, dtype, stack_key):
        rate = actcond.get_rate()
        if random.random() <= rate:

            if len(self._stacks) >= Bleed.CAP:
                oldest_bleed = min(self._stacks.keys(), key=lambda k: k[0])
                del self._stacks[oldest_bleed]
            self._stacks[stack_key] = (actcond, self._adv.dmg_formula(stack_key[1], actcond.slip["value"][1], dtype=dtype, actcond_dmg=True))
            if self.slip_timer is None:
                # self.slip_timer = Timer(self.tick, actcond.slip["iv"], repeat=True)
                self.slip_timer = Timer(self.tick, 4.99, repeat=True)
                self.slip_timer.on()

            self.update()
            return True

        return False

    def get(self):
        return len(self._stacks)

    def off(self, stack_key):
        del self._stacks[stack_key]
        self.update()


class BleedEV(Bleed):
    def __init__(self, adv) -> None:
        super().__init__(adv)
        self._stack_states = {tuple((None for _ in range(Bleed.CAP))): 1.0}
        self._get = 1

    def tick(self, t):
        for source, value in self._dmg_by_source.items():
            log("dmg", f"{source[0]}_bleed", value, self._get)

    def get(self):
        return self._get

    def update(self):
        self._get = 0
        self._dmg_by_source = defaultdict(float)
        for state, state_p in self._stack_states.items():
            get = sum((int(stack is not None) for stack in state))
            self._get += get * state_p
            mod = 0.5 + (get / 2)
            for stack_key in state:
                if stack_key is not None:
                    self._dmg_by_source[stack_key[1]] += self._stacks[stack_key][1] * state_p * mod

    def on(self, actcond, dtype, stack_key):
        self._stacks[stack_key] = (actcond, self._adv.dmg_formula(stack_key[1], actcond.slip["value"][1], dtype=dtype, actcond_dmg=True))
        if self.slip_timer is None:
            self.slip_timer = Timer(self.tick, actcond.slip["iv"], repeat=True)
            self.slip_timer.on()

        rate = actcond.get_rate()
        n_states = defaultdict(float)

        for state, state_p in self._stack_states.items():
            state = [stack for stack in state if stack in self._stacks]
            fail_p = state_p * (1 - rate)
            success_p = state_p * rate
            if len(state) < 3:
                fail_state = list(state)
                while len(fail_state) < Bleed.CAP:
                    fail_state.append(None)
                success_state = list(state)
                success_state.append(stack_key)
                while len(success_state) < Bleed.CAP:
                    success_state.append(None)
            else:
                fail_state = state
                success_state = state[1:] + [stack_key]
            n_states[tuple(fail_state)] += fail_p
            n_states[tuple(success_state)] += success_p

        for state, state_p in n_states.copy().items():
            if state_p < EV_THRESHOLD:
                del n_states[state]
        n_states[tuple((None for _ in range(Bleed.CAP)))] = 1 - sum(n_states.values())

        self._stack_states = n_states

        self.update()
        return True

    def off(self, stack_key):
        del self._stacks[stack_key]

        n_states = defaultdict(float)

        for state, state_p in self._stack_states.items():
            state = [stack for stack in state if stack in self._stacks]
            while len(state) < 3:
                state.append(None)
            n_states[tuple(state)] = state_p

        self._stack_states = n_states
        self.update()


class SlipDmg:
    def __init__(self, actcond, data, source, dtype, target, ev=1) -> None:
        self._actcond = actcond
        self._adv = actcond._adv
        self._data = data
        self.iv = data.get("iv")
        self.kind = data.get("kind")
        self.func, self.value = data.get("value")
        self.is_percent = self.func == "percent"
        self.slip_timer = Timer(self.tick, self.iv, 1)
        self.slip_value = None
        self.source = source
        self.dtype = dtype
        self.target = target

    def on(self, ev=1):
        if not self.slip_timer.online:
            self.slip_timer.on()
        if self.func == "mod":
            value = self._adv.dmg_formula(self.source, self.value, dtype=self.dtype, actcond_dmg=True)
        elif self.func == "heal":
            value = self._adv.heal_formula(self.source, self.value)
        else:
            value = self.value
        self.slip_value = (self.source, self.target, value * ev)

    def off(self):
        self.slip_value = None
        self.slip_timer.off()

    def tick(self, e):
        source, target, value = self.slip_value
        if ENEMY in GENERIC_TARGET[target]:
            if self.kind is None:
                log("dmg", f"{source}_{self._actcond.aff}", value, 0)
        else:
            if self.kind == "corrosion":  # TODO: corrosion maffs
                self._adv.add_hp(value, percent=self.is_percent, can_die=True)
            elif self.kind == "hp":
                self._adv.add_hp(value, percent=self.is_percent)
            elif self.kind == "sp":
                target = self._data.get("target")
                if self.is_percent:
                    self._adv.charge_p("sp_regen", value, target=target)
                else:
                    self._adv.charge("sp_regen", value, target=target)
            else:  # self affliction
                self._adv.add_hp(-100 * value, percent=self.is_percent)

    def get(self):
        return self.slip_value is not None


class ActCond:
    def __init__(self, adv, id, target, data):
        g_logs.log_conf("actcond", id, data)
        self._adv = adv
        self.id = id
        self.target = target
        self.generic_target = GENERIC_TARGET[self.target]
        self.dtype = None
        self.is_zone = False

        self.aff = data.get("aff")

        self.hidden = bool(data.get("hide"))
        self.text = data.get("text") or self.aff
        self.icon = data.get("icon")
        self.overwrite = data.get("overwrite")
        self.refresh = data.get("refresh")
        self.maxstack = data.get("maxstack")
        self._rate = data.get("rate", 1.0)
        self.coei = bool(data.get("coei"))
        self.debuff = bool(data.get("debuff"))
        self.unremovable = bool(data.get("unremovable"))
        if data.get("lost_on_drg"):
            self.l_drg = Listener("dragon", self.all_off)

        self.remove_id = data.get("remove")
        self.lvl_up_id = data.get("lvl_up")
        self.lvl_down_id = data.get("lvl_down")

        self.count = data.get("count")
        self.maxcount = data.get("maxcount")
        self.addcount = bool(data.get("addcount"))
        self._adv.current_count = 0

        self.duration = data.get("duration")
        self.duration_scale = data.get("duration_scale")
        self.cooldown = data.get("cd")
        self.cooldown_timer = None

        self.dispel = data.get("dispel")
        self.relief = data.get("relief")

        self.buff_stack = {}

        self.slip = data.get("slip")
        self.slip_stack = {}
        self.is_bleed = False
        if self.slip:
            self.is_bleed = self.slip.get("kind") == "bleed"

        self.alt = data.get("alt")
        if self.alt:
            self.alt_has_s = any((sn in self.alt for sn in ("s1", "s2", "s3", "s4")))
            if self.alt_has_s:
                self.l_s = Listener("s", self.l_alt_s_pause, order=0).off()
                self.l_s_end = Listener("s_end", self.l_alt_s_resume, order=0).off()
            self.l_act_count_end = []
            if self.count:
                if "fs" in self.alt:
                    self.l_act_count_end.append(Listener("fs", self.l_alt_count, order=0).off())
                if self.alt_has_s:
                    self.l_act_count_end.append(Listener("s", self.l_alt_count, order=0).off())

        self.mod_list = []
        self.is_doublebuff = False
        if mod_args := data.get("mods"):
            for mod in mod_args:
                value, mtype, morder = mod
                self.mod_list.append(Modifier(mtype, morder, value, self.get, target=self.target))
                self.is_doublebuff = self.is_doublebuff or (mtype == "def" and morder == "buff")

        self.actcond_event = Event("actcond")
        self.actcond_event.actcond = self
        self.actcond_event.source = None
        self.actcond_event.dtype = None

    @property
    def stacks(self):
        return len(self.buff_stack)

    def get(self):
        return sum((ev for _, ev in self.buff_stack.values()))

    def log(self, *args):
        log("actcond", *args)

    def __repr__(self) -> str:
        return f"{self.text} ({self.id}-{self.target})"

    def get_rate(self):
        if self.debuff:
            return min(1.0, self._rate + Modifier.SELF.mod("debuffrate", operator=operator.add, initial=0))
        return self._rate

    def bufftime(self, dtype="s"):
        if self.aff and ENEMY in self.generic_target:
            return Modifier.SELF.mod(f"afftime_{self.aff}", operator=operator.add)
        else:
            if dtype == "s":
                if self.debuff:
                    return Modifier.SELF.mod("debufftime", operator=operator.add)
                else:
                    return Modifier.SELF.mod("bufftime", operator=operator.add)
            else:
                if self.debuff:
                    return 1.0
                else:
                    return 1.0 + Modifier.SELF.sub_mod("bufftime", "ex")

    def update_debuff_rates(self, debuff_rates):
        for mod in self.mod_list:
            dkey = f"debuff_{mod.mod_type}"
            for _, ev in self.buff_stack.values():
                debuff_rates[dkey] *= 1 - ev

    def l_on(self, e):
        return self.on(e.source, e.target)

    @allow_acl
    def check(self, zone=None):
        if self._adv.nihilism and not (self.coei or self.debuff) and (SELF in self.generic_target or TEAM in self.generic_target):
            return False
        if zone is not None and (can_zone := self._adv.active_actconds.can_zone(self)):
            return can_zone
        if (can_overwrite := self._adv.active_actconds.can_overwrite(self)) is not None:
            return can_overwrite
        if self.stacks == self.maxstack or self.stacks == self.count or (self.stacks == 1 and self.refresh):
            self.off(hide_msg=True)
            return "refresh"
        return "start"

    def on(self, source, dtype, ev=1, zone=None):
        self.dtype = dtype
        if self._adv.active_actconds.lvl_up_actcond(self, source, dtype, ev=1):
            return True
        state_msg = self.check(zone=zone)
        if not state_msg:
            return False
        if self.cooldown:
            if self.cooldown_timer:
                cd_timeleft = self.cooldown_timer.timeleft()
                self.cooldown_timer.off()
                self.cooldown_timer = Timer(self.l_on, cd_timeleft)
                self.cooldown_timer.source = source
                self.cooldown_timer.target = self.target
                self.cooldown_timer.on()
                return True
            else:
                self.cooldown_timer = Timer(timeout=self.cooldown)
                self.cooldown_timer.on()

        # skip the usual if it's an removing actcond
        if self.remove_id is not None:
            self.remove_actcond()
            self.log("remove", self.remove_id, self.count or "all", f"{self.id}-{self.target}")
            return True

        stack_key = (now(), source)
        while stack_key in self.buff_stack:
            stack_key = (stack_key[0] + 0.000001, *stack_key[1:])

        duration = -1
        duration_repr = "Forever"
        timer = None
        if zone:
            self.is_zone = True
            duration = zone
        elif self.duration:
            duration = self.duration * self.bufftime(dtype)
        if duration > -1:
            timer = Timer(self.l_off, duration)
            timer.stack_key = stack_key
            timer.reason = "timeout"
            timer.on()
            duration_repr = str(duration)
        elif self.count:
            if self.addcount:
                self.current_count = max(self.current_count + self.count, self.maxcount)
            else:
                self.current_count = self.count
            duration_repr = f"x{self.current_count}"
        self.buff_stack[stack_key] = (timer, ev * self.get_rate())

        self.effect_on(source, dtype, stack_key, timer=timer)
        self.log(state_msg, self.text, f"stack {self.stacks}", duration_repr, f"{self.id}-{self.target}")

        self.actcond_event.source = source
        self.actcond_event.dtype = dtype
        self.actcond_event()
        return True

    def _off(self, stack_key, hide_msg=False):
        timer, _ = self.buff_stack.pop(stack_key)
        if timer is not None:
            timer.off()
        self.effect_off(stack_key)
        if hide_msg:
            return
        timing, source = stack_key
        if source[1] is None:
            source = f"{source[0]}-N"
        else:
            source = f"{source[0]}-{source[1]}"
        self.log("end", self.text, f"stack {self.stacks}", f"from {source} at {timing:<.3f}s", f"{self.id}-{self.target}")

    def off(self, hide_msg=False):
        if self.buff_stack:
            stack_key = min(self.buff_stack.keys())
            self._off(stack_key, hide_msg=hide_msg)

    def l_off(self, e):
        self._off(e.stack_key)
        if getattr(e, "reason", None) == "timeout":
            self._adv.active_actconds.lvl_down_actcond(self, e.stack_key[1])

    def all_off(self, e=None, hide_msg=False):
        for stack_key in self.buff_stack.copy().keys():
            self._off(stack_key, hide_msg=hide_msg)

    def remove_actcond(self):
        for gtarget in self.generic_target:
            try:
                if self.count:
                    for _ in range(self.count):
                        self._adv.active_actconds.by_generic_target[gtarget][self.remove_id].off()
                else:
                    self._adv.active_actconds.by_generic_target[gtarget][self.remove_id].all_off()
            except KeyError:
                pass

    def effect_on(self, source, dtype, stack_key, timer=None):
        slip_dmg = None
        if self.slip is not None:
            if self.is_bleed:
                self._adv.bleed.on(self, dtype, stack_key)
            else:
                slip_dmg = SlipDmg(self, self.slip, source[0], dtype, self.target)
        if self.aff and not self.relief:
            if ENEMY in self.generic_target:
                if self._adv.afflictions[self.aff].on(self, stack_key, slip_dmg=slip_dmg):
                    self.slip_stack[stack_key] = slip_dmg
            elif slip_dmg:
                selfaff = Event("selfaff")
                selfaff.atype = self.aff
                selfaff.ev = 1  # selfaff abilities always proc, even when resisted
                selfaff.on()
                if (ev := self._rate - Modifier.SELF.mod(f"affres_{self.aff}", operator=operator.add, initial=0)) > EV_THRESHOLD:
                    slip_dmg.on(ev=ev)
                    self.slip_stack[stack_key] = slip_dmg

        if self.alt:
            for act, group in self.alt.items():
                self._adv.current.set_action(act, group)
            if self.alt_has_s and timer is not None:
                self.l_s.on()
                self.l_s_end.on()
            elif self.l_act_count_end:
                for listener in self.l_act_count_end:
                    listener.on()

    def effect_off(self, stack_key):
        if self.is_bleed:
            log("effect_off", "bleed")
            self._adv.bleed.off(stack_key)
        elif stack_key in self.slip_stack:
            if self.aff and not self.relief and ENEMY in self.generic_target:
                self._adv.afflictions[self.aff].off(stack_key)
            if self.slip is not None:
                try:
                    self.slip_stack[stack_key].off()
                    del self.slip_stack[stack_key]
                except KeyError:
                    pass

        if self.alt:
            for act, group in self.alt.items():
                self._adv.current.unset_action(act, group)
            if self.alt_has_s and stack_key[0] is not None:
                self.l_s.off()
                self.l_s_end.off()
            elif self.l_act_count_end:
                for listener in self.l_act_count_end:
                    listener.on()

    def _apply_stack_timer_func(self, func_name, stack_key=None):
        if stack_key is None:
            return list(filter(None, (getattr(timer, func_name)() for timer, _ in self.buff_stack.values() if timer is not None)))
        else:
            return getattr(self.buff_stack[stack_key][0], func_name)()

    def pause(self, stack_key=None):
        return self._apply_stack_timer_func("pause", stack_key=stack_key)

    def resume(self, stack_key=None):
        return self._apply_stack_timer_func("resume", stack_key=stack_key)

    def timeleft(self, stack_key=None):
        return max(self._apply_stack_timer_func("timeleft", stack_key=stack_key))

    def l_alt_s_pause(self, e):
        if self.alt.get(e.base) == e.group:
            if timers := self.pause():
                timer = timers[-1]
                log("alt_skill", "pause", timer.timing, timer.pause_time)

    def l_alt_s_resume(self, e):
        if self.alt.get(e.act.base) == e.act.group:
            if timers := self.resume():
                timer = timers[-1]
                log("alt_skill", "resume", timer.timing, timer.timing - now())

    def l_alt_count(self, e):
        if self.alt.get(e.base) == e.group:
            self.current_count -= 1
            if self.current_count == 0:
                self.off()


class AmpContext:
    def __init__(self, mod_type, mod_order, target, values, off_cb) -> None:
        self.level = 0
        self.timer = Timer(self.off, timeout=1)
        self.off_cb = off_cb
        self.modifier = Modifier(mod_type, mod_order, 1, target=target, get=self.get)
        self.values = values

    def on(self, max_level, publish=False, extend=None):
        self.level += 1
        if self.level > max_level:
            if publish:
                self.timer.off()
                self.level = 0
                return True
            else:
                self.level = max_level
        if extend is None:
            self.timer.on(self.values[self.level - 1][1])
        else:
            self.timer.add(extend)
        return False

    def get(self):
        if self.level == 0:
            return 0
        return self.values[self.level - 1][0]

    def off(self, t=None):
        self.level = 0
        self.off_cb()

    def __repr__(self) -> str:
        if self.level == 0:
            return "lv0"
        return f"lv{self.level}({self.get()}/{self.timer.timeleft():.2f})"


class Amp:
    MOD_ARGS = {
        1: ("maxhp", "buff"),
        2: ("att", "buff"),
        3: ("def", "buff"),
        4: ("critdmg", "buff"),
    }

    @staticmethod
    def initialize():
        id_to_amp = {amp_id: Amp(amp_id, **data) for amp_id, data in load_json("amp.json").items()}
        type_to_amp = {}
        for amp in id_to_amp.values():
            if amp.amp_id.endswith("0000"):
                type_to_amp[amp.type] = amp
        return id_to_amp, type_to_amp

    def __init__(self, amp_id, publish=None, extend=None, type=None, values=None):
        self.amp_id = amp_id
        self.publish = publish
        self.extend = extend
        self.type = type
        self.mod_type, self.mod_order = Amp.MOD_ARGS[type]
        self.name = f"{self.mod_type}_amp"

        self.amp_ctx_myself = AmpContext(self.mod_type, self.mod_order, "MYSELF", values[0 : self.publish - 1], self.log)
        self.amp_ctx_myparty = AmpContext(self.mod_type, self.mod_order, "MYPARTY", values[self.publish - 1 :], self.log)
        self.amp_ctx_lookup = {
            0: self.amp_ctx_myself,
            2: self.amp_ctx_myparty,
            "self": self.amp_ctx_myself,
            "team": self.amp_ctx_myparty,
        }
        self.max_level = 1

    def on(self, max_level, target):
        if will_publish := (target == 2 or self.amp_ctx_myself.on(self.publish - 1, publish=True)):
            self.max_level = max(self.max_level, max_level)
            self.amp_ctx_myparty.on(self.max_level, extend=self.extend if max_level < self.max_level else None)
        self.log(will_publish=int(will_publish))

    def log(self, will_publish=0):
        log("amp", self.name, f"self {self.amp_ctx_myself}", f"team {self.amp_ctx_myparty}", will_publish)


class ActiveActconds(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self.by_source = defaultdict(dict)
        self.by_generic_target = defaultdict(dict)
        self.by_overwrite = {}
        self.by_zone = {SELF: set(), TEAM: set(), ENEMY: set()}
        self.by_aff = {aff: [] for aff in AFFLICTION_LIST}

    def can_overwrite(self, actcond):
        if not actcond.overwrite:
            return None
        c_actcond = None
        for gtarget in actcond.generic_target:
            try:
                c_actcond = self.by_overwrite[(gtarget, actcond.overwrite)]
            except KeyError:
                continue
            if c_actcond is None:
                return "start"
            if all((n_mod >= c_mod for n_mod, c_mod in zip(actcond.mod_list, c_actcond.mod_list))):
                c_actcond.all_off(hide_msg=True)
                return "refresh"
        return False

    def lvl_up_actcond(self, actcond, source, dtype, ev=1):
        if not actcond.lvl_up_id:
            return False
        c_actcond = actcond
        found_actconds = [actcond]
        while (actcond_key := (c_actcond.lvl_up_id, c_actcond.target)) in self:
            c_actcond = self.get(actcond_key)
            found_actconds.append(c_actcond)
        highest_active = None
        for idx, c_actcond in enumerate(found_actconds):
            if c_actcond.get():
                highest_active = idx
        if highest_active is not None:
            highest_actcond = found_actconds[highest_active]
            if highest_actcond.lvl_up_id:
                highest_actcond.off(hide_msg=True)
                try:
                    found_actconds[highest_active + 1].on(source, dtype, ev=ev)
                except IndexError:
                    actcond._adv.actcond_make(highest_actcond.lvl_up_id, highest_actcond.target, source, dtype=dtype, ev=ev)
            else:
                highest_actcond.on(source, dtype, ev=ev)
            return True
        return False

    def lvl_down_actcond(self, actcond, source):
        if not actcond.lvl_down_id:
            return False
        if down_actcond := self.get((actcond.lvl_down_id, actcond.target)):
            down_actcond.on(source, actcond.dtype)
            return True
        return False

    def can_zone(self, actcond):
        zone_set = set()
        for gtarget in actcond.generic_target:
            zone_set.update(self.by_zone[gtarget])
        zone_count = sum((zac.stacks for zac in zone_set))
        if zone_count >= 4:
            oldest_zone = None
            for zac in zone_set:
                if oldest_zone is None:
                    oldest_zone = (zac, min(zac.buff_stack.keys()))
                else:
                    if (c_oldest := min(zac.buff_stack.keys())) < oldest_zone[1]:
                        oldest_zone = (zac, c_oldest)
            oldest_zone[0]._off(c_oldest, hide_msg=True)
        return "start"

    def add(self, actcond, actcond_source):
        abs_key = (actcond.id, actcond.target)
        if abs_key not in self:
            self[abs_key] = actcond
        name, aseq = actcond_source
        if aseq is not None:
            self.by_source[name][aseq] = actcond
        for gtarget in actcond.generic_target:
            self.by_generic_target[gtarget][actcond.id] = actcond
            if actcond.overwrite:
                self.by_overwrite[(gtarget, actcond.overwrite)] = actcond
            if actcond.is_zone:
                self.by_zone[gtarget].add(actcond)
        if actcond.aff and ENEMY in actcond.generic_target:
            self.by_aff[actcond.aff].append(actcond)

    def check(self, name, aseq=None):
        if aseq is not None:
            try:
                return self.by_source[name][aseq].get()
            except KeyError:
                pass
        else:
            return any((actcond.get() for actcond in self.by_source[name].values()))

    def stacks(self, actcond_id, target=SELF):
        try:
            return self.by_generic_target[target][str(actcond_id)].stacks
        except KeyError:
            return 0

    def aff_timeleft(self, afflictname):
        try:
            return max((actcond.timeleft() for actcond in self.by_aff[afflictname]))
        except (KeyError, ValueError):
            return 0
