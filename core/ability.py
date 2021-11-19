### Conditions
from core.modifier import Modifier


class Cond:
    def __init__(self, adv) -> None:
        self._adv = adv
        self.moment = False

    def get(self):
        return 1


### Sub Abilities
class Ab:
    def __init__(self, adv, cond) -> None:
        self._adv = adv
        self._cond = cond

    def on(self, e):
        pass

    def off(self, e):
        pass


class Mod(Ab):
    def __init__(self, adv, cond, *args) -> None:
        super().__init__(adv, cond)
        self.modifier = Modifier(str(cond, args), args[1], "passive", args[0], None if self._cond is None else self._cond.get)


### Controller
class Ability:
    def __init__(self, adv, data):
        self._adv = adv
