import operator

from core.modifier import Modifier
from core.timeline import Event, Listener, Timer
from conf import float_ceil
from core.log import log

OPS = {
    ">=": operator.ge,
    "<=": operator.le,
    "=": operator.eq,
    "<": operator.lt,
    ">": operator.gt,
}


class InactiveAbility(Exception):
    pass


### Conditions

CONDITONS = {}


class Cond:
    def __init__(self, adv, *args) -> None:
        self._adv = adv
        self.event = None
        self.cooldown = None

    def set_cooldown(self, cd):
        self.cooldown = Timer(timeout=cd - 0.0001)

    def get(self):
        return 1

    def check(self, e):
        return True

    def listener(self, callback, order=1):
        if self.cooldown is not None:

            def _checked_callback(e):
                if not self.cooldown.online and self.check(e):
                    callback(e)

        else:

            def _checked_callback(e):
                if self.check(e):
                    callback(e)

        return Listener(self.event, _checked_callback, order=order)


class CompareCond(Cond):
    def __init__(self, event, adv, *args) -> None:
        super().__init__(adv, *args)
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
    def __init__(self, adv, *args) -> None:
        super().__init__("hp", adv, *args)

    def get(self):
        return self._op(self._adv.hp, self.value)


CONDITONS["hp"] = CondHP


class CondHits(CompareCond):
    def __init__(self, adv, *args) -> None:
        super().__init__("hits", adv, *args)

    def get(self):
        return self._op(self._adv.hits, self.value)


CONDITONS["hits"] = CondHits


class CondActcond(CompareCond):
    def __init__(self, adv, *args) -> None:
        super().__init__("actcond", adv, *args[1:])
        self.actcond_id = args[0]

    def get(self):
        return self._op(sum((int(actcond_id == self.actcond_id) for actcond_id, _ in self._adv.active_actconds)), self.value)


CONDITONS["actcond"] = CondActcond


class CondBuffedBy(Cond):
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
        self.target = args[0]
        self.event = "s"

    def check(self, e):
        return e.base == self.target


CONDITONS["buffed_by"] = CondBuffedBy


class CondShift(Cond):
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
        if args[0] == "dform":
            self.form_check = self._adv.dragonform.in_dform
        elif args[0] == "ddrive":
            self.form_check = self._adv.dragonform.in_ddrive

    def get(self):
        return self.form_check()


CONDITONS["shift"] = CondShift


class CondBreak(Cond):
    def get(self):
        return 0.15


CONDITONS["break"] = CondBreak


class CondOverdrive(Cond):
    def get(self):
        return 0.35


CONDITONS["overdrive"] = CondOverdrive


class CondBleed(Cond):
    def get(self):
        return self._adv.bleed.get()


CONDITONS["bleed"] = CondBleed


class CondEvent(Cond):
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
        self.event = args[0]


CONDITONS["event"] = CondEvent


class CondPersistentCount(Cond):
    def __init__(self, event, adv, *args) -> None:
        super().__init__(adv, *args)
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
    def __init__(self, adv, *args) -> None:
        super().__init__("hits", adv, *args)


CONDITONS["hitcount"] = CondHitsEvent


class CondSlayer(CondPersistentCount):
    def __init__(self, adv, *args) -> None:
        super().__init__("slayer", adv, *args)


CONDITONS["slayer"] = CondSlayer


class CondAffProc(Cond):
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
        self.event = args[0]


CONDITONS["aff"] = CondAffProc


class CondMult(Cond):
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
        self.value = args[0]
        self.threshold = args[1]
        self.max_count = args[2]

    def get(self):
        return min(self.max_count, getattr(self._adv, self.value, 0) // self.threshold)


CONDITONS["mult"] = CondMult


class CondGetDP(Cond):
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
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
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
        self.event = "actcond"

    def check(self, e):
        if e.actcond.is_doublebuff:
            log("doublebuff", e.source[0])
        return e.actcond.is_doublebuff


CONDITONS["doublebuff"] = CondDoublebuff


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
        try:
            self.target = args[1].replace("-t:", "")
            if len(args) == 3:
                super().__init__(adv, ability, args[0], self.target, args[2])
            else:
                super().__init__(adv, ability, args[0], self.target, "passive")
        except IndexError:
            self.target = "act"
            if isinstance(ability.cond, (CondOverdrive, CondBleed)):
                super().__init__(adv, ability, args[0], "killer", "passive")
            elif isinstance(ability.cond, CondBreak):
                super().__init__(adv, ability, args[0], "killer", "break")
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
            self.l_cond = self._cond.listener(self._actcond_on)

    def _actcond_on(self, e):
        if e.name == "actcond":
            source = e.source or ("ability", -1)
            dtype = e.dtype or "#"
        else:
            source = ("ability", -1)
            dtype = "#"
        self._adv.actcond_make(self.actcond_list[self.idx], self.target, source, dtype=dtype, ev=getattr(e, "ev", 1))
        self.idx = (self.idx + 1) % len(self.actcond_list)
        if self.max_count is not None:
            self.count += 1
            if self.count > self.max_count:
                self.l_cond.off()


SUB_ABILITIES["actcond"] = AbActcond


class AbHitattr(Ab):
    def __init__(self, adv, ability, *args) -> None:
        super().__init__(adv, ability)
        self.hitattr = args[0]
        self.max_count = ability.data.get("count")
        self.count = 0
        self.l_cond = None
        if self._cond is not None:
            self.l_cond = self._cond.listener(self._actcond_on)

    def _actcond_on(self, e):
        self._adv.hitattr_make("ab", "ab", "default", 1, self.hitattr, ev=getattr(e, "ev", 1))
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
            self.l_cond = self._cond.listener(self._dprep)

    def _dprep(self, e):
        self._adv.dragonform.charge_dprep(self.value)


SUB_ABILITIES["dprep"] = AbDragonPrep


class AbDragonPrepCap(Ab):
    def __init__(self, adv, ability, *args) -> None:
        super().__init__(adv, ability, *args)
        self.value = args[0]
        if self._cond is not None:
            self.l_cond = self._cond.listener(self._dprep_max, order=2)

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
                self.cond = CONDITONS[cond[0]](adv, *cond[1:])
                if cd := data.get("cd"):
                    self.cond.set_cooldown(cd)
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
