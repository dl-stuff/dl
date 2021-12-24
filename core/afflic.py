from collections import defaultdict, namedtuple

from core.timeline import *
from core.log import *
from core.acl import allow_acl
import random

AFFLICTION_LIST = [
    "poison",
    "paralysis",
    "burn",
    "blind",
    "bog",
    "stun",
    "freeze",
    "sleep",
    "frostbite",
    "flashburn",
    "shadowblight",
    "stormlash",
    "scorchrend",
]


class Dot(object):
    """
    Damage over time; e.g. poison
    """

    def __init__(self, name, coef, duration, iv, dtype=None):
        self.name = name
        self.dtype = dtype
        self.active = 0
        self.coef = coef
        self.iv = iv  # Seconds between each damage tick
        self.duration = duration
        self.true_dmg_event = Event("true_dmg")
        self.true_dmg_event.dname = name
        self.true_dmg_event.dtype = dtype if dtype else name
        self.true_dmg_event.comment = ""
        self.tick_dmg = 0
        self.quickshot_event = Event("dmg_formula")
        self.tick_timer = Timer(self.tick_proc)
        self.dotend_timer = Timer(self.dot_end_proc)

    def dot_end_proc(self, t):
        log("dot", self.name, "end")
        self.active = 0
        self.tick_timer.off()
        self.cb_end()

    def cb_end(self):
        pass

    def tick_proc(self, t):
        if self.active == 0:
            return
        t.on(self.iv)
        self.true_dmg_event.count = self.tick_dmg
        self.true_dmg_event.on()

    # def __call__(self):
    #     return self.on()

    def get(self):
        return self.active

    def on(self):
        if self.active:
            log("dot", self.name, "failed")
            return 0
        self.active = 1
        self.tick_timer.on(self.iv)
        self.dotend_timer.on(self.duration)
        self.quickshot_event.dmg_coef = self.coef
        self.quickshot_event.dname = self.name
        self.quickshot_event.dtype = self.dtype if self.dtype else self.name
        self.quickshot_event.dot = True
        self.quickshot_event()
        self.tick_dmg = self.quickshot_event.dmg
        log("dot", self.name, "start", "%f/%d" % (self.iv, self.duration))
        return 1

    def off(self):
        self.tick_timer.off()
        self.dotend_timer.off()
        log("dot", self.name, "end by other reason")


class AfflicBase:
    def __init__(self, name, duration, tolerance):
        self.name = name
        self._resist = 0
        self._rate = 1
        self.tolerance = tolerance
        self.res_modifier = 0
        self.duration = duration
        self.default_duration = duration
        self.states = None
        self._get = 0.0

        self.c_uptime = (0, 0)
        self.last_afflict = 0
        self.attempts = 0

        self.event = Event(self.name)

        self.get_override = 0
        self.aff_edge_mods = []
        self.aff_time_mods = []

    @property
    def edge(self):
        return sum((m.get() for m in self.aff_edge_mods))

    @property
    def time(self):
        return 1 + sum((m.get() for m in self.aff_time_mods))

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, rate):
        if rate > 2:
            self._rate = float(rate) / 100.0
        else:
            self._rate = rate

    @property
    def resist(self):
        return self._resist

    @resist.setter
    def resist(self, resist):
        if resist > 1:
            self._resist = float(resist) / 100.0
        else:
            self._resist = resist

    def get(self):
        if self.resist >= 3:
            return 0
        else:
            return self.get_override or self._get

    def set_res_mod(self, delta):
        self.res_modifier = max(min(self.res_modifier + delta, 0), -1)

    def uptime(self):
        next_r = self.get()
        next_t = now()
        if next_r == 0:
            self.last_afflict = next_t
        prev_r, prev_t = self.c_uptime
        rate = prev_r + next_r * (next_t - prev_t)
        self.c_uptime = (rate, next_t)
        if next_t > 0 and rate > 0:
            log(
                "{}_uptime".format(self.name),
                "{:.2f}/{:.2f}".format(rate, next_t),
                "{:.2%}".format(rate / next_t),
            )
        # if next_t > 0 and rate > 0:
        #     log('uptime', self.name, rate / next_t)


class AfflicUncapped(AfflicBase):
    def __init__(self, name=None, duration=12, tolerance=0.05):
        super().__init__(name, duration, tolerance)
        self.stacks = defaultdict(lambda: 0)

    def update(self):
        self.uptime()
        nostack_p = 1.0
        for stack_p, count in self.stacks.items():
            nostack_p *= (1.0 - stack_p) ** count
        self._get = 1.0 - nostack_p

    def stack_end(self, e):
        self.stacks[e.total_success_p] -= 1
        if self.stacks[e.total_success_p] == 0:
            del self.stacks[e.total_success_p]
        self.update()
        log("affliction", self.name, self._get)

    def on(self, speshul_sandy_sum=1.0):
        self.attempts += 1
        if self.states is None:
            self.states = defaultdict(lambda: 0.0)
            self.states[self.resist] = 1.0
        states = defaultdict(lambda: 0.0)
        total_success_p = 0.0
        for res, state_p in self.states.items():
            res = max(0, res + self.res_modifier)
            if res >= self.rate or res >= 1:
                states[res] += state_p
            else:
                rate_after_res = min(1.0, self.rate - res) * speshul_sandy_sum
                success_p = state_p * rate_after_res
                fail_p = state_p * (1.0 - rate_after_res)
                total_success_p += success_p
                states[res + self.tolerance] += success_p
                if fail_p > 0:
                    states[res] += fail_p
        if total_success_p > 0:
            self.states = states
            self.stacks[total_success_p] += 1
            t = Timer(self.stack_end, self.duration)
            t.total_success_p = total_success_p
            t.on()
            self.update()
        log("affliction", self.name, self._get)
        self.event.rate = total_success_p
        self.event()

        return total_success_p


class AfflicCapped(AfflicBase):
    State = namedtuple("State", ("timers", "resist"))

    def __init__(self, name=None, duration=12, tolerance=0.2):
        super().__init__(name, duration, tolerance)
        self.stack_cap = 1

    def update(self):
        self.uptime()
        total_p = 0.0
        states = defaultdict(lambda: 0.0)
        for state, state_p in self.states.items():
            reduced_state = self.State(frozenset([t for t in state.timers if t.timing > now()]), state.resist)
            states[reduced_state] += state_p
            if reduced_state.timers:
                total_p += state_p
        self.states = states
        self._get = total_p
        return total_p

    def stack_end(self, t):
        self.update()
        log("affliction", self.name, self.get())
        if self.get() != self.start_rate:
            log("cc", self.name, self.get() or "end")

    def on(self):
        self.attempts += 1
        timer = Timer(self.stack_end, self.duration)
        if self.states is None:
            self.states = defaultdict(lambda: 0.0)
            self.states[self.State(frozenset(), self.resist)] = 1.0
        states = defaultdict(lambda: 0.0)
        total_p = 0.0
        for start_state, start_state_p in self.states.items():
            res = start_state.resist - self.res_modifier
            if res >= self.rate or res >= 1 or len(start_state.timers) >= self.stack_cap:
                states[start_state] += start_state_p
            else:
                rate_after_res = min(1, self.rate - res)
                succeed_timers = frozenset(list(start_state.timers) + [timer])
                state_on_succeed = self.State(succeed_timers, min(1.0, res + self.tolerance))
                overall_succeed_p = start_state_p * rate_after_res
                overall_fail_p = start_state_p * (1.0 - rate_after_res)
                total_p += overall_succeed_p
                states[state_on_succeed] += overall_succeed_p
                if overall_fail_p > 0:
                    states[start_state] += overall_fail_p
        if total_p > 0:
            timer.on()
            self.states = states
            self.update()
        self.event.rate = total_p
        self.event()
        log("affliction", self.name, self.get())
        self.start_rate = round(self.get(), 3)
        log("cc", self.name, self.start_rate or "fail")
        return total_p


class Afflic_dot(AfflicUncapped):
    def __init__(self, name=None, duration=12, iv=3.99, tolerance=0.05):
        super().__init__(name, duration=duration, tolerance=tolerance)
        self.coef = 0.97
        self.default_iv = iv
        self.iv = iv
        self.dot = None

    def on(self, name, rate, coef, duration=None, iv=None, dtype=None, speshul_sandy_sum=1.0):
        self.event.source = name
        self.rate = rate + self.edge
        self.coef = coef
        if dtype is None and name[0] == "s":
            self.dtype = "s"
        else:
            self.dtype = dtype
        self.duration = (duration or self.default_duration) * self.time
        self.iv = iv or self.default_iv
        self.dot = Dot(f"o_{name}_{self.name}", coef, self.duration, self.iv, self.dtype)
        self.dot.on()
        r = super().on(speshul_sandy_sum=speshul_sandy_sum)
        self.dot.tick_dmg *= r
        return r

    def timeleft(self):
        if self.dot:
            return self.dot.dotend_timer.timing - now()
        else:
            return 0


class Afflic_cc(AfflicCapped):
    def __init__(self, name=None, duration=6.5, tolerance=0.2):
        super().__init__(name, duration, tolerance=tolerance)
        self.stack_cap = 1

    def on(self, name, rate, duration=None, min_duration=None, dtype=None):
        self.event.source = name
        self.rate = rate + self.edge
        self.duration = (duration or self.default_duration) * self.time
        if min_duration:
            self.duration = (self.duration + min_duration) / 2
        return super().on()

    def cb_end(self):
        pass


class Afflic_scc(AfflicCapped):
    def __init__(self, name=None, duration=8, tolerance=0.1):
        super().__init__(name, duration, tolerance)
        self.stack_cap = 1

    def on(self, name, rate, duration=None, dtype=None):
        self.event.source = name
        self.rate = rate + self.edge
        self.duration = duration or self.default_duration
        return super().on()

    def cb_end(self):
        pass


class Afflic_bog(Afflic_scc):
    def __init__(self, name=None, duration=8, tolerance=0.2):
        super().__init__(name, duration, tolerance)

    def on(self, name, rate, duration=None, dtype=None):
        self.event.source = name
        p = super().on(name, rate, duration)
        if p:
            # from core.advbase import Debuff
            # Debuff('{}_bog'.format(name),-0.5*p,self.duration,1,'att','bog').on()
            from core.advbase import Selfbuff

            bog = Selfbuff("{}_bog".format(name), 0.5 * p, self.duration, "att", "bog").no_bufftime()
            bog.bufftype = "bog"
            bog.on()
        return p


class Afflics(object):
    RESIST_PROFILES = {
        None: {
            "poison": 0,
            "burn": 0,
            "paralysis": 0,
            "frostbite": 0,
            "flashburn": 0,
            "shadowblight": 0,
            "stormlash": 0,
            "scorchrend": 0,
            "blind": 99,
            "bog": 99,
            "freeze": 99,
            "stun": 99,
            "sleep": 99,
        },
        "immune": {
            "poison": 999,
            "burn": 999,
            "paralysis": 999,
            "frostbite": 999,
            "flashburn": 999,
            "shadowblight": 999,
            "stormlash": 999,
            "scorchrend": 999,
            "blind": 999,
            "bog": 999,
            "freeze": 999,
            "stun": 999,
            "sleep": 999,
        },
        ("flame", False): {  # Legend Volk
            "poison": 0,
            "burn": 0,
            "freeze": 100,
            "paralysis": 100,
            "blind": 99,
            "stun": 99,
            "bog": 99,
            "sleep": 99,
            "frostbite": 0,
            "flashburn": 0,
            "stormlash": 0,
            "shadowblight": 0,
            "scorchrend": 0,
        },
        ("flame", True): {  # Master Jaldabaoth (wind side)
            "poison": 100,
            "burn": 60,
            "freeze": 100,
            "paralysis": 100,
            "blind": 100,
            "stun": 100,
            "bog": 100,
            "sleep": 100,
            "frostbite": 100,
            "flashburn": 100,
            "stormlash": 100,
            "shadowblight": 100,
            "scorchrend": 0,
        },
        ("shadow", False): {  # Legend Kai Yan
            "poison": 0,
            "burn": 0,
            "freeze": 100,
            "paralysis": 100,
            "blind": 100,
            "stun": 99,
            "bog": 99,
            "sleep": 99,
            "frostbite": 0,
            "flashburn": 0,
            "stormlash": 0,
            "shadowblight": 0,
            "scorchrend": 0,
        },
        ("shadow", True): {  # Master Asura (light Side)
            "poison": 80,
            "burn": 100,
            "freeze": 100,
            "paralysis": 100,
            "blind": 100,
            "stun": 100,
            "bog": 100,
            "sleep": 100,
            "frostbite": 100,
            "flashburn": 100,
            "stormlash": 100,
            "shadowblight": 80,
            "scorchrend": 100,
        },
        ("wind", False): {  # Legend Ciella
            "poison": 85,
            "burn": 100,
            "freeze": 100,
            "paralysis": 100,
            "blind": 100,
            "stun": 100,
            "bog": 100,
            "sleep": 100,
            "frostbite": 100,
            "flashburn": 100,
            "stormlash": 20,
            "shadowblight": 100,
            "scorchrend": 100,
        },
        ("wind", True): {  # Master Iblis (water side)
            "poison": 0,
            "burn": 100,
            "freeze": 100,
            "paralysis": 100,
            "blind": 100,
            "stun": 100,
            "bog": 100,
            "sleep": 100,
            "frostbite": 100,
            "flashburn": 100,
            "stormlash": 0,
            "shadowblight": 100,
            "scorchrend": 100,
        },
        ("water", False): {  # Legend Ayaha & Otoha
            "poison": 100,
            "burn": 0,
            "freeze": 100,
            "paralysis": 100,
            "blind": 100,
            "stun": 100,
            "bog": 100,
            "sleep": 100,
            "frostbite": 0,
            "flashburn": 100,
            "stormlash": 100,
            "shadowblight": 100,
            "scorchrend": 100,
        },
        ("water", True): {  # Master Surtr (flame side)
            "poison": 85,
            "burn": 85,
            "freeze": 100,
            "paralysis": 85,
            "blind": 100,
            "stun": 100,
            "bog": 100,
            "sleep": 100,
            "frostbite": 0,
            "flashburn": 85,
            "stormlash": 85,
            "shadowblight": 0,
            "scorchrend": 85,
        },
        ("light", False): {  # Legend Tartarus
            "poison": 200,
            "burn": 200,
            "freeze": 200,
            "paralysis": 85,
            "blind": 200,
            "stun": 200,
            "bog": 200,
            "sleep": 200,
            "frostbite": 200,
            "flashburn": 20,
            "stormlash": 200,
            "shadowblight": 200,
            "scorchrend": 200,
        },
        ("light", True): {  # Master Lilith (shadow side)
            "poison": 100,
            "burn": 100,
            "freeze": 100,
            "paralysis": 30,
            "blind": 100,
            "stun": 100,
            "bog": 100,
            "sleep": 100,
            "frostbite": 100,
            "flashburn": 30,
            "stormlash": 100,
            "shadowblight": 100,
            "scorchrend": 100,
        },
    }

    def __init__(self):
        self.poison = Afflic_dot("poison", duration=15, iv=2.9)
        self.burn = Afflic_dot("burn", duration=12, iv=3.9)
        self.paralysis = Afflic_dot("paralysis", duration=13, iv=3.9)
        self.frostbite = Afflic_dot("frostbite", duration=21, iv=2.9)
        self.flashburn = Afflic_dot("flashburn", duration=21, iv=2.9)
        self.shadowblight = Afflic_dot("shadowblight", duration=21, iv=2.9)
        self.stormlash = Afflic_dot("stormlash", duration=21, iv=2.9)
        self.scorchrend = Afflic_dot("scorchrend", duration=21, iv=2.9)

        self.blind = Afflic_scc("blind", duration=8)
        self.bog = Afflic_bog("bog", duration=8)
        self.freeze = Afflic_cc("freeze", duration=4.5)
        self.stun = Afflic_cc("stun", duration=6.5)
        self.sleep = Afflic_cc("sleep", duration=6.5)

        self.set_resist()

    def set_resist(self, profile=None):
        for aff, resist in Afflics.RESIST_PROFILES[profile].items():
            getattr(self, aff).resist = resist

    def get_resist(self):
        return {aff: int(getattr(self, aff).resist * 100) for aff in AFFLICTION_LIST}

    def get_uptimes(self):
        uptimes = {}
        for atype in AFFLICTION_LIST:
            aff = self.__dict__[atype]
            aff.uptime()
            rate, t = aff.c_uptime
            if rate > 0:
                uptimes[atype] = rate / t
        return uptimes.items()

    def get_attempts(self):
        attempts = {}
        for atype in AFFLICTION_LIST:
            aff = self.__dict__[atype]
            if aff.attempts > 0:
                attempts[atype] = aff.attempts
        return attempts
