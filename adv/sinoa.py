from core.advbase import *

class Sinoa(Adv):
    S1_DURATIONS = (15, 15, 10)
    def prerun(self):
        self.s1_states = {(None, None, None, None): 1}
        self.combined_states = None

        self.dmg_test_event = Event('dmg_formula')
        self.dmg_test_event.dmg_coef = 1
        self.dmg_test_event.dname = 'test'
        self.s1_buffcount = 0

        self.defchain = Event('defchain')
        self.t_doublebuff = 0

        Event('idle').listener(self.s1_combine_after_s, order=0)

    def s1_combine_after_s(self, e):
        prev = self.action.getprev()
        if prev.name in ('s3', 's4'):
            self.s1_combine()

    @staticmethod
    def s1_prune(n_t, tpl):
        if not tpl:
            return None
        return tuple(s_t for s_t in tpl if s_t > n_t) or None

    def s1_expire(self, t):
        n_t = now()
        new_states = defaultdict(lambda: 0)
        for state, state_p in self.s1_states.items():
            n_state = (
                Sinoa.s1_prune(n_t, state[0]),
                Sinoa.s1_prune(n_t, state[1]),
                Sinoa.s1_prune(n_t, state[2]),
                state[3]
            )
            new_states[n_state] += state_p
        new_states[(None, None, None, None)] += 1 - sum(new_states.values())
        self.s1_states = new_states
        self.s1_combine()

    def s1_proc(self, e):
        if e.name != 's1':
            # use RNG variant when shared
            return Teambuff(e.name, *random.choice((
                (0.25, 15.0, 'att', 'buff'),
                (0.25, 15.0, 'defense', 'buff'),
                (0.25, 10.0, 'crit', 'chance'),
                (0.15, -1, 'maxhp', 'buff')
            ))).on()

        n_t = now()
        bt = self.mod('buff', operator=operator.add)
        new_states = defaultdict(lambda: 0)
        db_rate = 0
        for dt in set(Sinoa.S1_DURATIONS):
            Timer(self.s1_expire).on(dt*bt)
        for state, state_p in self.s1_states.items():
            for i in range(3):
                t_expire = n_t + Sinoa.S1_DURATIONS[i] * bt
                if state[i] is None:
                    n_times = (t_expire,)
                else:
                    n_times = (t_expire, *state[i])
                n_state = state[:i] + (n_times,) + state[i+1:]
                new_states[n_state] += state_p / 4
                if i == 1:
                    db_rate += state_p / 4
            if state[3] is None:
                n_times = (-1,)
            else:
                n_times = (-1, -1)
            n_state = state[:3] + (n_times,)
            new_states[n_state] += state_p / 4
        new_states[(None, None, None, None)] += 1 - sum(new_states.values())
        self.s1_states = new_states
        self.s1_combine()

        self.defchain.rate = db_rate
        self.defchain.on()

        self.t_doublebuff += db_rate
        if self.t_doublebuff > 1:
            self.t_doublebuff -= 1
            log('buff', 'doublebuff', 15 * self.mod('buff', operator=operator.add))

    def s1_combine(self):
        self.combined_states = defaultdict(lambda: 0)
        for state, state_p in self.s1_states.items():
            c_state = tuple(
                0 if state[i] is None else len(state[i])
                for i in range(4)
            )
            self.combined_states[c_state] += state_p
        self.combined_states[(0, 0, 0, 0)] += 1 - sum(self.combined_states.values())
        
        # teambuffs
        m_team = 0
        self.s1_buffcount = 0
        for state, state_p in self.combined_states.items():
            self.s1_buffcount += sum(state) * state_p
            if state[0] == 0 and state[2] == 0:
                continue
            state_mods = [
                Modifier('sinoa_att', 'att', 'buff', 0.25 * state[0]),
                Modifier('sinoa_crit', 'crit', 'chance', 0.25 * state[2]),
            ]
            m_team += state_p * self.count_s1_team_buff(state_mods)
        log('buff', 'team', m_team)

    @property
    def buffcount(self):
        return super().buffcount + self.s1_buffcount

    def dmg_formula(self, name, dmg_coef):
        if self.combined_states is None or name == 'test':
            return super().dmg_formula(name, dmg_coef)
        m_dmg = 0
        for state, state_p in self.combined_states.items():
            if state[0] == 0 and state[2] == 0:
                m_dmg += state_p * super().dmg_formula(name, dmg_coef)
                continue
            state_mods = [
                Modifier('sinoa_att', 'att', 'buff', 0.25 * state[0]),
                Modifier('sinoa_crit', 'crit', 'chance', 0.25 * state[2]),
            ]
            m_dmg += state_p * super().dmg_formula(name, dmg_coef)
            for m in state_mods:
                m.off()
        return m_dmg

    def count_s1_team_buff(self, state_mods):
        base_mods = [
            Modifier('base_cc', 'crit', 'chance', 0.12),
            Modifier('base_killer', 'killer','passive', 0.30)
        ]
        self.dmg_test_event.modifiers = ModifierDict()
        for mod in base_mods:
            self.dmg_test_event.modifiers.append(mod)
        for b in filter(lambda b: b.get() and b.bufftype == 'simulated_def', self.all_buffs):
            self.dmg_test_event.modifiers.append(b.modifier)

        self.dmg_test_event()
        no_team_buff_dmg = self.dmg_test_event.dmg

        for mod in state_mods:
            self.dmg_test_event.modifiers.append(mod)
        placeholders = []
        for b in filter(lambda b: b.get() and b.bufftype in ('team', 'debuff'), self.all_buffs):
            placehold = None
            if b.modifier.mod_type == 's':
                placehold = Modifier('placehold_sd', 'att', 'sd', b.modifier.get() / 2)
            elif b.modifier.mod_type == 'spd':
                placehold = Modifier('placehold_spd', 'att', 'spd', b.modifier.get())
            elif b.modifier.mod_type.endswith('_killer'):
                placehold = Modifier('placehold_k', 'killer', 'passive', b.modifier.get())
            if placehold:
                self.dmg_test_event.modifiers.append(placehold)
                placeholders.append(placehold)
            else:
                self.dmg_test_event.modifiers.append(b.modifier)

        self.dmg_test_event()
        team_buff_dmg = self.dmg_test_event.dmg
        for mod in chain(base_mods, state_mods, placeholders):
            mod.off()

        return team_buff_dmg / no_team_buff_dmg - 1

    def post_run(self, end):
        self.s1_combine()
        if self.t_doublebuff > 0.5:
            log('buff', 'doublebuff', 15 * self.mod('buff', operator=operator.add))

class Sinoa_RNG(Adv):
    def s1_proc(self, e):
        Teambuff(e.name, *random.choice((
            (0.25, 15.0, 'att', 'buff'),
            (0.25, 15.0, 'defense', 'buff'),
            (0.25, 10.0, 'crit', 'chance'),
            (0.15, -1, 'maxhp', 'buff')
        ))).on()

variants = {
    None: Sinoa,
    'RNG': Sinoa_RNG
}
