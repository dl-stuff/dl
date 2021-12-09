from collections import UserDict, UserList, defaultdict
from functools import reduce
import operator

from conf import GENERIC_TARGET, SELF, TEAM, ENEMY, AFFLICT_LIST, AFFRES_PROFILES

from core.timeline import Timer, Listener, now
from core.log import log
from core.acl import allow_acl


### modifiers


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
        self.buff_capped = order == "buff"
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
        return "<{} {} {} {}>".format(
            self.target,
            self.mod_type,
            self.mod_order,
            self.get(),
        )


class KillerModifier(Modifier):
    def __init__(self, value, killer_states, order="hit", get=None, target="MYSELF"):
        if "afflicted" in killer_states:
            self.killer_states = AFFLICT_LIST
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
                self.MODS[generic_target][kmtype][self.mod_order].append(self)

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
        self.tolerance = tolerance
        self.get_override = None
        self.reset(0.0)

    def reset(self, resist):
        self.resist = resist
        self._res_states = self._init_state()
        self._res_states[self.resist] = 1.0
        self._stacks = {}
        self._get = 0

    def get(self):
        return self.get_override or self._get

    def update(self):
        self._get = 1.0 - reduce(operator.mul, self._stacks.values(), 1.0)

    def _init_state(self):
        return defaultdict(float)

    def edge_mod(self):
        return Modifier.SELF.mod(self._edge_mtype, operator=operator.add, initial=0.0)

    def affres_mod(self):
        return Modifier.ENEMY.mod(self._affres_mtype, operator=operator.add, initial=0.0)

    def proc(self, rate, stack_key, speshul_sandy_sum=1.0):
        total_success_p = 0.0
        rate = rate + self.edge_mod()
        n_states = self._init_state()
        for res, state_p in self._res_states.items():
            res = max(0, res + self.affres_mod())
            if res >= rate or res >= 1:
                n_states[res] += state_p
            else:
                rate_after_res = min(1.0, rate - res) * speshul_sandy_sum
                success_p = state_p * rate_after_res
                fail_p = state_p * (1.0 - rate_after_res)
                total_success_p += success_p
                n_states[res + self.tolerance] += success_p
                if fail_p > 0:
                    n_states[res] += fail_p
        if total_success_p > AffEV.THRESHOLD:
            self._res_states = n_states
            self._stacks[stack_key] = 1 - total_success_p
            self.update()
            return total_success_p
        else:
            self._get = 0
            return 0.0

    def end(self, stack_key):
        del self._stacks[stack_key]
        self.update()


class AffEVCapped(AffEV):
    def __init__(self, allaff, aff, tolerance, group=None) -> None:
        self.group = group
        super().__init__(allaff, aff, tolerance)

    def proc(self, rate, stack_key, speshul_sandy_sum=1.0):
        if self.group:
            no_stack_p = 1.0
            for aff in self.group:
                no_stack_p *= 1.0 - self._allaff[aff].get()
        else:
            no_stack_p = 1.0 - self._allaff[self.aff].get()
        total_success_p = 0.0
        rate = rate + self.edge_mod()
        n_states = self._init_state()
        for res, state_p in self._res_states.items():
            res = max(0, res + self.affres_mod())
            if res >= rate or res >= 1:
                n_states[res] += state_p
            else:
                rate_after_res = min(1.0, rate - res) * no_stack_p * speshul_sandy_sum
                success_p = state_p * rate_after_res
                fail_p = state_p * (1.0 - rate_after_res)
                total_success_p += success_p
                n_states[res + self.tolerance] += success_p
                if fail_p > 0:
                    n_states[res] += fail_p
        if total_success_p > AffEV.THRESHOLD:
            self._res_states = n_states
            self._stacks[stack_key] = 1 - total_success_p
            self.update()
            return total_success_p
        else:
            return 0.0


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

    def proc(self, aff, rate, stack_key):
        return self[aff].proc(rate, stack_key)

    def end(self, aff, stack_key):
        return self[aff].end(stack_key)


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
        self.on(source, dtype, target, ev=ev)

    def on(self, source, dtype, target, ev=1):
        if not self.slip_timer.online:
            self.slip_timer.on()
        if self.func == "mod":
            value = self._adv.dmg_formula(source, self.value, dtype=dtype)
        elif self.func == "heal":
            value = self._adv.heal_formula(source, self.value)
        else:
            value = self.value
        self.slip_value = (source, target, value * ev)

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
                self._adv.add_hp(value, percent=self.is_percent)

    def get(self):
        return self.slip_value is not None


class ActCond:
    def __init__(self, adv, id, target, data):
        self._adv = adv
        self._id = id
        self.target = target
        self.generic_target = GENERIC_TARGET[self.target]

        self.hidden = bool(data.get("hide"))
        self.text = data.get("text")
        self.icon = data.get("icon")
        self.overwrite = data.get("overwrite")
        self.maxstack = data.get("maxstack")
        self._rate = data.get("rate", 1.0)
        self.coei = bool(data.get("coei"))
        self.debuff = bool(data.get("debuff"))
        self.unremovable = bool(data.get("unremovable"))
        if data.get("lost_on_drg"):
            self.l_drg = Listener("dragon", self.all_off)

        self.aff = data.get("aff")
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

        self.slip = data.get("slip")
        self.slip_stack = {}

        self.mod_list = []
        if mod_args := data.get("mods"):
            for mod in mod_args:
                value, mtype, morder = mod
                mod_name = "_".join((self._id, mtype, morder))
                self.mod_list.append(Modifier(mod_name, mtype, morder, value, self.get))

        self.buff_stack = {}

    def get(self):
        return self.stack

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

    def bufftime(self, source="s"):
        if source == "s":
            if self.debuff:
                return Modifier.SELF.mod("debufftime", operator=operator.add)
            else:
                return Modifier.SELF.mod("bufftime", operator=operator.add)
        else:
            if self.debuff:
                return 1.0
            else:
                return self._adv.sub_mod("bufftime", "ex")

    def l_on(self, e):
        return self.on(e.source, e.target)

    @allow_acl
    def check(self, source):
        if self._adv.nihilism and not (self.coei or self.debuff) and (SELF in self.generic_target or TEAM in self.generic_target):
            return False
        return True

    def on(self, source, dtype):
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
        if self.duration:
            duration = self.duration * self.bufftime(source)
            timer = Timer(self.l_off, duration)
            timer.stack_key = stack_key
        self.buff_stack[stack_key] = timer

        if not self.effect_on(source, dtype, stack_key):
            return False

        self.log("start", self.text, duration)

    def _off(self, stack_key):
        timer = self.buff_stack.pop(stack_key)
        if timer is not None:
            timer.off()
        self.effect_off(stack_key)

    def off(self):
        if self.buff_stack:
            stack_key = min(self.buff_stack.keys())
            self._off(stack_key)

        self.log("end", self.text, f"from {stack_key[0]:<8.3f}, {stack_key[1]}")

    def l_off(self, e):
        self._off(e.stack_key)

    def all_off(self, e):
        for stack_key, timer in self.buff_stack.items():
            if timer is not None:
                timer.off()
            self.effect_off(stack_key)
        self.buff_stack = {}

    def effect_on(self, source, dtype, stack_key):
        ev = 1
        if self.aff and not self.relief:
            self._adv.afflictions[self.aff].proc(self._rate, stack_key)
            ev = self._adv.afflictions[self.aff].get()
        if self.slip is not None:
            # TODO: EV maffs
            self.slip_stack[stack_key] = SlipDmg(self, self.slip, source, dtype, self.target, ev=ev)

    def effect_off(self, stack_key):
        if self.aff and not self.relief:

        if self.slip is not None:
            try:
                self.slip_stack[stack_key].off()
                del self.slip_stack[stack_key]
            except KeyError:
                pass
        # no real need to turn off modifiers
