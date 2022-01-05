from collections import UserDict, UserList, defaultdict
from functools import reduce
import operator

from conf import GENERIC_TARGET, SELF, TEAM, ENEMY, AFFLICTION_LIST, AFFRES_PROFILES, wyrmprints_meta

from core.timeline import Event, Timer, Listener, now
from core.log import log, g_logs
from core.acl import allow_acl


### modifiers


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
    THRESHOLD = 0.00001

    def __init__(self, allaff, aff, tolerance) -> None:
        self._allaff = allaff
        self.aff = aff
        self._edge_mtype = f"edge_{self.aff}"
        self._affres_mtype = f"affres_{self.aff}"
        self.aff_event = Event(self.aff)
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
        return acc * max(0, 1.0 - value)

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
        return Modifier.SELF.mod(self._edge_mtype, operator=operator.add, initial=0.0)

    def affres_mod(self):
        return Modifier.ENEMY.mod(self._affres_mtype, operator=operator.add, initial=0.0)

    def on(self, rate, stack_key, extra_p=1.0, slip_dmg=None):
        total_success_p = 0.0
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
        if total_success_p > AffEV.THRESHOLD:
            self._res_states = n_states
            self._stacks[stack_key] = total_success_p
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

    def on(self, rate, stack_key, extra_p=1.0):
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
        log("slip_dmg", value, ev)

    def off(self):
        self.slip_value = None
        self.slip_timer.off()

    def tick(self, e):
        source, target, value = self.slip_value
        if ENEMY in GENERIC_TARGET[target]:
            if self.kind is None:
                log("dmg", f"{source}_{self._actcond.aff}", value, 0)
            elif self.kind == "bleed":  # TODO: handle mbleed
                log("dmg", f"{source}_bleed", value * (0.5 + 0.5 * self._adv.get_slipcount(self.kind)), 0)
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
                self._adv.add_hp(-value, percent=self.is_percent)

    def get(self):
        return self.slip_value is not None


class ActCond:
    def __init__(self, adv, id, target, data):
        g_logs.log_conf("actcond", id, data)
        self._adv = adv
        self.id = id
        self.target = target
        self.generic_target = GENERIC_TARGET[self.target]

        self.aff = data.get("aff")

        self.hidden = bool(data.get("hide"))
        self.text = data.get("text") or self.aff
        self.icon = data.get("icon")
        self.overwrite = data.get("overwrite")
        self.maxstack = data.get("maxstack")
        self._rate = data.get("rate", 1.0)
        self.coei = bool(data.get("coei"))
        self.debuff = bool(data.get("debuff"))
        self.unremovable = bool(data.get("unremovable"))
        if data.get("lost_on_drg"):
            self.l_drg = Listener("dragon", self.all_off)

        self.remove_id = data.get("remove")
        self.duration = data.get("duration")
        self.duration_scale = data.get("duration_scale")
        self.duration_count = data.get("count")
        self.duration_maxcount = data.get("maxcount")
        self.duration_addcount = data.get("addcount")
        self.cooldown = data.get("cd")
        self.cooldown_timer = None

        self.dispel = data.get("dispel")
        self.relief = data.get("relief")

        self.buff_stack = {}

        self.slip = data.get("slip")
        self.slip_stack = {}

        self.mod_list = []
        if mod_args := data.get("mods"):
            for mod in mod_args:
                value, mtype, morder = mod
                self.mod_list.append(Modifier(mtype, morder, value, self.get, target=self.target))

    def get(self):
        return sum((stack[1] for stack in self.buff_stack.values()))

    def log(self, *args):
        if not self.hidden:
            log("actcond", *args)

    @property
    def stack(self):
        return len(self.buff_stack)

    @property
    def rate(self):
        if self.debuff:
            return self._rate + Modifier.SELF.mod("debuffrate", operator=operator.add, initial=0)
        return self._rate

    def bufftime(self, dtype="s"):
        if self.aff:
            return 1.0
        elif dtype == "s":
            if self.debuff:
                return Modifier.SELF.mod("debufftime", operator=operator.add)
            else:
                return Modifier.SELF.mod("bufftime", operator=operator.add)
        else:
            if self.debuff:
                return 1.0
            else:
                return 1.0 + Modifier.SELF.sub_mod("bufftime", "ex")

    def l_on(self, e):
        return self.on(e.source, e.target)

    @allow_acl
    def check(self, source):
        if self._adv.nihilism and not (self.coei or self.debuff) and (SELF in self.generic_target or TEAM in self.generic_target):
            return False
        return True

    def on(self, source, dtype, ev=1):
        if not self.check(source):
            return False
        if self.stack == self.maxstack or self.overwrite == -1:
            self.off()
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

        stack_key = (now(), source)

        duration = -1
        timer = None
        if self.duration:
            duration = self.duration * self.bufftime(dtype)
            timer = Timer(self.l_off, duration)
            timer.stack_key = stack_key
            timer.on()
        self.buff_stack[stack_key] = (timer, ev)

        self.effect_on(source, dtype, stack_key)
        self.log("start", self.text, f"stack {self.stack}", duration, self.id, self.target)

    def _off(self, stack_key):
        timer, _ = self.buff_stack.pop(stack_key)
        if timer is not None:
            timer.off()
        self.effect_off(stack_key)
        self.log("end", self.text, f"stack {self.stack}", f"from {stack_key[1]} at {stack_key[0]:<.3f}s", self.id, self.target)

    def off(self):
        if self.buff_stack:
            stack_key = min(self.buff_stack.keys())
            self._off(stack_key)

    def l_off(self, e):
        self._off(e.stack_key)

    def all_off(self, e):
        for stack_key, timer in self.buff_stack.items():
            if timer is not None:
                timer.off()
            self.effect_off(stack_key)
        self.buff_stack = {}

    def effect_on(self, source, dtype, stack_key):
        slip_dmg = None
        if self.slip is not None:
            slip_dmg = SlipDmg(self, self.slip, source[0], dtype, self.target)
        if self.aff and not self.relief:
            if ENEMY in self.generic_target:
                if self._adv.afflictions[self.aff].on(self._rate, stack_key, slip_dmg=slip_dmg):
                    self.slip_stack[stack_key] = slip_dmg
            else:
                selfaff = Event("selfaff")
                selfaff.atype = self.aff
                selfaff.on()
                slip_dmg.on()
                self.slip_stack[stack_key] = slip_dmg

    def effect_off(self, stack_key):
        if self.aff and not self.relief and ENEMY in self.generic_target:
            self._adv.afflictions[self.aff].off(stack_key)
        if self.slip is not None:
            try:
                self.slip_stack[stack_key].off()
                del self.slip_stack[stack_key]
            except KeyError:
                pass


class ActiveActconds(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self._by_source = defaultdict(dict)

    def add(self, actcond, actcond_source):
        abs_key = (actcond.id, actcond.target)
        if abs_key not in self:
            self[abs_key] = actcond
        name, aseq = actcond_source
        self._by_source[name][aseq] = actcond

    def check(self, name, aseq=None):
        if aseq is not None:
            try:
                return self._by_source[name][aseq].get()
            except KeyError:
                pass
        else:
            return any((actcond.get() for actcond in self._by_source[name].values()))
