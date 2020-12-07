from core.advbase import *

class Ezelith(Adv):
    def prerun(self):
        self.a1_hits = 0
        # for h in range(1, 12):
        #     setattr(self, f's1_hit{h}', self.s1_hit)
        self.s2_debuff = Debuff('s2_ab', 0.0, 20, 0).on()
        self.s2_states = {None: 1.0}
        self.a1_debuff_rate_mod = Modifier('a1_debuff_rate', 'debuff_rate', 'passive', 0.2)

    # def s1_hit(self, name, base, group, aseq):
    #     self.a1_hits += 1
    #     if self.a1_hits % 2 == 0:
    #         Selfbuff('a1',0.2,7,'crit','chance').on()

    def add_combo(self, name='#'):
        result = super().add_combo(name=name)
        if self.hits >= 15:
            self.a1_debuff_rate_mod.on()
        else:
            self.a1_debuff_rate_mod.off()
        if name.startswith('s1'):
            for _ in range(self.echo):
                self.a1_hits += 1
                if self.a1_hits % 2 == 0:
                    Selfbuff('a1_crit', 0.2, 7, 'crit', 'chance').on()
        return result

    def x_proc(self, e):
        if self.buff('s2'):
            new_states = defaultdict(lambda: 0.0)
            t = now()
            chance = 0.35
            miss = 1 - chance
            duration = 5 * self.mod('debuff', operator=operator.add)
            for end, rate in self.s2_states.items():
                if end is not None and end < t:
                    end = None
                new_states[t+duration] += chance * rate
                new_states[end] += miss * rate
            new_states[None] += 1 - sum(new_states.values())
            mrate = 1 - new_states[None]
            self.s2_debuff.value(newvalue=-0.1, newchance=mrate)
            self.s2_debuff.on()
            self.s2_states = new_states

variants = {None: Ezelith}
