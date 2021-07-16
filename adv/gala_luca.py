from core.advbase import *


class Gala_Luca(Adv):
    SAVE_VARIANT = False
    CONNECTING_CALL_CRITR = 0.03

    def prerun(self):
        self.crit_mod = self.custom_crit_mod
        self.a1_buff_types = 3
        self.a1_states = {(None,) * self.a1_buff_types: 1.0}
        self.all_icon_avg = (0, 0)
        self.s1_icon_avg = (0, 0)

        if self.nihilism:
            self.gluca_crit_mod = Modifier("s1", "crit", "chance", 0).off()
            self.share_dst = "s1"
            self.extra_actmods.append(self.get_gluca_crit_mod)

    def update_icon_avg(self, n_avg, count, c_avg):
        return count + 1, (count * c_avg + n_avg) / (count + 1)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.rebind_function(Gala_Luca, "buff_icon_count")
        adv.rebind_function(Gala_Luca, "get_gluca_crit_mod")
        adv.gluca_crit_mod = Modifier(dst, "crit", "chance", 0).off()
        adv.share_dst = dst
        adv.extra_actmods.append(adv.get_gluca_crit_mod)

    def get_gluca_crit_mod(self, name, base, group, aseq, attr):
        if base in (self.share_dst, "ds") or attr.get("gluca"):
            self.gluca_crit_mod.mod_value = 0.1 * self.buff_icon_count()
            log("debug_gluca", f"{name}:{aseq}", self.gluca_crit_mod.mod_value)
            return self.gluca_crit_mod
        return None

    def buff_icon_count(self):
        # not accurate to game
        icons = [b.name for b in self.all_buffs if b.get() and not b.hidden and b.bufftype == "self" or b.bufftype == "team"]
        icon_count = len(set(icons))
        if self.conf["sim_buffbot.count"] is not None:
            icon_count += self.conf.sim_buffbot.count
        return min(icon_count, 7)

    def custom_crit_mod(self, name):
        in_s1 = name[0:2] == "s1" or name == "ds"
        base_icon_count = self.buff_icon_count()

        if name == "test" or self.nihilism:
            if self.nihilism:
                self.all_icon_avg = self.update_icon_avg(base_icon_count, *self.all_icon_avg)
                if in_s1:
                    self.s1_icon_avg = self.update_icon_avg(base_icon_count, *self.s1_icon_avg)
            return self.solid_crit_mod(name)

        base_rate, crit_dmg = self.combine_crit_mods()
        crit_dmg -= 1
        new_states = defaultdict(lambda: 0.0)
        t = round(now() * 4) / 4
        mean_rate = 0.0

        icon_avg = 0
        for start_state, state_p in self.a1_states.items():
            state = tuple([b if b is not None and t - b <= 20.0 else None for b in start_state])  # expire old stacks
            a1_buff_count = sum(b is not None for b in state)  # active a1buff count
            icon_count = min(base_icon_count + a1_buff_count, 7)
            current_rate = min(
                1.0,
                base_rate + self.CONNECTING_CALL_CRITR * a1_buff_count + min(0.28, 0.04 * icon_count) + 0.1 * icon_count * int(in_s1),
            )
            # current_rate += 0.03 * a1_buff_count # a1buff crit
            # current_rate += min(0.28, 0.04 * icon_count) # a1 icon crit
            # current_rate += 0.1 * icon_count * int(in_s1) # s1 icon crit
            # current_rate = min(1.0, current_rate)
            mean_rate += current_rate * state_p
            icon_avg += icon_count * state_p

            if state[0] is not None and t - state[0] < 3.0:  # proc in last 3 seconds
                new_states[state] += state_p  # state won't change
            else:
                miss_rate = 1.0 - current_rate
                new_states[state] += miss_rate * state_p
                for i in range(self.a1_buff_types):
                    # t is the newest buff timing so it's in the front; the rest remain in order
                    new_states[(t,) + state[0:i] + state[i + 1 :]] += current_rate * state_p / self.a1_buff_types

        self.all_icon_avg = self.update_icon_avg(icon_avg, *self.all_icon_avg)
        if in_s1:
            self.s1_icon_avg = self.update_icon_avg(icon_avg, *self.s1_icon_avg)

        self.a1_states = new_states

        return 1.0 + mean_rate * crit_dmg

    def post_run(self, end):
        self.comment = f"avg buff icon {self.all_icon_avg[1]:.2f} (s1 {self.s1_icon_avg[1]:.2f})"


class Gala_Luca_MAX(Gala_Luca):
    comment = "7 buff icons from team (buff value not considered)"

    def buff_icon_count(self):
        return 7


class Gala_Luca_70MC(Gala_Luca):
    CONNECTING_CALL_CRITR = 0.04
    comment = "70 MC"
    conf = {
        "c": {
            "name": "Gala Luca",
            "icon": "100006_09_r05",
            "att": 619,
            "hp": 893,
            "ele": "light",
            "wt": "blade",
            "spiral": True,
            "a": [["resself_curse_crit_chance", 0.15, 10.0, 15.0], ["resself_poison_crit_chance", 0.15, 10.0, 15.0], ["affres_poison", 100.0], ["affres_curse", 100.0], ["cc", 0.13]],
        },
        "s1": {
            "sp": 2870,
            "startup": 0.1,
            "recovery": 2.16667,
            "attr": [
                {"dmg": 5.07, "iv": 0.3},
                {"dmg": 5.07, "iv": 2.0},
                {"dmg": 5.07, "iv": 2.06667},
                {"dmg": 5.07, "iv": 2.13333},
            ],
        },
        "s2": {
            "sp": 3899,
            "startup": 0.1,
            "recovery": 1.0,
            "attr": [
                {"amp": ["10000", 3, 0], "cd": 30.0},
                {"buff": ["self", 0.8, 10.0, "crit", "damage"], "iv": 0.16667},
            ],
        },
    }


variants = {None: Gala_Luca, "MAX": Gala_Luca_MAX, "70MC": Gala_Luca_70MC}
