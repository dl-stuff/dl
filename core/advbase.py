import enum
import operator
import sys
import random
from functools import reduce
from itertools import product, chain
from collections import OrderedDict, Counter

# from core import *
from core.config import Conf
from core.timeline import *
from core.log import *
from core.afflic import *
from core.modifier import *
from core.dummy import Dummy, dummy_function
from core.condition import Condition
from core.slots import DragonBase, Slots
import core.acl
from core.acl import CONTINUE, allow_acl
import conf as globalconf
from conf.equip import get_equip_manager
from ctypes import c_float


def float_ceil(value, percent):
    c_float_value = c_float(c_float(percent).value * value).value
    int_value = int(c_float_value)
    return int_value if int_value == c_float_value else int_value + 1


class Skill(object):
    _static = Static({"s_prev": "<nop>", "first_x_after_s": 0, "silence": 0, "current_s": {}})
    charged = 0
    sp = 0
    silence_duration = 1.9
    name = "_Skill"

    def __init__(self, name=None, acts=None):
        self.charged = 0
        self.name = name

        self.act_dict = acts or {}
        self.act_base = None

        self._static.silence = 0
        self.silence_end_timer = Timer(self.cb_silence_end)
        self.silence_end_event = Event("silence_end")
        self.skill_charged = Event(f"{self.name}_charged")

        self.enable_phase_up = False
        self.maxcharge = 1
        self.autocharge_sp = 0

        self.p_max = 0
        self.dragonbattle_skill = False
        self.overcharge_sp = None

    def add_action(self, group, act, phase_up=True):
        act.cast = self.cast
        self.act_dict[group] = act
        if act.group == globalconf.DEFAULT:
            self.act_base = act
        if isinstance(act.group, int):
            # might need to distinguish which phase can up eventually
            self.enable_phase_up = self.enable_phase_up or phase_up
        elif act.group.startswith("overcharge"):
            if self.overcharge_sp is None:
                self.overcharge_sp = [(globalconf.DEFAULT, self.act_dict[globalconf.DEFAULT].conf.sp)]
            self.overcharge_sp.append((act.group, act.conf.sp))
        if act.conf["sp_regen"] and not self.autocharge_sp:
            self.autocharge_init(act.conf["sp_regen"]).on()

    def set_enabled(self, enabled):
        for ac in self.act_dict.values():
            ac.enabled = enabled

    def reset_uses(self):
        if self.dragonbattle_skill:
            return
        for ac in self.act_dict.values():
            ac.uses = ac.conf["uses"] or -1
        self.charged = 0
        if self.overcharge_sp is not None:
            self._static.current_s[self.name] = globalconf.DEFAULT

    @property
    def phase(self):
        return self._static.current_s[self.name]

    @property
    def ac(self):
        try:
            return self.act_dict[self._static.current_s[self.name]]
        except KeyError:
            return self.act_base

    @property
    def sp(self):
        if self.overcharge_sp:
            return sum((sp for _, sp in self.overcharge_sp))
        return self.real_sp

    @property
    def real_sp(self):
        if self.dragonbattle_skill:
            return self.ac.conf["sp_db"] or self.ac.conf.sp
        return self.ac.conf.sp

    @property
    def count(self):
        return self.charged // self.sp

    @property
    def overcharge(self):
        return self.ac.overcharge

    @property
    def sp_str(self):
        if self.overcharge_sp is not None:
            # oc_summed = "+".join((str(sp) for _, sp in self.overcharge_sp))
            oc_summed = self.sp
            if self._static.current_s[self.name] == globalconf.DEFAULT:
                return f"{self.charged}/{oc_summed}"
            return f"{self.charged}/{oc_summed} [{self._static.current_s[self.name]}]"
        else:
            if self.maxcharge > 1:
                return f"{self.charged}/{self.sp} [{self.count}]"
            return f"{self.charged}/{self.sp}"

    @property
    def owner(self):
        return self.act_base.conf["owner"] or None

    def phase_up(self):
        if self.p_max:
            cur_s = self._static.current_s[self.name]
            cur_s = (cur_s + 1) % self.p_max
            self._static.current_s[self.name] = cur_s

    def __call__(self, *args):
        return self.precast()

    def precast(self, t=None):
        if not self.check():
            return False
        result = self.ac.tap(defer=False)
        if isinstance(result, float):
            Timer(self.precast).on(result)
            return True
        elif not result:
            return False
        self.enable_phase_up and self.phase_up()
        return self.cast()

    def charge(self, sp):
        if not self.ac.enabled:
            return
        self.charged = max(min(self.sp * self.maxcharge, self.charged + sp), 0)
        if self.charged >= self.sp:
            self.skill_charged()
        if self.overcharge_sp is not None:
            oc_threshold = 0
            for oc_group, oc_sp in self.overcharge_sp:
                oc_threshold += oc_sp
                if self.charged >= oc_threshold:
                    self._static.current_s[self.name] = oc_group

    def cb_silence_end(self, e):
        if loglevel >= 2:
            log("silence", "end")
        self._static.silence = 0
        self.silence_end_event()

    @allow_acl
    def check(self):
        if self._static.silence or not self.ac or not self.ac.enabled:
            return False
        if self.overcharge_sp:
            valid_sp = self.real_sp
            valid_uses = self.act_dict[globalconf.DEFAULT].uses
        else:
            valid_sp = self.sp
            valid_uses = self.ac.uses
        if valid_sp == 0:
            return False
        if self.charged < valid_sp or valid_uses == 0:
            return False
        return True

    def cast(self):
        self.charged -= self.sp
        if self.overcharge_sp is not None:
            self._static.current_s[self.name] = globalconf.DEFAULT
        self._static.s_prev = self.name
        # Even if animation is shorter than 1.9, you can't cast next skill before 1.9
        self.silence_end_timer.on(self.silence_duration)
        self._static.silence = 1
        if self.ac.uses > 0:
            self.ac.uses -= 1
        if loglevel >= 2:
            log("silence", "start")
        return 1

    def autocharge(self, t):
        if self.charged < self.sp * self.maxcharge:
            self.charge(self.autocharge_sp)
            log("sp", self.name + "_autocharge", int(self.autocharge_sp))

    def autocharge_init(self, sp, iv=1):
        if callable(sp):
            self.autocharge_timer = Timer(sp, iv, 1)
        else:
            if sp < 1:
                sp = int(sp * self.sp)
            self.autocharge_sp = sp
            self.autocharge_timer = Timer(self.autocharge, iv, 1)
        return self.autocharge_timer


class ReservoirSkill(Skill):
    def __init__(self, name=None, acts=None, true_sp=1, maxcharge=1):
        super().__init__(name=name, acts=acts)
        self.maxcharge = maxcharge
        self.true_sp = true_sp

    def add_action(self, group, act, phase_up=True):
        super().add_action((act.base, group), act, phase_up=phase_up)

    @property
    def ac(self):
        try:
            return self.act_dict[(self.name, self._static.current_s[self.name])]
        except KeyError:
            return self.act_base

    @property
    def sp(self):
        return self.true_sp

    def __call__(self, call=1):
        self.name = f"s{call}"
        return super().__call__()


class ReservoirChainSkill(Skill):
    def __init__(self, name=None, altchain=None, sp=1129, maxcharge=3):
        super().__init__(name)
        self.chain_timer = Timer(self.chain_off)
        self.chain_status = 0
        self.altchain = altchain or "default"
        self.maxcharge = maxcharge
        self._sp = sp

    def add_action(self, group, act, phase_up=True):
        super().add_action((act.base, group), act, phase_up=phase_up)

    @property
    def ac(self):
        return self.act_dict[(self.name, self._static.current_s[self.name])]

    def chain_on(self, skill, timeout=3):
        timeout += self.ac.getrecovery()
        self.chain_status = skill
        self.chain_timer.on(timeout)
        log("skill_chain", f"s{skill}", timeout)
        self._static.current_s[f"s{skill}"] = f"chain"
        self._static.current_s[f"s{3-skill}"] = self.altchain

    def chain_off(self, t=None, reason="timeout"):
        log("skill_chain", "chain off", reason)
        self.chain_status = 0
        self._static.current_s["s1"] = globalconf.DEFAULT
        self._static.current_s["s2"] = globalconf.DEFAULT

    @property
    def sp(self):
        return self._sp

    def __call__(self, call=1):
        self.name = f"s{call}"
        casted = super().__call__()
        if casted:
            if self.count == 0 and self.chain_timer.online:
                self.chain_timer.off()
                self.chain_off(reason="reservoir below 1")
            else:
                self.chain_on(call)
        return casted


class Nop(object):
    name = "nop"
    index = 0
    status = -2
    idle = 1
    has_delayed = 0


class Action(object):
    _static = Static(
        {
            "prev": 0,
            "doing": 0,
            "spd_func": 0,
            "c_spd_func": 0,
            "f_spd_func": 0,
            "actmod_off": 0,
            "pin": "idle",
        }
    )
    OFF = -2
    STARTUP = -1
    DOING = 0
    RECOVERY = 1

    name = "_Action"
    index = 0
    recover_start = 0
    startup_start = 0
    status = -2
    idle = 0

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
        if not self._static.f_spd_func:
            self._static.f_spd_func = self.nospeed
        if not self._static.doing:
            self._static.doing = self.nop
        if not self._static.prev:
            self._static.prev = self.nop

        self.startup_timer = Timer(self._cb_acting)
        self.recovery_timer = Timer(self._cb_act_end)
        self.start_event = Event(f"{self.name}_start")
        self.act_event = Event(self.name)
        self.idle_event = Event("idle")
        self.end_event = Event(f"{self.name}_end")
        self.end_event.act = self.act_event
        self.defer_event = Event("defer")

        self.general_end_event = Event("act_end")

        self.enabled = True
        self.delayed = set()
        # ?????
        # self.rt_name = self.name
        # self.tap, self.o_tap = self.rt_tap, self.tap
        self.explicit_x = False

    def __call__(self):
        return self.tap()

    def getdoing(self):
        return self._static.doing

    def _setdoing(self):
        self.explicit_x = False
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

    def can_follow(self, name, atype, conf, elapsed):
        if atype == "s" and self.atype != "s":
            return 0.0
        timing = conf[name]
        if timing is None:
            timing = conf[atype]
        if timing is None:
            if atype == "fs" and self.atype == "x":
                timing = 0.66666 - self._startup
            elif name != self.name:
                timing = conf["any"]
        if timing is None:
            return None
        timing -= 0.0001
        # log("canfollow", self.name, name, atype, str(conf))
        return max(0, round(timing / self.speed() - elapsed, 5))

    def can_interrupt(self, name, atype):
        return self.can_follow(name, atype, self.conf.interrupt, self.startup_timer.elapsed())

    def can_cancel(self, name, atype):
        return self.can_follow(name, atype, self.conf.cancel, self.recovery_timer.elapsed())

    def has_follow(self, name, atype):
        return bool(self.conf.interrupt[name] is not None or self.conf.interrupt[atype] is not None or self.conf.cancel[name] is not None or self.conf.cancel[atype] is not None)

    @property
    def _startup(self):
        return self.conf.startup

    @property
    def _recovery(self):
        return self.conf.recovery

    def getrecovery(self):
        # Lathna/Ramona spaget, fixed now
        # if "recovery_nospd" in self.conf:
        #     return self._recovery / self.speed() + self.conf["recovery_nospd"]
        return self._recovery / self.speed()

    def getstartup(self):
        return self._startup / self.speed()

    def nospeed(self):
        return 1

    def speed(self):
        return self._static.spd_func()

    def _cb_acting(self, e):
        if self.getdoing() == self:
            self.status = Action.DOING
            self._act()
            self.status = Action.RECOVERY
            self.recover_start = now()
            self.recovery_timer.on(self.getrecovery())

    def _cb_act_end(self, e):
        self.explicit_x = False
        if self.getdoing() == self:
            if loglevel >= 2:
                log("ac_end", self.name)
            self.status = Action.OFF
            self._setprev()  # turn self from doing to prev
            self._static.doing = self.nop
            self.idle_event()
            self.general_end_event()
            self.end_event()

    def _act(self):
        if loglevel >= 2:
            log("act", self.name)
        self.act_event()

    def turn_off(self):
        self.startup_timer.off()
        self.recovery_timer.off()
        self.general_end_event()
        self.end_event()

    def add_delayed(self, mt):
        self.delayed.add(mt)

    def remove_delayed(self, mt):
        self.delayed.discard(mt)

    def clear_delayed(self):
        count = 0
        for mt in self.delayed:
            if mt.online:
                count += 1
            if mt.actmod:
                self._static.actmod_off(mt)
            mt.off()
        self.delayed = set()
        return count

    @property
    def has_delayed(self):
        return len([mt for mt in self.delayed if mt.online and mt.timing > now()])

    @property
    def max_delayed(self):
        try:
            return max([mt.timing - now() for mt in self.delayed if mt.online and mt.timing > now()])
        except ValueError:
            return 0

    def defer_tap(self, t):
        self.defer_event.pin = t.pin
        self.defer_event()

    def tap(self, t=None, defer=True):
        if not self.enabled:
            return False
        doing = self._static.doing

        # if doing.idle:
        #     log("tap", self.name, self.atype, f"idle {doing.status}")
        # else:
        #     log("tap", self.name, self.atype, f"doing {doing.name}:{doing.status}")

        # if doing == self:  # self is doing
        # return False

        # if doing.idle # idle
        #    pass
        if not doing.idle:  # doing != self
            if doing.status == Action.STARTUP:  # try to interrupt an action
                timing = doing.can_interrupt(self.name, self.atype)
                if timing is not None:  # can interrupt action
                    if timing > 0:
                        if defer:
                            dt = Timer(self.defer_tap)
                            dt.pin = self._static.pin
                            dt.on(timing)
                            return False
                        return timing
                    doing.turn_off()
                    logargs = ["interrupt", doing.name, f"by {self.name}"]
                    delta = now() - doing.startup_start
                    logargs.append(f"after {delta:.2f}s")
                    log(*logargs)
                else:
                    return False
            elif doing.status == Action.RECOVERY:  # try to cancel an action
                timing = doing.can_cancel(self.name, self.atype)
                if timing is not None:  # can cancel action
                    if timing > 0:
                        if defer:
                            dt = Timer(self.defer_tap)
                            dt.pin = self._static.pin
                            dt.on(timing)
                            return False
                        return timing
                    doing.turn_off()
                    count = doing.clear_delayed()
                    delta = now() - doing.recover_start
                    logargs = ["cancel", doing.name, f"by {self.name}"]
                    logargs.append(f"after {delta:.2f}s")
                    if count > 0:
                        logargs.append(f'lost {count} hit{"s" if count > 1 else ""}')
                    log(*logargs)
                else:
                    return False
            elif doing.status == Action.DOING:
                raise Exception(f"Illegal action {doing} -> {self}")
            self._setprev()
        self.delayed = set()
        self.status = Action.STARTUP
        self.startup_start = now()
        self.startup_timer.on(self.getstartup())
        self._setdoing()
        self.start_event()
        if now() <= 3:
            log("debug", "tap", self.name, "startup", self.getstartup())
        return True


class Repeat(Action):
    def __init__(self, conf, parent):
        super().__init__(f"{parent.name}-repeat", conf)
        self.parent = parent
        self.act_event = Event("repeat")
        self.act_event.name = self.parent.act_event.name
        self.act_event.base = self.parent.act_event.base
        self.act_event.group = self.parent.act_event.group
        self.act_event.dtype = "fs"
        self.act_event.end = False
        self.end_repeat_event = Event("repeat")
        self.end_repeat_event.name = self.parent.act_event.name
        self.end_repeat_event.base = self.parent.act_event.base
        self.end_repeat_event.group = self.parent.act_event.group
        self.end_repeat_event.dtype = "fs"
        self.end_repeat_event.end = True
        self.count = 0
        self.extra_charge = None
        self.count0_time = None

    def can_ic(self, name, atype, can):
        if name == self.parent.name and atype == self.parent.atype:
            return None
        result = can(name, atype)
        if result is not None:
            self.parent.end_event.on()
            self.end_repeat_event.on()
        return result

    def can_interrupt(self, name, atype):
        return self.can_ic(name, atype, self.parent.can_interrupt)

    def can_cancel(self, name, atype):
        if self.explicit_x:
            self.parent.end_event.on()
            self.end_repeat_event.on()
            return 0.0
        return self.can_ic(name, atype, self.parent.can_cancel)

    def __call__(self):
        self.count = 0
        self.count0_time = now()
        self.tap()

    def _cb_act_end(self, e):
        self.tap()

    def tap(self, t=None):
        self.count += 1
        self._static.doing = self.nop
        # if self.extra_charge:
        #     log("extra_charge", now() - self.count0_time, self.extra_charge)
        if (not self.parent.enabled) or (self.extra_charge and now() - self.count0_time > self.extra_charge):
            self.extra_charge = None
            self.parent.end_event.on()
            self.end_repeat_event.on()
            self.idle_event()
            return False
        else:
            return super().tap()


class X(Action):
    INDEX_PATTERN = re.compile(r"d?x(\d)+")

    def __init__(self, name, conf, act=None):
        parts = name.split("_")
        index = int(X.INDEX_PATTERN.match(parts[0]).group(1))
        super().__init__((name, index), conf, act)
        self.base = parts[0]
        if name[0] == "d":
            self.group = globalconf.DRG
        elif len(parts) == 1:
            self.group = globalconf.DEFAULT
        else:
            self.group = parts[1]
        self.atype = "x"

        self.act_event = Event("x")
        self.act_event.name = self.name
        self.act_event.base = self.base
        self.act_event.group = self.group
        self.act_event.dtype = "x"
        self.act_event.index = self.index

        self.end_event = Event("x_end")
        self.end_event.act = self.act_event

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
    LEVEL_PATTERN = re.compile(r"(d?fs)(\d)+")

    def __init__(self, name, conf, act=None):
        super().__init__(name, conf, act)
        parts = name.split("_")
        self.base = parts[0]
        if name[0] == "d":
            self.group = globalconf.DRG
        elif len(parts) == 1:
            self.group = globalconf.DEFAULT
        else:
            self.group = parts[1]
        self.atype = "fs"
        self.level = 0
        if len(parts[0]) > 2 and (match := Fs.LEVEL_PATTERN.match(parts[0])):
            self.base = match.group(1)
            self.level = int(match.group(2))

        self.act_event = Event("fs")
        self.act_event.name = self.name
        self.act_event.base = self.base
        self.act_event.group = self.group
        self.act_event.dtype = self.base
        self.act_event.level = self.level
        self.start_event = Event(f"{self.base}_start")
        self.start_event.act = self.act_event
        self.end_event = Event(f"{self.base}_end")
        self.end_event.act = self.act_event
        self.charged_event = Event(f"{self.base}_charged")
        self.charged_event.act = self.act_event

        self.charged_timer = Timer(self._charged)

        self.act_repeat = None
        if self.conf["repeat"]:
            self.act_repeat = Repeat(self.conf.repeat, self)

        self.extra_charge = 0
        self.last_buffer = 0

    def _charged(self, _):
        self.extra_charge = 0
        self.charged_event()

    def _cb_act_end(self, e):
        if self.act_repeat:
            self._setprev()
            self.act_repeat()
        else:
            super()._cb_act_end(e)
        self.last_buffer = 0

    def turn_off(self):
        self.charged_timer.off()
        self.extra_charge = 0
        self.charged_event()
        return super().turn_off()

    @property
    def _charge(self):
        if self.act_repeat is not None and self.act_repeat.extra_charge is None:
            self.act_repeat.extra_charge = self.extra_charge or None
            self.extra_charge = 0
            return self.conf.charge
        return self.conf.charge

    @property
    def _buffer(self):
        # human input buffer time
        return self.conf.get("buffer", 0.46667)

    def set_enabled(self, enabled):
        self.enabled = enabled

    def charge_speed(self):
        if self.base.startswith("dfs"):
            return 1.0
        return self._static.c_spd_func()

    def speed(self):
        if self.base.startswith("dfs"):
            return super().speed()
        return self._static.f_spd_func() - 1 + super().speed()

    def getstartup(self, include_buffer=True):
        startup = self._startup / self.speed()
        return self.getcharge(include_buffer=include_buffer) + startup

    def getcharge(self, include_buffer=True):
        buffer = 0
        if include_buffer:
            buffer = self._buffer
            prev = self.getdoing()
            if prev is self.nop:
                prev = self.getprev()
            if isinstance(prev, (X, Dodge, S)):
                bufferable = prev.startup_timer.elapsed() + prev.recovery_timer.elapsed()
                buffer = max(0, self._buffer - bufferable)
                # log("input_buffer", prev.name, buffer, bufferable)
            self.last_buffer = buffer
        charge = self._charge / self.charge_speed() + self.extra_charge
        return buffer + charge

    def __call__(self):
        charge = self.getcharge()
        if super().__call__():
            log("charge", self.name, charge, self.extra_charge)
            self.charged_timer.on(charge)
            return True
        return False


class S(Action):
    TAP_DELAY = 0.1

    def __init__(self, name, conf, act=None):
        super().__init__(name, conf, act)
        self.atype = "s"

        parts = name.split("_")
        self.base = parts[0]
        self.group = globalconf.DEFAULT
        self.phase = 0
        self.overcharge = 0
        if len(parts) >= 2:
            self.group = parts[1]
            if self.group.startswith("phase"):
                self.phase = int(self.group[5:])
            if self.group.startswith("overcharge"):
                self.overcharge = int(self.group[10:])

        self.act_event = Event("s")
        self.act_event.name = self.name
        self.act_event.base = self.base
        self.act_event.group = self.group
        self.act_event.dtype = "s"
        self.act_event.phase = self.phase
        self.act_event.overcharge = self.overcharge

        self.end_event = Event("s_end")
        self.end_event.act = self.act_event

        self.uses = -1

    def getstartup(self):
        return S.TAP_DELAY + super().getstartup()


class Misc(Action):
    def __init__(self, name, conf, act=None, atype=None):
        super().__init__(name, conf, act)
        self.atype = atype or name

        self.act_event = Event(name)
        self.act_event.name = self.name
        self.act_event.base = self.name
        self.act_event.group = globalconf.DEFAULT
        self.act_event.dtype = self.name
        self.act_event.conf = self.conf
        self.act_event.msg = "-"
        self.act_event.logcast = True

        self.end_event = Event(f"{name}_end")
        self.end_event.act = self.act_event

    def getstartup(self):
        return self._startup

    def getrecovery(self):
        return self._recovery


class Dodge(Misc):
    def __init__(self, name, conf, act=None):
        super().__init__(name, conf, act, atype="dodge")
        self.act_event.name = "#" + name
        self.act_event.dtype = "#"


class Shift(Misc):
    def __init__(self, name, dform_name, conf, act=None):
        super().__init__(name, conf, act, atype="s")
        self.act_event.dtype = "x"
        self.act_event.logcast = False
        self.dform_name = dform_name


class DashX(Misc):
    DASH_TIME = 0.5  # prob

    def __init__(self, name, conf, act=None):
        super().__init__(name, conf, act=act)
        self.act_event.dtype = "x"
        self.to_x = conf["to_x"] or 1

    def getstartup(self):
        return super().getstartup() + DashX.DASH_TIME


class Adv(object):

    BASE_CTIME = 2
    SAVE_VARIANT = True
    NO_DEPLOY = False
    FIXED_RNG = None
    MC = None  # generally assume max mc
    DISABLE_DACL = False

    Timer = Timer
    Event = Event
    Listener = Listener

    name = None
    _acl_default = None
    _dacl_default = None

    def dmg_proc(self, name, amount):
        pass

    """
    New before/proc system:
    x/fs/s events will try to call <name>_before before everything, and <name>_proc at each hitattr

    Examples:
    Albert FS:
        fs_proc is called when he uses base fs
        fs2_proc is called when he uses alt fs2

    Addis s1:
        s1_hit1 is called after the 1st s1 hit when s2 buff is not active
        s1_enhanced_hit1 after the 1st s1 hit is called when s2 buff is active
        s1_proc is called after the final (4th) hit

    Mitsuba:
        x_proc is called when base dagger combo
        x_tempura_proc is called when tempura combo
    """

    def prerun(self):
        pass

    @staticmethod
    def prerun_skillshare(adv, dst):
        pass

    comment = ""
    conf = {}
    a1 = None
    a2 = None
    a3 = None

    skill_default = {"startup": 0.0, "recovery": 1.8, "sp": 0}
    conf_default = {
        # Latency represents the human response time, between when an event
        # triggers a "think" event, and when the human actually triggers
        # the input.  Right now it's set to zero, which means "perfect"
        # response time (which is unattainable in reality.)
        "latency.x": 0,
        "latency.sp": 0,
        "latency.default": 0,
        "latency.idle": 0,
        "s1": skill_default,
        "s2": skill_default,
        "s3": skill_default,
        "s4": skill_default,
        "dodge.startup": 0.63333,
        "dodge.recovery": 0,
        "dodge.interrupt": {"s": 0.0},
        "dodge.cancel": {"s": 0.0},
        "dooodge.startup": 3.0,
        "dooodge.recovery": 0,
        "acl": "dragon;s1;s2;s3;s4",
        "mbleed": True,
        "attenuation.hits": 1,
        "attenuation.delay": 0.25,
    }
    actual_buffs_trust = ("self", "team", "echo", "ele", "next", "nearby")

    def hitattr_check(self, name, conf):
        if conf["attr"]:
            for attr in conf["attr"]:
                if not isinstance(attr, dict):
                    continue
                if "dmg" in attr:
                    self.damage_sources.add(name)
                if "buff" in attr:
                    buffs = attr["buff"] if isinstance(attr["buff"][0], list) else (attr["buff"],)
                    if any((bargs[0] in Adv.actual_buffs_trust for bargs in buffs)):
                        self.buff_sources.add(name)
                aff = attr.get("afflic")
                if aff is not None:
                    aff = aff[0]
                    res = int(getattr(self.afflics, aff).resist * 100)
                    if not "999 all affliction res" in self.condition:
                        self.condition(f"{res} {aff} res")
        if conf.get("energizable"):
            self.energy.extra_tensionable.add(name)

    @property
    def current_x(self):
        if self.in_dform():
            return globalconf.DRG
        return self._current_x

    @current_x.setter
    def current_x(self, value):
        self._current_x = value

    def doconfig(self):
        # comment
        if self.conf.c["comment"]:
            self.comment = self.conf.c["comment"]
        # set act
        self.action = Action()
        self.action._static.spd_func = self.speed
        self.action._static.c_spd_func = self.c_speed
        self.action._static.f_spd_func = self.f_speed
        self.action._static.actmod_off = self.actmod_off
        # set buff
        self.base_buff = Buff()
        self.all_buffs = []
        self.base_buff._static.all_buffs = self.all_buffs
        self.base_buff._static.adv = self
        self.active_buff_dict = ActiveBuffDict()
        # set modifier
        self.modifier = Modifier(0, 0, 0, 0)
        self.all_modifiers = ModifierDict()
        self.modifier._static.all_modifiers = self.all_modifiers
        self.modifier._static.g_condition = self.condition
        if self.berserk_mode:
            Modifier("berserk_fs_odmg", "fs", "berserk", self.conf["berserk"] - 1)

        # nihilism
        self.nihilism = bool(self.conf["nihilism"])
        if self.nihilism:
            self.condition("Curse of Nihility")
            self.afflics.set_resist((self.conf.c.ele, self.nihilism))
        self.afflic_condition()

        # auto fsf/dodge
        self._think_modes = set()
        if self.conf["dumb"]:
            self._think_modes.add("dumb")
            self.dumb_cd = int(self.conf["dumb"])
            self.dumb_count = 0
            self.condition(f"be a dumb every {self.dumb_cd}s")

        self.hits = 0
        self.last_c = 0
        self.hit_event = Event("hit")

        self._hp = 3000
        self.base_hp = 3000
        self.hp_event = Event("hp")
        self.heal_event = Event("heal")
        self.dispel_event = Event("dispel")
        self.aff_relief_event = Event("aff_relief")

        from module.tension import Energy, Inspiration

        self.energy = Energy()
        self.inspiration = Inspiration()
        self.tension = [self.energy, self.inspiration]
        if self.nihilism:
            for tension in self.tension:
                tension.set_disabled("nihilism")
        self.sab = []
        self.extra_actmods = []
        self.crisis_mods = {
            "s": CrisisModifier("s_crisis_modifier", "s", self),
            "x": CrisisModifier("x_crisis_modifier", "x", self),
            "fs": CrisisModifier("fs_crisis_modifier", "fs", self),
        }
        self._cooldowns = {}

        self._echoes = {}
        self.bleed = None
        self.alive = True

        # init dragon here so that actions can be processed
        self.slots.d.oninit(self)

        # init actions
        for xn, xconf in self.conf.find(r"^d?x\d+(_[A-Za-z0-9]+)?$"):
            a_x = X(xn, self.conf[xn])
            if xn != a_x.base and self.conf[a_x.base]:
                a_x.conf.update(self.conf[a_x.base], rebase=True)
            self.a_x_dict[a_x.group][a_x.index] = a_x
            self.hitattr_check(xn, xconf)
        self.a_x_dict = dict(self.a_x_dict)
        for group, actions in self.a_x_dict.items():
            gxmax = f"{group}.x_max"
            if not self.conf[gxmax]:
                self.conf[gxmax] = max(actions.keys())
        self.current_x = globalconf.DEFAULT
        self.deferred_x = None

        for name, fs_conf in self.conf.find(r"^d?fs\d*(_[A-Za-z0-9]+)?$"):
            try:
                base = name.split("_")[0]
                if base.startswith("fs") and base != "fs":
                    fs_conf.update(self.conf.fs, rebase=True)
                if name != base and self.conf[base]:
                    fs_conf.update(self.conf[base], rebase=True)
            except KeyError:
                pass
            self.a_fs_dict[name] = Fs(name, fs_conf)
            self.hitattr_check(name, fs_conf)
        if "fs1" in self.a_fs_dict:
            self.a_fs_dict["fs"].enabled = False
        self.current_fs = None
        self.alt_fs_buff = None

        if not self.conf["cannot_fsf"]:
            self.a_fsf = Fs("fsf", self.conf.fsf)
            self.a_fsf.act_event = Event("none")

        self.a_dodge = Dodge("dodge", self.conf.dodge)
        self.a_dooodge = Dodge("dooodge", self.conf.dooodge)
        self.a_dash = None
        if self.conf["dash"]:
            self.a_dash = DashX("dash", self.conf.dash)

        self.actconds = {}

    @property
    def ctime(self):
        # base ctime is 2
        return self.mod("ctime", operator.add, initial=Adv.BASE_CTIME)

    def actmod_on(self, e):
        do_sab = True
        do_tension = e.name.startswith("s") or e.base in ("ds1", "ds2")
        if do_tension:
            for t in self.tension:
                t.on(e)
        if do_sab:
            for b in self.sab:
                b.act_on(e)

    def actmods(self, name, base=None, group=None, aseq=None, attr=None):
        mods = []
        for m in self.extra_actmods:
            if isinstance(m, Modifier):
                if name == m.mod_name:
                    mods.append(m)
            else:
                modifier = m(name, base, group, aseq, attr)
                if modifier:
                    if isinstance(modifier, list):
                        mods.extend(modifier)
                    else:
                        mods.append(modifier)
        for t in chain(self.tension, self.sab):
            if name in t.active:
                mods.append(t.modifier)
        if name != "dodge" and name[0] == "d":
            mods.extend(self.dragonform.shift_mods)
        # log('actmods', name, str(mods))
        return mods

    def actmod_off(self, e):
        do_sab = True
        do_tension = e.dtype == "s"
        if do_tension:
            for t in self.tension:
                t.off(e)
        if do_sab:
            for b in self.sab:
                b.act_off(e)

    def l_set_hp(self, e):
        can_die = getattr(e, "can_die", None)
        ignore_dragon = getattr(e, "ignore_dragon", False)
        source = getattr(e, "source", None)
        try:
            self.add_hp(e.delta, can_die=can_die, ignore_dragon=ignore_dragon, source=source)
        except AttributeError:
            self.set_hp(e.hp, can_die=can_die, ignore_dragon=ignore_dragon, source=source)

    def l_heal_make(self, e):
        self.heal_make(e.name, e.delta, target=e.target, fixed=True)

    def heal_formula(self, name, coef):
        healstat = self.max_hp * 0.16 + self.base_att * self.mod("att") * 0.06
        energize = 1
        if name in self.energy.active:
            energize += self.energy.modifier.get()
        potency = self.mod("recovery")
        elemental_mod = 1.2
        coef_mod = 0.01
        # log("heal_formula", coef * coef_mod, healstat, energize, potency, elemental_mod)
        return coef * coef_mod * healstat * energize * potency * elemental_mod

    def heal_make(self, name, coef, target="self", fixed=False):
        if fixed:
            heal_value = coef
        else:
            heal_value = self.heal_formula(name, coef)
        log("heal", name, heal_value, target)
        if target != "self":
            self.slots.c.set_need_healing()
        self.add_hp(heal_value, percent=False)

    def add_hp(self, delta, percent=True, can_die=False, ignore_dragon=False, source=None):
        if percent:
            if self.in_dform() and delta < 0 and not ignore_dragon:
                self.dragonform.extend_shift_time(delta / 100, percent=True)
                return delta
            delta = self.max_hp * delta / 100
        if delta > 0:
            delta *= self.sub_mod("getrecovery", "buff") + 1
        new_hp = self._hp + delta
        self.set_hp(new_hp, percent=False, can_die=can_die, ignore_dragon=ignore_dragon, source=source)

    def set_hp(self, hp, percent=True, can_die=False, ignore_dragon=False, source=None):
        max_hp = self.max_hp
        if self.conf["flask_env"] and "hp" in self.conf:
            hp = self.conf["hp"]
            percent = True
        old_hp = self._hp
        if percent:
            hp = max_hp * hp / 100
        if hp > old_hp:
            self.heal_event.delta = hp - old_hp
            self.heal_event()
        elif self.in_dform() and not ignore_dragon:
            delta = (hp - old_hp) / 10000
            if delta < 0:
                self.dragonform.extend_shift_time(delta, percent=True)
                return delta
        if can_die:
            self._hp = max(min(hp, max_hp), 0)
            if self._hp == 0:
                self.stop()
                self.alive = False
                return
        else:
            self._hp = max(min(hp, max_hp), 1)
        if self._hp != old_hp:
            delta = self._hp - old_hp
            log("hp", f"{self._hp / max_hp:.1%}", f"{int(self._hp)}/{max_hp}", f"{round(delta):+}")
            self.condition.hp_cond_update()
            self.hp_event.hp = self.hp
            self.hp_event.real_hp = self._hp
            self.hp_event.delta = (delta / max_hp) * 100
            self.hp_event.real_delta = delta
            self.hp_event.source = source
            self.hp_event()

            if self._hp < max_hp:
                self.slots.c.set_need_regen()
            return delta

    @property
    def hp(self):
        if self._hp == 1:
            return 0
        return min(self._hp / self.max_hp * 100, 100)

    def get_hp(self):
        return self.hp

    def max_hp_mod(self):
        return 1 + min(0.3, self.sub_mod("maxhp", "buff")) + self.sub_mod("maxhp", "passive")

    @property
    def max_hp(self):
        return float_ceil(self.base_hp, self.max_hp_mod())

    def afflic_condition(self):
        if "afflict_res" in self.conf:
            res_conf = self.conf.afflict_res
            if self.berserk_mode or all((value >= 300 for value in res_conf.values())):
                self.condition("999 all affliction res")
                self.afflics.set_resist("immune")
            else:
                for afflic, resist in res_conf.items():
                    if self.condition(f"{resist} {afflic} res"):
                        vars(self.afflics)[afflic].resist = resist

    def sim_affliction(self):
        if self.berserk_mode:
            return
        if "sim_afflict" in self.conf:
            if self.conf.sim_afflict["onele"]:
                for aff_type in globalconf.ELE_AFFLICT[self.conf.c.ele]:
                    aff = vars(self.afflics)[aff_type]
                    aff.get_override = 1
                    self.sim_afflict.add(aff_type)
            else:
                for aff_type in AFFLICT_LIST:
                    aff = vars(self.afflics)[aff_type]
                    if self.conf.sim_afflict[aff_type]:
                        aff.get_override = min(self.conf.sim_afflict[aff_type], 1.0)
                        self.sim_afflict.add(aff_type)

    def sim_buffbot(self):
        if "sim_buffbot" in self.conf:
            if "def_down" in self.conf.sim_buffbot:
                value = self.conf.sim_buffbot.def_down
                if self.condition("boss def {:+.0%}".format(value)):
                    buff = self.Selfbuff("simulated_def", value, -1, mtype="def")
                    buff.chance = 1
                    buff.val = value
                    buff.on()
            if "str_buff" in self.conf.sim_buffbot:
                if self.condition("team str {:+.0%}".format(self.conf.sim_buffbot.str_buff)):
                    self.Selfbuff("simulated_att", self.conf.sim_buffbot.str_buff, -1).on()
            if "critr" in self.conf.sim_buffbot:
                if self.condition("team crit rate {:+.0%}".format(self.conf.sim_buffbot.critr)):
                    self.Selfbuff(
                        "simulated_crit_rate",
                        self.conf.sim_buffbot.critr,
                        -1,
                        "crit",
                        "chance",
                    ).on()
            if "critd" in self.conf.sim_buffbot:
                if self.condition("team crit dmg {:+.0%}".format(self.conf.sim_buffbot.critd)):
                    self.Selfbuff(
                        "simulated_crit_dmg",
                        self.conf.sim_buffbot.critd,
                        -1,
                        "crit",
                        "damage",
                    ).on()
            if "echo" in self.conf.sim_buffbot:
                if self.condition("echo att {:g}".format(self.conf.sim_buffbot.echo)):
                    self.enable_echo("sim", fixed_att=self.conf.sim_buffbot.echo)
            if "doublebuff_interval" in self.conf.sim_buffbot:
                interval = round(self.conf.sim_buffbot.doublebuff_interval, 2)
                if self.condition("team doublebuff every {:.2f} sec".format(interval)):
                    sim_defchain = Event("defchain")
                    sim_defchain.source = None

                    def proc_sim_doublebuff(t):
                        sim_defchain()
                        # assume that this is a skill buff
                        self.buffskill_event()

                    Timer(proc_sim_doublebuff, interval, True).on()
            if "dprep" in self.conf.sim_buffbot:
                if self.condition(f"team dprep {self.conf.sim_buffbot.dprep}%"):
                    self.dragonform.charge_dprep(self.conf.sim_buffbot.dprep)

    def config_slots(self):
        if self.conf["classbane"] == "HDT":
            self.conf.c.a.append(["k_HDT", 0.3])
        self.slots.set_slots(self.conf.slots)
        self.element = self.slots.c.ele

    def config_acl(self):
        # acl
        self.conf.acl, _ = core.acl.extract_dact(self.conf.acl)
        if self.acl_source != "init":
            if self._acl_default is None:
                self._acl_default = core.acl.build_acl(self.conf.acl)
            self._acl = self._acl_default
        else:
            self._acl = core.acl.build_acl(self.conf.acl)
        self._acl.reset(self)
        # dacl
        self.using_default_dacl = False
        if not self.conf["dacl"]:
            if self.slots.d.dform["dacl"]:
                self.conf.dacl = self.slots.d.dform["dacl"]
            else:
                self.conf.dacl = DragonBase.DEFAULT_DCONF["dacl"]
            self.using_default_dacl = True
        else:
            self.using_default_dacl = (self.slots.d.dform["dacl"] and self.conf.dacl == self.slots.d.dform["dacl"]) or self.conf.dacl == DragonBase.DEFAULT_DCONF["dacl"]
        if self.dacl_source != "init":
            if self._dacl_default is None:
                self._dacl_default = core.acl.build_acl(self.conf.dacl)
            self._dacl = self._dacl_default
        else:
            self._dacl = core.acl.build_acl(self.conf.dacl)
        self._dacl.reset(self)

        self._c_acl = self._acl

    def pre_conf(self, equip_conditions=None, name=None):
        self.conf = Conf(self.conf_default)
        self.acl_source, self.dacl_source = None, None
        self.conf.update(globalconf.get_adv(name or self.name))
        if not self.conf["prefer_baseconf"]:
            self.conf.update(self.conf_base)
        self.equip_conf, self.real_equip_conditions = self.equip_manager.get_preferred_entry(equip_conditions)
        equip_conditions = equip_conditions or self.real_equip_conditions
        self.equip_conditions = equip_conditions
        self.conf.update(equip_conditions.get_conf())
        if self.equip_conf:
            self.conf.update(self.equip_conf)
            self.acl_source = "equip" if "acl" in self.equip_conf else self.acl_source
            self.dacl_source = "equip" if "dacl" in self.equip_conf else self.dacl_source
        self.conf.update(self.conf_init)
        self.acl_source = "init" if "acl" in self.conf_init else self.acl_source
        self.dacl_source = "init" if "dacl" in self.conf_init else self.dacl_source
        if self.conf["prefer_baseconf"]:
            self.conf.update(self.conf_base)
            self.acl_source = "init"
            self.dacl_source = "init"

    def default_slot(self):
        self.slots = Slots(self.name, self.conf.c, self.sim_afflict, bool(self.conf["flask_env"]))

    def __init__(self, name=None, conf=None, duration=180, equip_conditions=None, opt_mode=None):
        if not name:
            raise ValueError("Adv module must have a name")
        self.name = name
        if self.__class__.__name__.startswith(self.name):
            self.variant = self.__class__.__name__.replace(self.name, "").strip("_")
        elif self.__class__.__name__.startswith("Adv"):
            self.variant = self.__class__.__name__.replace("Adv", "").strip("_")
        else:
            self.variant = None

        self.Event = Event
        self.Buff = Buff
        self.Debuff = Debuff
        self.Selfbuff = Selfbuff
        self.Teambuff = Teambuff
        self.Modifier = Modifier
        self.Conf = Conf

        self.conf_base = Conf(self.conf or {})
        self.conf_init = Conf(conf or {})
        self.ctx = Ctx().on()
        self.condition = Condition(None, self)
        self.duration = duration

        self.damage_sources = set()
        self.Modifier._static.damage_sources = self.damage_sources
        self.buff_sources = set()
        self.buffskill_event = Event("buffskill")

        self.equip_manager = get_equip_manager(self.name, variant=self.variant, save_variant_build=self.SAVE_VARIANT)
        self.equip_conditions = None
        self.real_equip_conditions = None
        self.equip_manager.set_pref_override(opt_mode)
        self.pre_conf(equip_conditions=equip_conditions)
        self.equip_manager.set_pref_override(None)

        self.dragonform = None

        # set afflic
        self.afflics = Afflics()
        if self.conf["berserk"]:
            self.berserk_mode = True
            self.condition(f"Agito Berserk Phase ODPS (FS {self.conf.berserk:.0f}x)")
            self.afflics.set_resist("immune")
        else:
            self.nihilism = bool(self.conf["nihilism"])
            self.berserk_mode = False
            self.afflics.set_resist((self.conf.c.ele, self.nihilism))
        self.sim_afflict = set()
        self.sim_affliction()

        self.default_slot()

        self.crit_mod = self.solid_crit_mod
        # self.crit_mod = self.rand_crit_mod

        self.Skill = Skill()

        self.a_x_dict = defaultdict(lambda: {})
        self.a_fs_dict = {}
        self.a_s_dict = {f"s{n}": Skill(f"s{n}") for n in range(1, 5)}
        self.a_s_dict["ds1"] = Skill("ds1")
        self.a_s_dict["ds2"] = Skill("ds2")

        # self.classconf = self.conf
        # self.init()

        # self.ctx.off()
        self._acl = None
        self._dacl = None
        self._c_acl = None
        self.using_default_dacl = False

        self.stats = []

    def dmg_mod(self, name, dtype=None):
        mod = 1
        if dtype is None:
            dtype = name.split("_")
            if dtype[0] == "o":
                dtype = dtype[1]
            else:
                dtype = dtype[0]
            if name.startswith("dx"):
                dtype = "x"
            elif name.startswith("ds") and name[2].isdigit():
                dtype = "s"

        if self.berserk_mode:
            mod *= self.mod("odaccel")

        if dtype == "s":
            try:
                mod *= 1 if self.a_s_dict[name].owner is None else self.skill_share_att
            except:
                pass
            return mod * self.mod("s")
        elif dtype == "x":
            return mod * self.mod("x")
        elif dtype == "fs":
            return mod * self.mod("fs")
        else:
            return mod

    @allow_acl
    def mod(self, mtype, operator=None, initial=1):
        return self.all_modifiers.mod(mtype, operator=operator, initial=initial)

    @allow_acl
    def sub_mod(self, mtype, morder):
        return self.all_modifiers.sub_mod(mtype, morder)

    @allow_acl
    def adv_affres(self, aff):
        return self.all_modifiers.sub_mod("affres", aff) + self.all_modifiers.sub_mod("affres", "all")

    @allow_acl
    def speed(self, target=None):
        if target is None:
            return 1 + min(self.sub_mod("spd", "buff"), 0.50) + self.sub_mod("spd", "passive")
        else:
            return 1 + min(self.sub_mod("spd", "buff"), 0.50) + self.sub_mod("spd", "passive") + self.sub_mod("spd", target)

    @allow_acl
    def c_speed(self):
        return 1 + min(self.sub_mod("cspd", "buff"), 0.50) + self.sub_mod("cspd", "passive")

    @allow_acl
    def f_speed(self):
        return 1 + min(self.sub_mod("fspd", "buff"), 0.50) + self.sub_mod("fspd", "passive")

    def enable_echo(self, name, active_time=None, mod=None, fixed_att=None):
        new_att = fixed_att or (mod * self.base_att * self.mod("att"))
        if new_att >= self.echo_att:
            if active_time is not None:
                self.disable_echo(name, active_time)
            active_time = now()
            self._echoes[(name, active_time)] = new_att
            log("echo", name, new_att, str(self._echoes))
            return active_time
        return False

    @property
    def echo(self):
        return 2 if self._echoes else 1

    @property
    def echo_att(self):
        return 0 if not self._echoes else max(self._echoes.values())

    def disable_echo(self, name, active_time):
        try:
            del self._echoes[(name, active_time)]
        except KeyError:
            pass

    def dmg_formula_echo(self, coef):
        # so 5/3(Bonus Damage amount)/EnemyDef +/- 5%
        armor = 10 * self.def_mod()
        return 5 / 3 * (self.echo_att * coef) / armor

    def crit_mod(self):
        return 1

    def combine_crit_mods(self):
        m = {"chance": 0, "damage": 0}
        for order, modifiers in self.all_modifiers["crit"].items():
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
                    for order, mods in self.all_modifiers[f"{cond_name}_crit"].items():
                        for mod in mods:
                            modifiers[order].add(mod)
                else:
                    p *= 1 - cond_p
            # total += p * reduce(operator.mul, [1 + sum([mod.get() for mod in order]) for order in modifiers.values()], 1.0)
            for order, values in modifiers.items():
                m[order] += p * sum([mod.get() for mod in values])

        chance = min(m["chance"], 1)
        cdmg = m["damage"] + 1.7

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

    @allow_acl
    def att_mod(self, name=None):
        att = self.mod("att")
        cc = self.crit_mod(name)
        k = self.killer_mod(name)
        # if name == 's1_ddrive':
        #     print(dict(self.all_modifiers['att']))
        #     exit()
        return cc * att * k

    def uses_affliction(self):
        return bool(self.afflics.get_attempts()) or any((self.mod(f"{afflic}_killer") > 1 for afflic in AFFLICT_LIST))

    def build_rates(self, as_list=True):
        rates = {}
        for afflic in AFFLICT_LIST:
            rate = vars(self.afflics)[afflic].get()
            if rate > 0:
                rates[afflic] = rate

        if self.bleed is None:
            debuff_rates = {}
        else:
            rates["bleed"] = self.bleed.get()
            debuff_rates = {"debuff": 1 - rates["bleed"]}

        for buff in self.all_buffs:
            if buff.get() and (buff.bufftype == "debuff" or buff.name == "simulated_def") and buff.val < 0:
                dkey = f"debuff_{buff.mod_type}"
                try:
                    debuff_rates[dkey] *= 1 - buff.chance
                except:
                    debuff_rates[dkey] = 1 - buff.chance
                try:
                    debuff_rates["debuff"] *= 1 - buff.chance
                except:
                    debuff_rates["debuff"] = 1 - buff.chance
        for dkey in debuff_rates.keys():
            debuff_rates[dkey] = 1 - debuff_rates[dkey]
        rates.update(debuff_rates)

        if self.conf["classbane"]:
            enemy_class = self.conf["classbane"]
            if self.condition(f"vs {enemy_class} enemy"):
                rates[enemy_class] = 1

        return rates if not as_list else list(rates.items())

    def killer_mod(self, name=None):
        total = self.mod("killer") - 1
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
                    if cond_name in AFFLICT_LIST:
                        for order, mods in self.all_modifiers["afflicted_killer"].items():
                            for mod in mods:
                                modifiers[order].add(mod)
                else:
                    p *= 1 - cond_p
            total += p * reduce(
                operator.mul,
                [1 + sum([mod.get() for mod in order]) for order in modifiers.values()],
                1.0,
            )
        return total

    def set_cd(self, key, timeout, proc=None):
        if not timeout or timeout <= 0:
            return
        if key is None:
            raise ValueError("Cooldown key cannot be None")
        log("set_cd", str(key), timeout)
        timeout -= 0.0001  # avoid race cond
        try:
            self._cooldowns[key].on(timeout=timeout)
        except KeyError:
            self._cooldowns[key] = Timer(proc=proc, timeout=timeout).on()

    def _is_cd(self, key):
        try:
            return bool(self._cooldowns[key].online)
        except KeyError:
            return False

    def is_set_cd(self, key, timeout, proc=None):
        if self._is_cd(key):
            return True
        self.set_cd(key, timeout, proc=proc)
        return False

    @allow_acl
    def is_cd(self, *args):
        if len(args) > 1:
            return self._is_cd(tuple(args))
        target_key = args[0]
        if isinstance(target_key, str):
            return self._is_cd(target_key)
        for key in self._cooldowns:
            if isinstance(key, tuple) and key[0] == target_key:
                return self._is_cd(key)
        return False

    @allow_acl
    def def_mod(self):
        defa = min(1 - self.mod("def", operator=operator.add), 0.5)
        defb = min(1 - self.mod("defb", operator=operator.add), 0.3)
        berserk_def = 4 if self.berserk_mode else 1
        return (1 - min(defa + defb, 0.5)) * berserk_def

    @allow_acl
    def sp_mod(self, name, target=None):
        if name == "sp_regen":
            return 1
        sp_mod = self.mod("sp", operator=operator.add)
        if name.startswith("fs"):
            sp_mod += self.mod("spf", operator=operator.add, initial=0)
        if target is not None:
            sp_mod += self.mod(f"sp_{target}", operator=operator.add, initial=0)
        return sp_mod

    @allow_acl
    def sp_val(self, param, target=None):
        if self.in_dform():
            if target not in ("ds1", "ds2"):
                return 0
            if param.startswith("fs"):
                actkeys = ("d" + param,)
            elif isinstance(param, int):
                actkeys = (f"dx{i}" for i in range(1, min(param, self.dragonform.dx_max) + 1))
            else:
                actkeys = (param,)
        else:
            if target not in ("s1", "s2", "s3", "s4"):
                return 0
            if isinstance(param, int):
                suffix = "" if self.current_x == globalconf.DEFAULT else f"_{self.current_x}"
                actkeys = (f"x{i}{suffix}" for i in range(1, min(param, self.conf[self.current_x].x_max) + 1))
            else:
                actkeys = (param,)
        sp_sum = 0
        for act in actkeys:
            attrs = self.conf[f"{act}.attr"]
            if not attrs:
                continue
            for attr in attrs:
                if attr.get("sp"):
                    break
            if attr:
                sp_sum += attr.get("sp", 0)
        return sp_sum

    @allow_acl
    def charged_in(self, param, sn):
        s = getattr(self, sn)
        return self.sp_val(param, target=sn) + s.charged >= s.sp

    @allow_acl
    def have_buff(self, name):
        for b in self.all_buffs:
            if b.name.startswith(name) and b.get():
                return True
        return False

    @allow_acl
    def buffstack(self, name):
        return reduce(lambda s, b: s + int(b.get() and b.name == name), self.all_buffs, 0)

    @property
    def buffcount(self):
        buffcount = reduce(
            lambda s, b: s + int(b.get() and b.bufftype in ("self", "team") and not b.hidden),
            self.all_buffs,
            0,
        )
        if self.conf["sim_buffbot.count"] is not None:
            buffcount += self.conf.sim_buffbot.count
        return buffcount

    @property
    def zonecount(self):
        return len([b for b in self.all_buffs if type(b) == ZoneTeambuff and b.get()])

    def add_amp(self, amp_id="10000", max_level=3, target=0):
        self.hitattr_make(
            "amp_proc",
            "amp",
            "proc",
            0,
            {"amp": [amp_id, max_level, target]},
        )

    @allow_acl
    def amp_lvl(self, kind=None, key="10000"):
        try:
            return self.active_buff_dict.get_amp(key).level(kind, adjust=kind is None)
        except (ValueError, KeyError):
            return 0

    @allow_acl
    def amp_timeleft(self, kind=None, key="10000"):
        try:
            return self.active_buff_dict.get_amp(key).timeleft(kind)
        except (ValueError, KeyError):
            return 0

    def l_idle(self, e):
        """
        Listener that is called when there is nothing to do.
        """
        self.think_pin("idle")
        prev = self.action.getprev()
        if prev.name[0] == "s":
            self.think_pin(prev.name)
        if self.Skill._static.first_x_after_s:
            self.Skill._static.first_x_after_s = 0
            s_prev = self.Skill._static.s_prev
            self.think_pin("%s-x" % s_prev)
        # return self.x()

    def l_defer(self, e):
        self.think_pin(e.pin)

    def getprev(self):
        prev = self.action.getprev()
        return prev.name, prev.index, prev.status

    @allow_acl
    def dragon(self):
        return self.dragonform.shift()

    @allow_acl
    def sack(self):
        return self.dragonform.sack()

    def in_dform(self):
        return self.dragonform.in_dform()

    @property
    def in_drg(self):
        return self.dragonform.status

    @property
    def can_drg(self):
        return self.dragonform.check()

    @allow_acl
    def fs(self, n=None):
        fsn = "fs" if n is None else f"fs{n}"
        if self.in_dform():
            fsn = "d" + fsn
        self.check_deferred_x()
        if self.current_fs is not None:
            fsn += "_" + self.current_fs
        try:
            return self.a_fs_dict[fsn]()
        except KeyError:
            return False

    @allow_acl
    def dfs(self, n=None):
        if not self.in_dform():
            return False
        fsn = "dfs" if n is None else f"dfs{n}"
        self.check_deferred_x()
        try:
            return self.a_fs_dict[fsn]()
        except KeyError:
            return False

    @allow_acl
    def fst(self, t=None, n=None, include_fs_anim=True):
        fsn = "fs" if n is None else f"fs{n}"
        if self.in_dform():
            fsn = "d" + fsn
        if self.current_fs is not None:
            fsn += "_" + self.current_fs
        try:
            fs_act = self.a_fs_dict[fsn]
        except KeyError:
            return False
        delta = 0
        if include_fs_anim:
            delta = fs_act.getstartup(include_buffer=False) + fs_act.getrecovery()
        else:
            delta = fs_act.getcharge(include_buffer=False)
        if delta < t:
            fs_act.extra_charge = t - delta
        return self.fs(n=n)

    @allow_acl
    def fstc(self, t=None, n=None):
        return self.fst(t=t, n=n, include_fs_anim=False)

    def check_deferred_x(self):
        if self.deferred_x is not None and not self.in_dform():
            log("deferred_x", self.deferred_x)
            self.current_x = self.deferred_x
            self.deferred_x = None

    def _next_x(self, prev=None):
        self.check_deferred_x()
        prev = prev or self.action.getdoing()
        if prev is self.action.nop:
            prev = self.action.getprev()
        if isinstance(prev, X):
            if prev.group == self.current_x and prev.conf["loop"]:
                x_next = prev
            else:
                if prev.index < self.conf[self.current_x].x_max:
                    x_next = self.a_x_dict[self.current_x][prev.index + 1]
                else:
                    x_next = self.a_x_dict[self.current_x][1]
                if not prev.has_follow(x_next.name, "any"):
                    x_next = self.a_x_dict[self.current_x][1]
        elif isinstance(prev, DashX):
            x_next = self.a_x_dict[self.current_x][prev.to_x]
        else:
            x_next = self.a_x_dict[self.current_x][1]
        # special: in dform and if there isn't enough time left to complete next x, try sack instead
        if x_next.group == globalconf.DRG:
            if self.dragonform.dform_mode == -1 and not self.dragonform.untimed_shift and x_next.getstartup() >= self.dshift_timeleft:
                return self.sack()
        elif not x_next.enabled:
            self.current_x = globalconf.DEFAULT
            x_next = self.a_x_dict[self.current_x][1]
        return x_next()

    @allow_acl
    def dx(self, n=1):
        # dragon acl compat thing
        # force dodge cancel if not at max combo, or check dform
        if not self.in_dform():
            return CONTINUE
        prev = self.action.getdoing()
        if isinstance(prev, X) and prev.index == n and prev.status == Action.RECOVERY:
            if prev.index < self.conf[prev.group].x_max or self.dragonform.auto_dodge(prev.index):
                x_next = self.dragonform.d_dodge
            else:
                x_next = self.a_x_dict[self.current_x][1]
            return x_next()
        return False

    def l_x(self, e):
        # FIXME: race condition?
        x_max = self.conf[self.current_x].x_max
        logname = e.base if e.group in (globalconf.DEFAULT, globalconf.DRG) else e.name
        if e.index == x_max and not self.conf[e.name]["loop"]:
            log("x", logname, "-" * 45 + f" c{x_max} ")
        else:
            log("x", logname)
        self.hit_make(
            e,
            self.conf[e.name],
            cb_kind=f"x_{e.group}" if e.group != globalconf.DEFAULT else "x",
            pin="x",
            actmod=False,
        )

    @allow_acl
    def dodge(self):
        if self.in_dform():
            return self.dragonform.d_dodge()
        return self.a_dodge()

    @allow_acl
    def dooodge(self):
        self.last_c = 0
        return self.a_dooodge()

    @allow_acl
    def dash(self):
        if self.in_dform() or not self.a_dash:
            return False
        return self.a_dash()

    @allow_acl
    def fsf(self):
        try:
            return self.a_fsf()
        except AttributeError:
            return False

    def l_misc(self, e):
        if e.logcast:
            log("cast", e.name, e.msg)
        self.hit_make(e, e.conf, cb_kind=e.name.strip("#"))
        self.think_pin(e.name)

    def add_combo(self, name="#"):
        # real combo count
        delta = now() - self.last_c
        ctime = self.ctime
        self.last_c = now()
        g_logs.total_hits += self.echo
        kept_combo = delta <= ctime
        if delta <= ctime:
            self.hits += self.echo
            self.slots.c.update_req_ctime(delta, ctime)
        else:
            self.hits = self.echo
            log("combo", f"reset combo after {delta:2.4}s")
        self.hit_event.name = name
        self.hit_event.add = self.echo
        self.hit_event.hits = self.hits
        self.hit_event.kept_combo = kept_combo
        self.hit_event()
        return kept_combo

    def load_aff_conf(self, key):
        confv = self.conf[key]
        if confv is None:
            return []
        if isinstance(confv, list):
            return confv
        if self.sim_afflict:
            aff = next(iter(self.sim_afflict))
            if confv[aff]:
                return confv[aff]
        return confv["base"] or []

    def config_coabs(self):
        if not self.conf["flask_env"]:
            coab_list = self.load_aff_conf("coabs")
        else:
            coab_list = self.conf["coabs"] or []
        self.slots.c.set_coab_list(coab_list)

    def rebind_function(self, owner, src, dst=None, overwrite=True):
        dst = dst or src
        if not overwrite and hasattr(self, dst):
            return
        try:
            self.__setattr__(dst, getattr(owner, src).__get__(self, self.__class__))
        except AttributeError:
            pass

    @property
    def skills(self):
        return (self.s1, self.s2, self.s3, self.s4)

    @property
    def dskills(self):
        if self.ds2.ac:
            return (self.ds1, self.ds2)
        return (self.ds1,)

    @allow_acl
    def s(self, n):
        if self.in_dform():
            return False
        self.check_deferred_x()
        skey = f"s{n}"
        try:
            return self.a_s_dict[skey]()
        except KeyError:
            return False

    @allow_acl
    def ds(self, n=1):
        if not self.in_dform():
            return False
        try:
            return self.a_s_dict[f"ds{n}"]()
        except KeyError:
            return False

    @property
    def s1(self):
        return self.a_s_dict["s1"]

    @property
    def s2(self):
        return self.a_s_dict["s2"]

    @property
    def s3(self):
        return self.a_s_dict["s3"]

    @property
    def s4(self):
        return self.a_s_dict["s4"]

    @property
    def ds1(self):
        return self.a_s_dict["ds1"]

    @property
    def ds2(self):
        return self.a_s_dict["ds2"]

    def config_skills(self):
        self.current_s = {
            "s1": globalconf.DEFAULT,
            "s2": globalconf.DEFAULT,
            "s3": globalconf.DEFAULT,
            "s4": globalconf.DEFAULT,
            "ds1": globalconf.DEFAULT,
            "ds2": globalconf.DEFAULT,
        }
        self.Skill._static.current_s = self.current_s
        self.conf.s1.owner = None
        self.conf.s2.owner = None

        if not self.conf["flask_env"]:
            self.skillshare_list = self.load_aff_conf("share")
        else:
            self.skillshare_list = self.conf["share"] or []
        preruns = {}
        try:
            self.skillshare_list.remove(self.name)
        except ValueError:
            pass
        self.skillshare_list = list(OrderedDict.fromkeys(self.skillshare_list))
        if len(self.skillshare_list) > 2:
            self.skillshare_list = self.skillshare_list[:2]
        if len(self.skillshare_list) < 2:
            self.skillshare_list.insert(0, "Weapon")

        from conf import skillshare
        from core.simulate import load_adv_module

        self_data = skillshare.get(self.name, {})
        share_limit = self_data.get("limit", 10)
        sp_modifier = self_data.get("mod_sp", 1)
        self.skill_share_att = self_data.get("mod_att", 0.7)
        share_costs = 0

        for idx, owner in enumerate(self.skillshare_list):
            dst_key = f"s{idx+3}"
            # if owner == 'Weapon' and (self.slots.w.noele or self.slots.c.ele in self.slots.w.ele):
            if owner == "Weapon":
                s3 = self.slots.w.s3
                if s3:
                    self.conf.update(s3)
                    self.conf.s3.owner = None
            else:
                # I am going to spaget hell for this
                sdata = skillshare[owner]
                try:
                    share_costs += sdata["cost"]
                except KeyError:
                    # not allowed to share skill
                    continue
                if share_limit < share_costs:
                    raise ValueError(f"Skill share exceed cost {(*self.skillshare_list, share_costs)}.")
                src_key = f's{sdata["s"]}'
                shared_sp = self.sp_convert(sdata["sp"], sp_modifier)
                try:
                    owner_module, _, _ = load_adv_module(owner)
                    owner_conf = globalconf.get_adv(owner)
                    for src_sn, src_snconf in owner_conf.find(f"^{src_key}(_[A-Za-z0-9]+)?$"):
                        dst_sn = src_sn.replace(src_key, dst_key)
                        self.conf[dst_sn] = src_snconf
                        modified_attr = []
                        hitseq = []
                        for idx, attr in enumerate(self.conf[dst_sn].get("attr", [])):
                            if isinstance(attr, dict):
                                if attr.get("ab"):
                                    continue
                                hitseq.append(idx + 1)
                                if attr.get("buffele", self.slots.c.ele) != self.slots.c.ele:
                                    attr = dict(attr)
                                    del attr["buff"]
                                    del attr["buffele"]
                                    if all((k == "iv" or k == "msl" for k in attr)):
                                        continue
                            modified_attr.append(attr)
                        self.conf[dst_sn]["attr"] = modified_attr
                        self.conf[dst_sn].owner = owner
                        self.conf[dst_sn].sp = shared_sp

                        for idx, hs in enumerate(hitseq):
                            self.rebind_function(owner_module, f"{src_sn}_hit{idx+1}", f"{dst_sn}_hit{hs}")

                    preruns[dst_key] = owner_module.prerun_skillshare
                    for sfn in ("before", "proc"):
                        self.rebind_function(owner_module, f"{src_key}_{sfn}", f"{dst_key}_{sfn}")
                except:
                    pass
                self.conf[dst_key].owner = owner
                self.conf[dst_key].sp = shared_sp

        for sn, snconf in self.conf.find(r"^d?s\d(_[A-Za-z0-9]+)?$"):
            s = S(sn, snconf)
            if s.group != globalconf.DEFAULT and self.conf[s.base]:
                snconf.update(self.conf[s.base], rebase=True)
            if s.group.startswith("phase"):
                s.group = int(s.group[5:])
                try:
                    self.a_s_dict[s.base].p_max = max(self.a_s_dict[s.base].p_max, s.group)
                except ValueError:
                    self.a_s_dict[s.base].p_max = s.group
                self.current_s[s.base] = 0
                s.group -= 1
                s.act_event.group = s.group
            phase_up = True
            if self.nihilism:
                phase_up = snconf.get("phase_coei")
            self.a_s_dict[s.base].add_action(s.group, s, phase_up=phase_up)
            self.hitattr_check(sn, snconf)

        return preruns

    def run(self):
        global loglevel
        if not loglevel:
            loglevel = 0

        self.ctx.on()
        g_logs.reset()

        self.config_slots()
        self.doconfig()

        self.l_idle = Listener("idle", self.l_idle)
        self.l_defer = Listener("defer", self.l_defer)
        self.l_x = Listener("x", self.l_x)
        self.l_dodge = Listener("dodge", self.l_misc)
        self.l_dash = Listener("dash", self.l_misc)
        self.l_dshift = Listener("dshift", self.l_misc)
        self.l_fs = Listener("fs", self.l_fs)
        self.l_s = Listener("s", self.l_s)
        self.l_repeat = Listener("repeat", self.l_repeat)
        # self.l_x           = Listener(['x','x1','x2','x3','x4','x5'],self.l_x)
        # self.l_fs          = Listener(['fs','x1fs','x2fs','x3fs','x4fs','x5fs'],self.l_fs)
        # self.l_s           = Listener(['s','s1','s2','s3'],self.l_s)
        self.l_silence_end = Listener("silence_end", self.l_silence_end)
        self.l_dmg_make = Listener("dmg_make", self.l_dmg_make)
        self.l_true_dmg = Listener("true_dmg", self.l_true_dmg)
        self.l_dmg_formula = Listener("dmg_formula", self.l_dmg_formula)
        self.l_set_hp = Listener("set_hp", self.l_set_hp)
        self.l_heal_make = Listener("heal_make", self.l_heal_make)

        self.uses_combo = False

        preruns_ss = self.config_skills()

        # if self.conf.c.a:
        #     self.slots.c.a = list(self.conf.c.a)

        self.config_coabs()

        self.base_att = 0

        self.slots.oninit(self)
        self.base_att = int(self.slots.att)
        self.base_hp = int(self.slots.hp)
        self._hp = self.max_hp

        self.sim_buffbot()

        if "hp" in self.conf:
            self.set_hp(self.conf["hp"])
            if self.hp == 0:
                self.condition(f"force hp=1")
            else:
                self.condition(f"force hp={self.hp}%")
        else:
            self.set_hp(100)

        for dst_key, prerun in preruns_ss.items():
            prerun(self, dst_key)
        self.prerun()

        self.config_acl()

        self.displayed_att = int(self.base_att * self.mod("att"))

        if self.conf["fleet"]:
            self.condition(f'with {self.conf["fleet"]} other {self.slots.c.name}')

        Event("idle")()
        if "dragonbattle" in self.conf and self.conf["dragonbattle"]:
            self.dragonform.set_dragonbattle()
            self.dragon()

        end, reason = Timeline.run(self.duration)

        self.base_buff.count_team_buff()
        self.dragonform.d_shift_partial_end()
        if not self.alive:
            reason = "death"
            if self.comment:
                self.comment += "; "
            self.comment += f"died at {end:.02f}s"
            end = self.duration

        log("sim", "end", reason)

        self.post_run(end)
        self.logs = copy.deepcopy(g_logs)

        self.slots.c.downgrade_coabs()

        return end

    def post_run(self, end):
        pass

    def set_dacl(self, enable):
        if self.DISABLE_DACL:
            return
        if enable:
            self._dacl.reset(self)
            self._c_acl = self._dacl
        else:
            self._c_acl = self._acl

    def cb_think(self, t):
        if "dumb" in self._think_modes and (now() // self.dumb_cd > self.dumb_count):
            self.dumb_count = now() // self.dumb_cd
            self.last_c = 0
            return self.a_dooodge()

        # log("think", t.dname, "dacl" if self._acl is self._dacl else "acl", "/".join(map(str, (t.pin, t.dstat, t.didx, t.dhit))))

        result = self._c_acl(t)

        # log("think", t.dname, "dacl" if self._acl is self._dacl else "acl", "/".join(map(str, (t.pin, t.dstat, t.didx, t.dhit))), result)

        if not result and t.pin[0] == "x" and isinstance(t.doing, X) and t.didx > 0 and t.doing.status == Action.RECOVERY and t.dhit == 0:
            if self.in_dform():
                dodge = self.dragonform.dx_dodge_or_wait(t.didx)
                if dodge:
                    return dodge()
            elif t.doing.conf["auto_fsf"]:
                return self.fsf()

        return result or self._next_x()

    def think_pin(self, pin):
        # pin as in "signal", says what kind of event happened

        if pin in self.conf.latency:
            latency = self.conf.latency[pin]
        else:
            latency = self.conf.latency.default

        doing = self.action.getdoing()
        self.action._static.pin = pin

        t = Timer(self.cb_think)
        t.pin = pin
        t.dname = doing.name
        t.dstat = doing.status
        t.didx = doing.index
        t.dhit = int(doing.has_delayed)
        t.doing = doing
        t.on(latency)

    def l_silence_end(self, e):
        doing = self.action.getdoing()
        sname = self.Skill._static.s_prev
        if doing.name[0] == "x":
            self.Skill._static.first_x_after_s = 1
        else:
            self.think_pin(sname + "-x")  # best choice
        self.think_pin(sname)
        # if doing.name[0] == 's':
        #   no_deed_to_do_anythin

    # DL uses C floats and round SP up, which leads to precision issues
    @staticmethod
    def sp_convert(haste, sp):
        # FIXME: dum
        return float_ceil(sp, haste)

    def _get_sp_targets(self, target, name, no_autocharge, filter_func=None):
        if target is None:
            targets = self.skills
        if isinstance(target, str):
            try:
                targets = [self.a_s_dict[target]]
            except KeyError:
                return None
        if isinstance(target, (list, tuple)):
            targets = []
            for t in target:
                try:
                    s = self.a_s_dict[t]
                    if s not in targets:
                        targets.append(s)
                except KeyError:
                    continue
        if not filter_func and no_autocharge:
            filter_func = lambda s: not hasattr(s, "autocharge_timer")
        return filter(filter_func, targets)

    # sp = self.sp_convert(self.sp_mod(name), sp)
    def _charge(self, name, sp, sp_func, target=None, no_autocharge=False, dragon_sp=False, show_sp_per_skill=False):
        real_sp = {}
        if self.in_dform() and dragon_sp:
            # dra mode sp
            if target is None:
                targets = self.dskills
            else:
                targets = (self.a_s_dict[target],)
            for s in targets:
                real_sp[s.name] = sp_func(s, name, sp)
            skills = self.dskills
        else:
            # adv mode sp
            targets = self._get_sp_targets(target, name, no_autocharge)
            if not targets:
                return None
            for s in targets:
                real_sp[s.name] = sp_func(s, name, sp)
            skills = self.skills

        if not real_sp:
            return None

        # f"{s.name}:+{sp_func(s, name, sp)}"
        real_sp_counter = Counter(real_sp.values())
        most_common = real_sp_counter.most_common()[0][0]
        charged_sp = f"+{most_common}"
        if show_sp_per_skill and len(real_sp_counter) > 1:
            all_sp_str = []
            for s in skills:
                aspstr = s.sp_str
                real_sp_val = real_sp.get(s.name, most_common)
                if real_sp_val != most_common:
                    aspstr += f" (+{real_sp_val})"
                all_sp_str.append(aspstr)
            all_sp_str = ", ".join(all_sp_str)
        else:
            all_sp_str = ", ".join((s.sp_str for s in skills))
        if target:
            if isinstance(target, list):
                target_str = ",".join(target)
            else:
                target_str = target
            target_str = f"{name}->{target_str}"
        else:
            target_str = name
        return charged_sp, all_sp_str, target_str

    def _add_sp_fn(self, s, name, sp):
        sp = float_ceil(sp, self.sp_mod(name, target=s.name))
        s.charge(sp)
        return sp

    def _prep_sp_fn(self, s, _, percent):
        sp = float_ceil(s.real_sp, percent)
        s.charge(sp)
        return sp

    def charge_p(self, name, percent, target=None, no_autocharge=False, dragon_sp=False):
        percent = percent / 100 if percent > 1 else percent
        result = self._charge(
            name,
            percent,
            self._prep_sp_fn,
            target=target,
            no_autocharge=no_autocharge,
            dragon_sp=dragon_sp,
        )
        if not result:
            return
        _, all_sp_str, target_str = result
        log(
            "sp",
            target_str,
            f"{percent*100:.0f}%",
            all_sp_str,
        )
        if percent >= 1 and target is None:
            self.think_pin("prep")

    def charge(self, name, sp, target=None, dragon_sp=False):
        result = self._charge(
            name,
            sp,
            self._add_sp_fn,
            target=target,
            dragon_sp=dragon_sp,
            show_sp_per_skill=True,
        )
        if not result:
            return
        charged_sp, all_sp_str, target_str = result
        log(
            "sp",
            target_str,
            charged_sp,
            all_sp_str,
        )
        self.think_pin("sp")

    def l_dmg_formula(self, e):
        name = e.dname
        if self.berserk_mode and getattr(e, "dot", False):
            dmg_coef = 0
        else:
            dmg_coef = e.dmg_coef
        if hasattr(e, "dtype"):
            dtype = e.dtype
        else:
            dtype = name
        if hasattr(e, "modifiers"):
            if e.modifiers != None and e.modifiers != 0:
                self.all_modifiers = e.modifiers
        e.dmg = self.dmg_formula(name, dmg_coef, dtype=dtype)
        self.all_modifiers = self.modifier._static.all_modifiers
        e.ret = e.dmg
        return

    def dmg_formula(self, name, dmg_coef, dtype=None):
        dmg_mod = self.dmg_mod(name, dtype=dtype)
        att = self.att_mod(name)
        armor = 10 * self.def_mod()
        ex = self.mod("ex")
        # to allow dragon overriding
        ele = (self.mod(self.element) + 0.5) * (self.mod(f"{self.slots.c.ele}_resist"))
        # log("maffs", name, str(dtype), str((dmg_mod, att, self.base_att, armor, ex, ele)))
        return 5.0 / 3 * dmg_coef * dmg_mod * ex * att * self.base_att / armor * ele  # true formula

    def l_true_dmg(self, e):
        log("dmg", e.dname, e.count, 0, e.comment)

    def l_dmg_make(self, e):
        try:
            return self.dmg_make(e.dname, e.dmg_coef, e.dtype)
        except AttributeError:
            return self.dmg_make(e.dname, e.dmg_coef)

    def l_attenuation(self, t):
        self.add_combo(name=t.dname)
        return self.dmg_make(
            t.dname,
            t.dmg_coef,
            t.dtype,
            hitmods=t.hitmods,
            attenuation=t.attenuation,
            depth=t.depth,
        )

    def dmg_make(self, name, coef, dtype=None, fixed=False, hitmods=None, attenuation=None, depth=0):
        if coef <= 0.01:
            return 0
        if hitmods is not None:
            for m in hitmods:
                m.on()
        count = self.dmg_formula(name, coef, dtype=dtype) if not fixed else coef
        if hitmods is not None:
            for m in hitmods:
                m.off()
        log("dmg", name, count, coef)
        # self.dmg_proc(name, count)
        dmg_made_event = Event("dmg_made")
        dmg_made_event.name = name
        dmg_made_event.count = count
        dmg_made_event.on()
        if fixed:
            return count
        if not self.berserk_mode and self.echo > 1:
            if attenuation is not None:
                rate, pierce, hitmods = attenuation
                echo_count = self.dmg_formula_echo(coef / (rate ** depth))
            else:
                echo_count = self.dmg_formula_echo(coef)
            # self.dmg_proc(name, echo_count)
            dmg_made_event = Event("dmg_made")
            dmg_made_event.name = "echo"
            dmg_made_event.source = name
            dmg_made_event.count = echo_count
            dmg_made_event.on()
            log("dmg", "echo", echo_count, f"from {name}")
            count += echo_count
        if attenuation is not None:
            rate, pierce, hitmods = attenuation
            if pierce != 0:
                coef *= rate
                depth += 1
                if depth == 1:
                    name = f"{name}_extra{depth}"
                else:
                    name = "_".join(name.split("_")[:-1]) + f"_extra{depth}"
                t = Timer(self.l_attenuation)
                t.dname = name
                t.dmg_coef = coef
                t.dtype = dtype
                t.hitmods = hitmods
                t.attenuation = (rate, pierce - 1, hitmods)
                t.depth = depth
                t.on(self.conf.attenuation.delay)
        return count

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None, dtype=None):
        g_logs.log_hitattr(name, attr)
        hitmods = self.actmods(name, base, group, aseq, attr)
        crisis_mod_key = dtype if dtype in self.crisis_mods else None
        if "dmg" in attr:
            if "killer" in attr:
                hitmods.append(KillerModifier(name, "hit", *attr["killer"]))
            if "killer_hitcount" in attr:
                for k in reversed(attr["killer_hitcount"][0]):
                    if self.hits >= k[0]:
                        hitmods.append(KillerModifier(name, "hit", k[1], attr["killer_hitcount"][1]))
                        break
            if "bufc" in attr:
                hitmods.append(Modifier(f"{name}_bufc", "ex", "bufc", attr["bufc"] * self.buffcount))
            if "drg" in attr:
                # base 0.2 + any ability ddamage, no dracolith
                hitmods.append(Modifier(f"{name}_drg", "ex", "dragon", 0.2 + self.mod("da", operator=operator.add, initial=0)))
            if "fade" in attr:
                attenuation = (attr["fade"], self.conf.attenuation.hits, hitmods)
            else:
                attenuation = None
            if self.berserk_mode and "odmg" in attr:
                hitmods.append(Modifier(name, "ex", "odgauge", attr["odmg"] - 1))
            if "crit" in attr:
                hitmods.append(Modifier("hitattr_crit", "crit", "chance", attr["crit"]))
            for m in hitmods:
                m.on()
            if "crisis" in attr:
                self.crisis_mods[crisis_mod_key].set_per_hit(attr["crisis"])
            if "extra" in attr:
                for _ in range(min(attr["extra"], round(self.buffcount))):
                    self.add_combo(name)
                    self.dmg_make(name, attr["dmg"], dtype=dtype, attenuation=attenuation)
            else:
                self.add_combo(name)
                self.dmg_make(name, attr["dmg"], dtype=dtype, attenuation=attenuation)

        if onhit:
            onhit(name, base, group, aseq, dtype)

        if "sp" in attr:
            dragon_sp = base in ("ds1", "ds2") or base.startswith("dfs") or group == globalconf.DRG
            if isinstance(attr["sp"], int):
                value = attr["sp"]
                self.charge(base, value, dragon_sp=dragon_sp)
            else:
                value = attr["sp"][0]
                mode = None if len(attr["sp"]) == 1 else attr["sp"][1]
                target = None if len(attr["sp"]) == 2 else attr["sp"][2]
                if target == "sn":
                    target = base
                charge_f = self.charge
                if mode == "%":
                    charge_f = self.charge_p
                charge_f(base, value, target=target, dragon_sp=dragon_sp)

        if "dp" in attr:
            self.dragonform.charge_dp(name, attr["dp"])

        if "utp" in attr:
            self.dragonform.charge_utp(name, attr["utp"])

        if "hp" in attr:
            try:
                self.add_hp(float(attr["hp"]))
            except TypeError:
                value = attr["hp"][0]
                mode = None if len(attr["hp"]) == 1 else attr["hp"][1]
                if mode == "=":
                    self.set_hp(value)
                elif mode == ">":
                    if self.hp > value:
                        self.set_hp(value)
                elif mode == "%":
                    self.set_hp(self.hp * value)

        if "heal" in attr:
            try:
                self.heal_make(name, float(attr["heal"]))
            except TypeError:
                value = attr["heal"][0]
                target = attr["heal"][1]
                self.heal_make(name, value, target)

        if "afflic" in attr:
            aff_type, aff_args = attr["afflic"][0], attr["afflic"][1:]
            getattr(self.afflics, aff_type).on(name, *aff_args, dtype=dtype)
            if self.conf["fleet"]:
                try:
                    aff_args[1] = 0
                except IndexError:
                    pass
                for _ in range(self.conf["fleet"]):
                    getattr(self.afflics, aff_type).on(name, *aff_args, dtype=dtype)

        if "bleed" in attr:
            from module.bleed import Bleed, mBleed

            try:
                rate, mod, duration = attr["bleed"]
            except ValueError:
                rate, mod = attr["bleed"]
                duration = 30
            rate = max(min(100, rate + self.sub_mod("debuff_rate", "passive") * 100), 0)
            debufftime = self.mod("debuff", operator=operator.add)
            if self.bleed is not None:
                use_mbleed = isinstance(self.bleed, mBleed)
            else:
                use_mbleed = self.conf.mbleed and rate < 100
            if use_mbleed:
                if self.bleed is None:
                    self.bleed = mBleed("init", mod, dtype=dtype)
                    self.bleed.reset()
                self.bleed = mBleed(base, mod, duration=duration, chance=rate / 100, debufftime=debufftime, dtype=dtype)
                self.bleed.on()
            else:
                if self.bleed is None:
                    self.bleed = Bleed("init", mod, dtype=dtype)
                    self.bleed.reset()
                if rate == 100 or rate >= random.uniform(0, 100):
                    self.bleed = Bleed(base, mod, duration=duration, debufftime=debufftime, dtype=dtype)
                    self.bleed.on()

        if "amp" in attr:
            amp_id, amp_max_lvl, amp_target = attr["amp"]
            amp_buff = self.active_buff_dict.get_amp(amp_id)
            amp_buff.on(amp_max_lvl, amp_target, fleet=self.conf["fleet"] or 0)

        # coei: _CurseOfEmptinessInvalid
        if "buff" in attr:
            self.hitattr_buff_outer(name, base, group, aseq, attr)

        if "dispel" in attr:
            self.dispel(attr["dispel"])

        if "relief" in attr:
            self.aff_relief(*attr["relief"])

        if "vars" in attr:
            varname = attr["vars"][0]
            value = attr["vars"][1]
            try:
                limit = attr["vars"][2]
            except IndexError:
                limit = 1
            try:
                old_value = self.__dict__[varname]
                new_value = max(0, min(limit, self.__dict__[varname] + value))
            except KeyError:
                old_value = None
                new_value = value
            if new_value != old_value:
                self.__dict__[varname] = new_value
                log(varname, f"{value:+}", new_value, limit)

        for m in hitmods:
            m.off()
        if crisis_mod_key is not None:
            self.crisis_mods[crisis_mod_key].set_per_hit(None)

    def hitattr_buff_outer(self, name, base, group, aseq, attr):
        bctrl = None
        blist = attr["buff"]
        if self.nihilism and not attr.get("coei"):
            if isinstance(blist[0], list):
                blist = [["team", buff[1], buff[2], "dummy", "zone"] for buff in blist if buff[0] == "zone"]
                if not blist:
                    return
            else:
                if blist[0] != "zone":
                    return
                blist = ["team", blist[1], blist[2], "dummy", "zone"]
        try:
            if blist[-1][0] == "-":
                bctrl = blist[-1]
                blist = blist[:-1]
        except TypeError:
            pass
        if bctrl:
            if bctrl == "-off":
                try:
                    self.active_buff_dict.off(*blist)
                except:
                    pass
                return
            elif bctrl == "-refresh":
                try:
                    return self.active_buff_dict.on(base, group, aseq)
                except KeyError:
                    pass
            elif bctrl == "-replace":
                self.active_buff_dict.off_all(base, aseq)
                try:
                    return self.active_buff_dict.on(base, group, aseq)
                except KeyError:
                    pass
            elif bctrl == "-await":
                try:
                    if not self.active_buff_dict.check(base, group, aseq):
                        return self.active_buff_dict.on(base, group, aseq)
                    return None
                except KeyError:
                    pass
            elif bctrl.startswith("-overwrite"):
                # does not support multi buffs
                try:
                    ow_buff = self.active_buff_dict.get_overwrite(bctrl)
                    v_current = abs(ow_buff.value())
                    d_current = ow_buff.duration
                    v_new = abs(blist[1])
                    d_new = blist[2]
                    if v_new > v_current:
                        ow_buff.off()
                    elif v_new == v_current:
                        if d_new == d_current:
                            ow_buff.on()
                            return
                        else:
                            ow_buff.off()
                    else:
                        return
                except:
                    pass
                buff = self.hitattr_buff(name, base, group, aseq, 0, blist, stackable=False)
                if buff:
                    self.active_buff_dict.add_overwrite(base, group, aseq, buff.on(), bctrl)
                return
        if isinstance(blist[0], list):
            buff_objs = []
            for bseq, attrbuff in enumerate(blist):
                obj = self.hitattr_buff(name, base, group, aseq, bseq, attrbuff, stackable=not bctrl)
                if obj:
                    buff_objs.append(obj)
            if buff_objs:
                self.active_buff_dict.add(base, group, aseq, MultiBuffManager(name, buff_objs).on())
        else:
            buff = self.hitattr_buff(name, base, group, aseq, 0, blist, stackable=not bctrl)
            if buff:
                self.active_buff_dict.add(base, group, aseq, buff.on())

    def hitattr_buff(self, name, base, group, aseq, bseq, attrbuff, stackable=False):
        btype = attrbuff[0]
        if btype in ("energy", "inspiration"):
            is_team = len(attrbuff) > 2 and bool(attrbuff[2])
            if self.conf["fleet"] and is_team:
                getattr(self, btype).add(attrbuff[1] * (self.conf["fleet"] + 1))
            else:
                getattr(self, btype).add(attrbuff[1], team=is_team)
        else:
            bargs = attrbuff[1:]
            bname = f"{name}_{aseq}{bseq}"
            try:
                if self.conf["fleet"] and btype in ("team", "nearby", "zone", "debuff"):
                    for _ in range(self.conf["fleet"] + 1 if stackable else 1):
                        buff = bufftype_dict[btype](bname, *bargs, source=name)
                        buff.bufftype = "self"
                        buff.on()
                    return buff
                else:
                    return bufftype_dict[btype](bname, *bargs, source=name)
            except ValueError:
                return None

    def l_hitattr_make(self, t):
        msl = getattr(t, "msl", 0)
        if msl:
            self.action.getdoing().remove_delayed(t)
            t.msl = 0
            t.on(msl)
        else:
            self.hitattr_make(t.name, t.base, t.group, t.aseq, t.attr, t.onhit, t.dtype)
            if t.pin is not None:
                self.think_pin(f"{t.pin}-h")
                p = Event(f"{t.pin}-h")
                p.is_hit = t.name in self.damage_sources
                p()
            if t.proc is not None:
                t.proc(t)
            if t.actmod:
                self.actmod_off(t)

    ATTR_COND = {
        "hp>": lambda s, v: s.hp > v,
        "hp>=": lambda s, v: s.hp >= v,
        "hp<": lambda s, v: s.hp < v,
        "hp<=": lambda s, v: s.hp <= v,
        "rng": lambda s, v: random.random() <= v if s.FIXED_RNG is None else s.FIXED_RNG,
        "hits": lambda s, v: s.hits >= v,
        "zone": lambda s, v: s.zonecount >= v,
        "var>=": lambda s, v: getattr(s, v[0], 0) >= v[1],
        "var>": lambda s, v: getattr(s, v[0], 0) > v[1],
        "var<=": lambda s, v: getattr(s, v[0], 0) <= v[1],
        "var<": lambda s, v: getattr(s, v[0], 0) < v[1],
        "var=": lambda s, v: getattr(s, v[0], 0) == v[1],
        "var!=": lambda s, v: getattr(s, v[0], 0) != v[1],
        # between 2 values
        "var<<": lambda s, v: v[1] <= getattr(s, v[0], 0) <= v[2],
        "amp": lambda s, v: s.active_buff_dict.check_amp_cond(*v),
    }

    def eval_attr_cond(self, cond):
        try:
            return Adv.ATTR_COND[cond[0]](self, cond[1])
        except KeyError:
            if cond[0] == "not":
                return not self.eval_attr_cond(cond[1])
            if cond[0] == "and":
                return all((self.eval_attr_cond(subcond) for subcond in cond[1:]))
            if cond[0] == "or":
                return any((self.eval_attr_cond(subcond) for subcond in cond[1:]))

    def do_hitattr_make(self, e, aseq, attr, pin=None):
        if "cond" in attr and not self.eval_attr_cond(attr["cond"]):
            return

        if "cd" in attr and self.is_set_cd((e.base, aseq), attr["cd"]):
            return

        spd = self.speed()
        iv = attr.get("iv", 0) / spd
        msl = attr.get("msl", 0)
        if attr.get("msl_spd"):
            msl /= spd
        try:
            onhit = getattr(self, f"{e.name}_hit{aseq+1}")
        except AttributeError:
            onhit = None
        if iv > 0 or msl > 0:
            mt = Timer(self.l_hitattr_make)
            mt.pin = pin
            mt.name = e.name
            mt.dtype = e.dtype
            mt.base = e.base
            mt.group = e.group
            try:
                mt.index = e.index
            except AttributeError:
                pass
            try:
                mt.level = e.level
            except AttributeError:
                pass
            mt.aseq = aseq
            mt.attr = attr
            mt.onhit = onhit
            mt.proc = None
            mt.actmod = False
            if msl and not iv:
                mt.on(msl)
            else:
                mt.msl = msl
                mt.on(iv)
                self.action.getdoing().add_delayed(mt)
            return mt
        else:
            e.pin = pin
            e.aseq = aseq
            e.attr = attr
            self.hitattr_make(e.name, e.base, e.group, aseq, attr, onhit, e.dtype)
            if pin is not None:
                p = Event(f"{pin}-h")
                p.is_hit = e.name in self.damage_sources
                p()
        return None

    @staticmethod
    def compare_mt(mt_a, mt_b):
        if mt_a is None:
            return mt_b
        if mt_b is None:
            return mt_a
        if (mt_a.timing + getattr(mt_a, "msl", 0)) >= (mt_b.timing + getattr(mt_b, "msl", 0)):
            return mt_a
        else:
            return mt_b

    def schedule_hits(self, e, conf, pin=None):
        final_mt = None
        if conf["attr"]:
            prev_attr = None
            for aseq, attr in enumerate(conf["attr"]):
                if isinstance(attr, str):
                    attr = getattr(self, attr, 0)
                if prev_attr is not None and isinstance(attr, int):
                    for repeat in range(1, attr):
                        res_mt = self.do_hitattr_make(e, aseq + repeat, prev_attr, pin=pin)
                else:
                    res_mt = self.do_hitattr_make(e, aseq, attr, pin=pin)
                    prev_attr = attr
                final_mt = self.compare_mt(res_mt, final_mt)
        return final_mt

    def hit_make(self, e, conf, cb_kind=None, pin=None, actmod=True):
        cb_kind = cb_kind or e.name
        try:
            getattr(self, f"{cb_kind}_before")(e)
        except AttributeError:
            pass
        final_mt = self.schedule_hits(e, conf, pin=pin)
        proc = getattr(self, f"{cb_kind}_proc", None)
        if final_mt is not None:
            final_mt.actmod = actmod
            final_mt.proc = proc
        else:
            if proc:
                proc(e)
            if actmod:
                self.actmod_off(e)
        self.think_pin(pin or e.name)

    def dispel(self, rate=100):
        # assume 100 rate for now
        self.dispel_event()

    def aff_relief(self, affs, rate=100):
        # assume 100 rate for now
        type = set(affs)
        if "all" in type:
            type = set(AFFLICT_LIST)
        affs = [buff for buff in self.all_buffs if buff.name in type]
        if len(affs) > 0:
            self.aff_relief_event()
            for aff in affs:
                aff.off()

    def l_fs(self, e):
        prev = self.action.getprev().name
        log("cast", e.base if e.group in (globalconf.DEFAULT, globalconf.DRG) else e.name, f"after {prev}")
        self.actmod_on(e)
        self.hit_make(e, self.conf[e.name], pin=e.name.split("_")[0])

    def l_s(self, e):
        self.actmod_on(e)
        if e.name in self.buff_sources:
            self.buffskill_event()
        prev = self.action.getprev().name
        if e.name[0] == "d":
            skills = self.dskills
        else:
            skills = self.skills
        log(
            "cast",
            e.base if e.group in (globalconf.DEFAULT, globalconf.DRG) else e.name,
            f"after {prev}",
            ", ".join([s.sp_str for s in skills]),
        )
        self.hit_make(e, self.conf[e.name], cb_kind=e.base)

    def l_repeat(self, e):
        self.actmod_on(e)
        if e.end:
            if self.conf[e.name].repeat["attr_release"]:
                for aseq, attr in enumerate(self.conf[e.name].repeat["attr_release"]):
                    self.do_hitattr_make(e, aseq, attr, pin=e.name.split("_")[0])
        else:
            self.hit_make(e, self.conf[e.name].repeat, pin=e.name.split("_")[0])

    @allow_acl
    def c_fs(self, group):
        if self.current_fs == group and self.alt_fs_buff is not None:
            return self.alt_fs_buff.uses
        return 0

    @allow_acl
    def c_x(self, group):
        return self.current_x == group

    @allow_acl
    def c_s(self, seq, group):
        return self.current_s[f"s{seq}"] == group

    @property
    def dgauge(self):
        try:
            return self.dragonform.utp_gauge
        except AttributeError:
            return self.dragonform.dragon_gauge

    @property
    def dshift_count(self):
        return g_logs.shift_count

    @property
    def dshift_timeleft(self):
        return self.dragonform.shift_end_timer.timeleft()

    @property
    def bleed_stack(self):
        try:
            return self.bleed._static["stacks"]
        except AttributeError:
            return 0

    @allow_acl
    def bleed_timeleft(self, stack=3):
        try:
            # only available for rng bleed
            return self.bleed.timeleft(stack=stack)
        except AttributeError:
            return 0

    @allow_acl
    def aff(self, afflictname=None):
        if not afflictname:
            return any([getattr(self.afflics, afflictname).get() for afflictname in AFFLICT_LIST])
        return getattr(self.afflics, afflictname).get()

    @allow_acl
    def aff_timeleft(self, afflictname):
        return getattr(self.afflics, afflictname).timeleft()

    @allow_acl
    def buff(self, *args):
        return self.active_buff_dict.check(*args)

    @allow_acl
    def timeleft(self, *args):
        return self.active_buff_dict.timeleft(*args)

    def stop(self):
        doing = self.action.getdoing()
        if doing.status == Action.RECOVERY or doing.status == Action.OFF:
            Timeline.stop()
            return True
        return False
