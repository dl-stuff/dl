from core.advbase import *
from pprint import pprint


class Sylas(Adv):
    def prerun(self):
        self.s2_states = {(None, None, None): 1}
        self.combined_states = None

        self.dmg_test_event = Event("dmg_formula")
        self.dmg_test_event.dmg_coef = 1
        self.dmg_test_event.dname = "test"
        self.s2_buffcount = 0

        self.defchain = Event("defchain")
        self.t_doublebuff = 0
        self.s2_max_hp = Modifier("s2_maxhp", "maxhp", "buff", 0)

        Event("idle").listener(self.s2_combine_after_s, order=0)

    def s2_combine_after_s(self, e):
        prev = self.action.getprev()
        if prev.name in ("s3", "s4"):
            self.s2_combine()

    @staticmethod
    def s2_prune(n_t, tpl):
        if not tpl:
            return None
        return tuple(s_t for s_t in tpl if s_t > n_t) or None

    def s2_expire(self, t):
        n_t = now()
        new_states = defaultdict(lambda: 0)
        for state, state_p in self.s2_states.items():
            n_state = (
                Sylas.s2_prune(n_t, state[0]),
                Sylas.s2_prune(n_t, state[1]),
                state[2],
            )
            new_states[n_state] += state_p
        new_states[(None, None, None)] += 1 - sum(new_states.values())
        self.s2_states = new_states
        self.s2_combine()

    def s2_proc(self, e):
        if self.nihilism:
            return Teambuff("s2_hp", 0.1, -1, "maxhp", "buff").on()
        n_t = now()
        n_bt = 15 * self.mod("buff", operator=operator.add)
        new_states = defaultdict(lambda: 0)
        db_rate = 0
        Timer(self.s2_expire).on(n_bt)
        for state, state_p in self.s2_states.items():
            n_all_state = []
            t_expire = n_t + n_bt
            for i in range(2):
                if state[i] is None:
                    n_times = (t_expire,)
                else:
                    n_times = (t_expire, *state[i])
                n_state = state[:i] + (n_times,) + state[i + 1 :]
                new_states[n_state] += state_p / 4
                if i == 1:
                    db_rate += state_p / 4
                n_all_state.append(n_times)
            if state[2] is None:
                n_times = (-1,)
            else:
                n_times = (-1, -1)
            n_state = state[:2] + (n_times,)
            new_states[n_state] += state_p / 4
            n_all_state.append(n_times)
            new_states[tuple(n_all_state)] += state_p / 4
            db_rate += state_p / 4
        new_states[(None, None, None)] += 1 - sum(new_states.values())
        self.s2_states = new_states
        self.s2_combine()

        self.defchain.rate = db_rate
        self.defchain.on()

        self.t_doublebuff += db_rate
        if self.t_doublebuff > 1:
            self.t_doublebuff -= 1
            log("buff", "doublebuff", 15 * self.mod("buff", operator=operator.add))

    def s2_combine(self):
        self.combined_states = defaultdict(lambda: 0)
        for state, state_p in self.s2_states.items():
            c_state = tuple(0 if state[i] is None else len(state[i]) for i in range(3))
            self.combined_states[c_state] += state_p
        self.combined_states[(0, 0, 0)] += 1 - sum(self.combined_states.values())

        # teambuffs
        m_team = 0
        self.s2_buffcount = 0
        for state, state_p in self.combined_states.items():
            self.s2_buffcount += sum(state) * state_p
            self.s2_max_hp.mod_value += state[2]
            if state[0] == 0:
                continue
            state_mods = [Modifier("sylas_att", "att", "buff", 0.25 * state[0])]
            m_team += state_p * self.count_s2_team_buff(state_mods)
        log("buff", "team", m_team)

    @property
    def buffcount(self):
        return super().buffcount + self.s2_buffcount

    def dmg_formula(self, name, dmg_coef, dtype=None, ignore_def=None):
        if self.combined_states is None or name == "test":
            return super().dmg_formula(name, dmg_coef, dtype=dtype, ignore_def=ignore_def)
        m_dmg = 0
        for state, state_p in self.combined_states.items():
            with Modifier("sylas_att", "att", "buff", 0.25 * state[0]):
                s_dmg = state_p * super().dmg_formula(name, dmg_coef, dtype=dtype, ignore_def=ignore_def)
                m_dmg += s_dmg
        return m_dmg

    def count_s2_team_buff(self, state_mods):
        base_mods = [
            Modifier("base_cc", "crit", "chance", 0.12),
            Modifier("base_killer", "killer", "passive", 0.30),
        ]
        self.dmg_test_event.modifiers = ModifierDict()
        for mod in base_mods:
            self.dmg_test_event.modifiers.append(mod)
        for b in filter(lambda b: b.get() and b.bufftype == "simulated_def", self.all_buffs):
            self.dmg_test_event.modifiers.append(b.modifier)

        self.dmg_test_event()
        no_team_buff_dmg = self.dmg_test_event.dmg

        for mod in state_mods:
            self.dmg_test_event.modifiers.append(mod)
        placeholders = []
        for b in filter(lambda b: b.get() and b.bufftype in ("team", "debuff"), self.all_buffs):
            placehold = None
            if b.modifier.mod_type == "s":
                placehold = Modifier("placehold_sd", "att", "sd", b.modifier.get() / 2)
            elif b.modifier.mod_type == "spd":
                placehold = Modifier("placehold_spd", "att", "spd", b.modifier.get())
            elif b.modifier.mod_type.endswith("_killer"):
                placehold = Modifier("placehold_k", "killer", "passive", b.modifier.get())
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
        self.s2_combine()
        if self.t_doublebuff > 0.5:
            log("buff", "doublebuff", 15 * self.mod("buff", operator=operator.add))


class Sylas_RNG(Adv):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.s2_buff_args = [
            (0.25, 15.0, "att", "buff"),
            (0.25, 15.0, "defense", "buff"),
            (0.20, -1, "maxhp", "buff"),
            "all",
        ]

    def s2_proc(self, e):
        pick = random.choice(self.s2_buff_args)
        if pick == "all":
            for buffarg in self.s2_buff_args[0:3]:
                Teambuff(e.name, *buffarg).on()
            self.aff_relief(["all"], 100)
        else:
            Teambuff(e.name, *pick).on()


class Sylas_S2STR(Adv):
    SAVE_VARIANT = False
    NO_DEPLOY = True
    comment = "always proc str s2"

    def s2_proc(self, e):
        Teambuff(e.name, 0.25, 15.0, "att", "buff").on()


class Sylas_S2DEF(Adv):
    SAVE_VARIANT = False
    NO_DEPLOY = True
    comment = "always proc def s2"

    def s2_proc(self, e):
        Teambuff(e.name, 0.25, 15.0, "defense", "buff").on()


class Sylas_S2HP(Adv):
    SAVE_VARIANT = False
    NO_DEPLOY = True
    comment = "always proc max hp s2"

    def s2_proc(self, e):
        Teambuff(e.name, 0.20, -1, "maxhp", "buff").on()


class Sylas_S2ALL(Adv):
    SAVE_VARIANT = False
    comment = "always proc all s2"

    def s2_proc(self, e):
        Teambuff(e.name, 0.25, 15.0, "att", "buff").on()
        Teambuff(e.name, 0.25, 15.0, "defense", "buff").on()
        Teambuff(e.name, 0.20, -1, "maxhp", "buff").on()
        self.aff_relief(["all"], 100)


variants = {
    None: Sylas,
    "RNG": Sylas_RNG,
    "S2STR": Sylas_S2STR,
    "S2DEF": Sylas_S2DEF,
    "S2HP": Sylas_S2HP,
    "S2ALL": Sylas_S2ALL,
}
