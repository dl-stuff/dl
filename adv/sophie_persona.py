from core.advbase import *
from module.template import Adv_INFUTP
from conf import DEFAULT
from core.acl import CONTINUE


class Sophie_Persona(Adv):
    def prerun(self):
        self.pithos_t = Timer(self.pithos_dmg, 5.23, 1)

        self.current_x = DEFAULT
        self.deferred_x = "ex"
        Event("dragondrive").listener(lambda e: self.pithos_t.on(), order=0)
        Event("dragondrive_end").listener(lambda e: self.pithos_t.off(), order=0)

    def pithos_dmg(self, _):
        self.dmg_make("x_pithos", 6.23, dtype="x")

    @allow_acl
    def norm(self):
        if self.current_x != DEFAULT and isinstance(self.action.getdoing(), X):
            self.deferred_x = DEFAULT
        return CONTINUE

    @allow_acl
    def ex(self):
        if self.current_x != "ex" and isinstance(self.action.getdoing(), X):
            self.deferred_x = "ex"
        return CONTINUE

    def _next_x(self):
        if self.current_x == "ex" and not isinstance(self.action.getdoing(), X):
            self.current_x = DEFAULT
        return super()._next_x()


class Sophie_Persona_INFUTP(Sophie_Persona, Adv_INFUTP):
    pass


variants = {None: Sophie_Persona, "INFUTP": Sophie_Persona_INFUTP}
