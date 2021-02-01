from core.advbase import *
from core.acl import CONTINUE

class Sophie_Persona(Adv):
    def prerun(self):
        self.pithos_t = Timer(self.pithos_dmg, 5.23, 1)
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(
            group='ddrive',
            buffs=[EffectBuff('pithos', -1, self.pithos_t.on, self.pithos_t.off)],
            x=True, fs=True, s1=True, s2=True
        ), drain=75)

        self.current_x = 'default'
        self.deferred_x = 'ex'
        Event('s').listener(self.reset_to_default, order=0)
        Event('dragondrive').listener(self.reset_to_default, order=0)
        Event('dragondrive_end').listener(self.reset_to_default, order=0)

    def pithos_dmg(self, _):
        self.dmg_make('x_pithos', 6.23)

    def reset_to_default(self, e):
        self.current_x = 'ddrive' if self.dragonform.dragondrive_buff.get() else 'default'

    @allow_acl
    def norm(self):
        base_x = 'ddrive' if self.dragonform.dragondrive_buff.get() else 'default'
        if self.current_x != base_x and isinstance(self.action.getdoing(), X):
            self.deferred_x = base_x
        return CONTINUE

    @allow_acl
    def ex(self):
        base_x = 'ddrive' if self.dragonform.dragondrive_buff.get() else 'default'
        ex_x = 'ddriveex' if self.dragonform.dragondrive_buff.get() else 'ex'
        if self.current_x == base_x and isinstance(self.action.getdoing(), X):
            self.deferred_x = ex_x
        return CONTINUE

    def check_deferred_x(self):
        pass

    def x(self, x_min=1):
        base_x = 'ddrive' if self.dragonform.dragondrive_buff.get() else 'default'
        ex_x = 'ddriveex' if self.dragonform.dragondrive_buff.get() else 'ex'
        prev = self.action.getprev()
        if isinstance(prev, X) and (prev.group == self.current_x or ex_x in (prev.group, self.current_x)):
            if self.deferred_x is not None:
                log('deferred_x', self.deferred_x)
                self.current_x = self.deferred_x
                self.deferred_x = None
            if prev.index < self.conf[prev.group].x_max:
                x_next = self.a_x_dict[self.current_x][prev.index+1]
            else:
                x_next = self.a_x_dict[self.current_x][x_min]
            if x_next.enabled:
                return x_next()
            else:
                self.current_x = base_x
        return self.a_x_dict[self.current_x][x_min]()

variants = {None: Sophie_Persona}
