import operator

from core.modifier import Modifier
from core.timeline import Event, Listener, Timer
from conf import float_ceil, OPS
from core.log import log


class InactiveAbility(Exception):
    pass


### Conditions

CONDITONS = {}


class Cond:
    def __init__(self, adv, data, *args) -> None:
        self._adv = adv
        self.event = None
        self._extra_checks = []
        if cd := data.get("cd"):
            self._cooldown = Timer(timeout=cd - 0.0001)
            self._extra_checks.append(self.not_cooldown)
        if actcond := data.get("actcond"):
            self._actcond_id = actcond
            self._extra_checks.append(self.has_actcond)

    def not_cooldown(self):
        if not self._cooldown.online:
            self._cooldown.on()
            return True
        return False

    def has_actcond(self):
        return self._adv.active_actconds.stacks(self.actcond_id) > 0

    def get(self):
        return 1

    def check(self, e):
        return True

    def trigger(self, callback, order=1):
        if self.event is not None:

            def _checked_callback(e):
                if all((ec() for ec in self._extra_checks)) and self.check(e):
                    callback(e)

            return Listener(self.event, _checked_callback, order=order)


CONDITONS["always"] = Cond


class CompareCond(Cond):
    def __init__(self, event, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        self._op = OPS[args[0]]
        self.value = args[1]
        self.event = event
        try:
            self.moment = bool(args[2])
        except IndexError:
            self.moment = False
        self.current_state = False

    def check(self, e):
        # check is true only when here is a change from current state
        new_state = self.get()
        result = self.current_state != new_state
        self.current_state = new_state
        return result


class CondHP(CompareCond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__("hp", adv, data, *args)

    def get(self):
        return self._op(self._adv.hp, self.value)


CONDITONS["hp"] = CondHP


class CondHits(CompareCond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__("hits", adv, data, *args)

    def get(self):
        return self._op(self._adv.hits, self.value)


CONDITONS["hits"] = CondHits


class CondActcond(CompareCond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__("actcond", adv, data, *args[1:])
        self.actcond_id = args[0]

    def get(self):
        return self._op(self._adv.active_actconds.stacks(self.actcond_id), self.value)


CONDITONS["actcond"] = CondActcond


class CondBuffedBy(Cond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        self.target = args[0]
        self.event = "s"

    def check(self, e):
        return e.base == self.target


CONDITONS["buffed_by"] = CondBuffedBy


class CondShift(Cond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        if args[0] == "dform":
            self.form_check = self._adv.dragonform.in_dform
        elif args[0] == "ddrive":
            self.form_check = self._adv.dragonform.in_ddrive

    def get(self):
        return self.form_check()


CONDITONS["shift"] = CondShift


class CondEvent(Cond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        self.event = args[0]


CONDITONS["event"] = CondEvent


class CondPersistentCount(Cond):
    def __init__(self, event, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        self.event = event
        self.threshold = args[0]
        self.count = 0
        self.target = None
        if len(args) > 1:
            self.target = args[1]

    def check(self, e):
        if self.target is not None and not e.name.startswith(self.target):
            return False
        self.count += e.count
        if self.count < self.threshold:
            return False
        else:
            self.count -= self.threshold
            return True


class CondHitsEvent(CondPersistentCount):
    def __init__(self, adv, data, *args) -> None:
        super().__init__("hits", adv, data, *args)


CONDITONS["hitcount"] = CondHitsEvent


class CondSlayer(CondPersistentCount):
    def __init__(self, adv, data, *args) -> None:
        super().__init__("slayer", adv, data, *args)


CONDITONS["slayer"] = CondSlayer


class CondAffProc(Cond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        self.event = "aff"
        self.aff = args[0]

    def check(self, e):
        return e.atype == self.aff


CONDITONS["aff"] = CondAffProc


class CondSelfAff(CondAffProc):
    def __init__(self, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        self.event = "selfaff"


CONDITONS["selfaff"] = CondSelfAff


class CondMult(Cond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        self.value = args[0]
        self.threshold = args[1]
        self.max_count = args[2]

    def get(self):
        return min(self.max_count, getattr(self._adv, self.value, 0) // self.threshold)


CONDITONS["mult"] = CondMult


class CondGetDP(Cond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        self.event = "dp"
        self.threshold = args[0]
        self.cache = 0

    def check(self, e):
        self.cache += e.value
        if self.cache > self.threshold:
            self.cache = self.cache % self.threshold
            return True
        return False


CONDITONS["get_dp"] = CondGetDP


class CondDoublebuff(Cond):
    def __init__(self, adv, data, *args) -> None:
        super().__init__(adv, data, *args)
        self.event = "actcond"

    def check(self, e):
        if e.actcond.is_doublebuff:
            log("doublebuff", e.source[0])
        return e.actcond.is_doublebuff


CONDITONS["doublebuff"] = CondDoublebuff


class CondFSHold(Cond):
    # def update_gozu_tenno_buff(self, t):
    #     # will ignore cd of 15s for qol reasons
    #     self.adv.gozu_tenno_buff.on(30)

    # def oninit(self, adv):
    #     super().oninit(adv)
    #     adv.gozu_tenno_buff = adv.Selfbuff("gozu_tenno_buff", 0.3, 30, "flame", "ele").no_bufftime()

    #     self.fs_charging_timer = Timer(self.update_gozu_tenno_buff, 3.0 - 0.00001, True)

    #     Event("fs_start").trigger(lambda _: self.fs_charging_timer.on(), order=0)
    #     Event("fs_end").trigger(lambda _: self.fs_charging_timer.off(), order=0)

    def __init__(self, adv, data, *args) -> None:
        self.required_time = args[0]
        if self.required_time == "cd":
            self.required_time = data["cd"]
            del data["cd"]
        super().__init__(adv, data, *args)
        self.event = args[1]

    def trigger(self, callback, order=1):
        def _checked_callback(e):
            if all((ec() for ec in self._extra_checks)) and self.check(e):
                callback(e)

        fs_charging_timer = Timer(_checked_callback, self.required_time - 0.00001, True)
        fs_charging_timer.name = "fs"
        Listener("fs_start", lambda _: fs_charging_timer.on())
        Listener(self.event, lambda _: fs_charging_timer.off())


CONDITONS["fs_hold"] = CondFSHold


### Sub Abilities
SUB_ABILITIES = {}


class Ab:
    def __init__(self, adv, ability, *args) -> None:
        self._adv = adv
        self._ability = ability
        self._cond = ability.cond
        self._cond_get = None if self._cond is None else self._cond.get


class AbModifier(Ab):
    def __init__(self, adv, ability, value, mtype, morder) -> None:
        super().__init__(adv, ability)
        self.modifier = Modifier(mtype, morder, value, self._cond_get)


class AbMod(AbModifier):
    def __init__(self, adv, ability, *args) -> None:
        if len(args) == 3:
            super().__init__(adv, ability, args[0], args[1], args[2].replace("-t:", ""))
        else:
            super().__init__(adv, ability, args[0], args[1], "passive")


SUB_ABILITIES["mod"] = AbMod


class AbActdmg(AbModifier):
    def __init__(self, adv, ability, *args) -> None:
        self.target = args[1].replace("-t:", "")
        if len(args) == 3:
            super().__init__(adv, ability, args[0], self.target, args[2])
        else:
            super().__init__(adv, ability, args[0], self.target, "passive")


SUB_ABILITIES["actdmg"] = AbActdmg


class AbCtime(AbModifier):
    def __init__(self, adv, ability, *args) -> None:
        super().__init__(adv, ability, args[0], "ctime", "passive")


SUB_ABILITIES["ctime"] = AbCtime


class AbActcond(Ab):
    def __init__(self, adv, ability, *args) -> None:
        super().__init__(adv, ability)
        self.target = args[0]
        self.actcond_list = args[1:]
        self.max_count = ability.data.get("count")
        self.count = 0
        self.idx = 0
        self.l_cond = None
        if self._cond is not None:
            self.l_cond = self._cond.trigger(self._actcond_on)

    def _actcond_on(self, e):
        if e.name == "actcond":
            source = (e.source[0], None) or ("ability", None)
            dtype = e.dtype or "#"
        else:
            source = ("ability", None)
            dtype = "#"
        self._adv.actcond_make(self.actcond_list[self.idx], self.target, source, dtype=dtype, ev=getattr(e, "ev", 1))
        self.idx = (self.idx + 1) % len(self.actcond_list)
        if self.max_count is not None:
            self.count += 1
            if self.count > self.max_count and self.l_cond:
                self.l_cond.off()


SUB_ABILITIES["actcond"] = AbActcond


class AbHitattr(Ab):
    def __init__(self, adv, ability, *args) -> None:
        super().__init__(adv, ability)
        self.hitattrs = args
        self.max_count = ability.data.get("count")
        self.count = 0
        self.l_cond = None
        if self._cond is not None:
            self.l_cond = self._cond.trigger(self._actcond_on)

    def _actcond_on(self, e):
        for aseq, hitattr in enumerate(self.hitattrs):
            self._adv.hitattr_make("ab", "ab", "default", aseq, hitattr, ev=getattr(e, "ev", 1))
        if self.max_count is not None:
            self.count += 1
            if self.count > self.max_count:
                self.l_cond.off()


SUB_ABILITIES["hitattr"] = AbHitattr


class AbDragonPrep(Ab):
    def __init__(self, adv, ability, *args) -> None:
        super().__init__(adv, ability, *args)
        self.value = args[0]
        if self._cond is not None:
            self.l_cond = self._cond.trigger(self._dprep)

    def _dprep(self, e):
        self._adv.dragonform.charge_dprep(self.value)


SUB_ABILITIES["dprep"] = AbDragonPrep


class AbDragonPrepCap(Ab):
    def __init__(self, adv, ability, *args) -> None:
        super().__init__(adv, ability, *args)
        self.value = args[0]
        if self._cond is not None:
            self.l_cond = self._cond.trigger(self._dprep_max, order=2)

    def _dprep_max(self, e):
        self._adv.dragonform.dragon_gauge = min(float_ceil(self._adv.dragonform.max_dragon_gauge, self.value), self._adv.dragonform.dragon_gauge)


SUB_ABILITIES["dprep_cap"] = AbDragonPrepCap


### Ability
class Ability:
    def __init__(self, adv, data, use_limit=False):
        self._adv = adv
        self.cond = None
        self.data = data
        if cond := data.get("cond"):
            try:
                self.cond = CONDITONS[cond[0]](adv, data, *cond[1:])
            except KeyError:
                print(cond)
                self.cond = None
        self.abs = []
        if ab_lst := data.get("ab"):
            for ab in ab_lst:
                try:
                    sub_ab = SUB_ABILITIES[ab[0]](adv, self, *ab[1:])
                except KeyError:
                    continue
                if use_limit and isinstance(sub_ab, AbModifier):
                    sub_ab.modifier.limit_group = data.get("lg")
                self.abs.append(sub_ab)


def make_ability(adv, data, use_limit=False):
    if not data.get("ele", adv.slots.c.ele) == adv.slots.c.ele or not data.get("wt", adv.slots.c.wt) == adv.slots.c.wt:
        return None
    return Ability(adv, data, use_limit=use_limit)
