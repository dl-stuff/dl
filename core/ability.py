import operator

from core.modifier import Modifier
from core.timeline import Event, Listener

OPS = {
    ">=": operator.ge,
    "<=": operator.le,
    "=": operator.eq,
    "<": operator.lt,
    ">": operator.gt,
}

### Conditions

CONDITONS = {}


class Cond:
    def __init__(self, adv, *args) -> None:
        self._adv = adv
        self.event = None

    def get(self):
        return 1

    def check(self, e):
        return True

    def listener(self, callback, order=1):
        def _checked_callback(self, e):
            if self.check(e):
                callback(e)

        return Listener(self.event, _checked_callback, order=order)


class CompareCond(Cond):
    def __init__(self, event, adv, *args) -> None:
        super().__init__(adv, *args)
        self._op = OPS[args[0]]
        self.value = args[1]
        try:
            if bool(args[2]):
                self.event = event
        except IndexError:
            pass

    def check(self, e):
        return self.get()


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


class CondBuffedBy(Cond):
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
        self.target = args[0]
        self.event = "s"

    def check(self, e):
        return e.base == self.target


CONDITONS["buffedby"] = CondBuffedBy


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


class CondEvent(Cond):
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
        self.event = args[0]


CONDITONS["event"] = CondEvent


class CondSlayer(Cond):
    def __init__(self, adv, *args) -> None:
        super().__init__(adv, *args)
        self.event = "slayed"
        self.threshold = args[0]
        self.count = 0
        # self.target = args[-1]

    def check(self, e):
        if (e.count + self.count) < self.threshold:
            self.count += e.count
            return False
        else:
            e.count += self.count
            return True


CONDITONS["slayer"] = CondSlayer


# ac_ABNORMAL_STATUS
# ac_TENSION_MAX, ac_TENSION_MAX_MOMENT
# ac_DEBUFF_SLIP_HP
# ac_SP1_OVER

### Sub Abilities
SUB_ABILITIES = {}


class Ab:
    def __init__(self, adv, cond, *args) -> None:
        self._adv = adv
        self._cond = cond
        self._cond_get = None if self._cond is None else self._cond.get


class AbModifier(Ab):
    def __init__(self, adv, cond, value, mtype, morder) -> None:
        super().__init__(adv, cond)
        self.modifier = Modifier(mtype, morder, value, self._cond_get)


class AbMod(AbModifier):
    def __init__(self, adv, cond, *args) -> None:
        super().__init__(adv, cond, args[0], args[1], "passive")


SUB_ABILITIES["mod"] = AbMod


class AbActdmg(AbModifier):
    def __init__(self, adv, cond, *args) -> None:
        print(adv, cond, *args)
        try:
            self.target = args[1].replace("-t:", "")
            super().__init__(adv, cond, args[0], self.target, "passive")
        except IndexError:
            self.target = "act"
            if isinstance(self._cond, CondOverdrive):
                super().__init__(adv, cond, args[0], "killer", "passive")
            if self._cond is None:
                super().__init__(adv, cond, args[0], self.target, "passive")
            else:
                super().__init__(adv, cond, args[0], self.target, str(self._cond.__class__.__name__))


SUB_ABILITIES["actdmg"] = AbActdmg


class AbCtime(AbModifier):
    def __init__(self, adv, cond, *args) -> None:
        super().__init__(adv, cond, args[0], "ctime", "passive")


### Ability
class Ability:
    def __init__(self, adv, data):
        self._adv = adv
        self.cond = None
        if cond := data.get("cond"):
            try:
                print(cond)
                self.cond = CONDITONS[cond[0]](*cond[1:])
            except KeyError:
                self.cond = None
        self.abs = []
        if ab_lst := data.get("ab"):
            for ab in ab_lst:
                try:
                    self.abs.append(SUB_ABILITIES[ab[0]](adv, self.cond, *ab[1:]))
                except KeyError:
                    pass
