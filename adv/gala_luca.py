from core.advbase import *
from module.template import LowerMCAdv


class Gala_Luca(Adv):
    SAVE_VARIANT = False
    CONNECTING_CALL_CRITR = 0.04

    def prerun(self):
        self.crit_mod = self.custom_crit_mod
        self.a1_buff_types = 3
        self.a1_buff_duration = 20.0
        self.a1_buff_cooldown = 3.0
        self.a1_states = {(None,) * self.a1_buff_types: 1.0}
        self.all_icon_avg = (0, 0)
        self.s1_icon_avg = (0, 0)

        if self.nihilism:
            self.gluca_crit_mod = Modifier("s1", "crit", "chance", 0).off()
            self.share_dst = "s1"
            self.extra_actmods.append(self.get_gluca_crit_mod)
            self.a1_crit_mod = Modifier("a1", "crit", "chance", 0)
            self.a1_crit_mod.get = self.a1_mod_value

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
        if base == self.share_dst or (base == "ds1" and self.dragonform.dform_mode == -1) or attr.get("gluca"):
            self.gluca_crit_mod.mod_value = 0.1 * self.buff_icon_count()
            log("gluca", f"{name}:{aseq}", self.gluca_crit_mod.mod_value)
            return self.gluca_crit_mod
        return None

    def a1_mod_value(self):
        # for nihil only
        return self.buff_icon_count() * 0.04

    def buff_icon_count(self):
        # not accurate to game
        icons = [b.name for b in self.all_buffs if b.get() and not b.hidden and b.bufftype == "self" or b.bufftype == "team"]
        icon_count = len(set(icons))
        if self.conf["sim_buffbot.count"] is not None:
            icon_count += self.conf.sim_buffbot.count
        return min(icon_count, 7)

    def custom_crit_mod(self, name):
        in_s1 = name[0:2] == "s1" or name[0:2] == "ds"
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
            state = tuple([b if b is not None and t - b <= self.a1_buff_duration else None for b in start_state])  # expire old stacks
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

            if state[0] is not None and t - state[0] < self.a1_buff_cooldown:  # proc in last 3 seconds
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
        if self.comment:
            self.comment += f"; avg buff icon {self.all_icon_avg[1]:.2f} (s1 {self.s1_icon_avg[1]:.2f})"
        else:
            self.comment = f"avg buff icon {self.all_icon_avg[1]:.2f} (s1 {self.s1_icon_avg[1]:.2f})"


class Gala_Luca_MAX(Gala_Luca):
    comment = "7 buff icons from team (buff value not considered)"

    def buff_icon_count(self):
        return 7


class Gala_Luca_50MC(Gala_Luca, LowerMCAdv):
    CONNECTING_CALL_CRITR = 0.03


class Gala_Luca_FAST(Gala_Luca):
    NO_DEPLOY = True
    comment = "faster but less accurate crit estimation"

    def prerun(self):
        super().prerun()
        self.a1_buff_count = 0.0
        self.a1_cooldown_rate = 0.0
        self.prev_t = 0.0

    def custom_crit_mod(self, name):
        in_s1 = name[0:2] == "s1" or name[0:2] == "ds"
        base_icon_count = self.buff_icon_count()

        if name == "test" or self.nihilism:
            if self.nihilism:
                self.all_icon_avg = self.update_icon_avg(base_icon_count, *self.all_icon_avg)
                if in_s1:
                    self.s1_icon_avg = self.update_icon_avg(base_icon_count, *self.s1_icon_avg)
            return self.solid_crit_mod(name)

        base_rate, crit_dmg = self.combine_crit_mods()
        crit_dmg -= 1
        t = now()
        icon_avg = 0

        def decay(value, ratio):
            return value * (1.0 - ratio ** 0.5)

        t_diff = t - self.prev_t
        self.prev_t = t
        self.a1_buff_count = decay(self.a1_buff_count, t_diff / self.a1_buff_duration)
        self.a1_cooldown_rate = decay(self.a1_cooldown_rate, t_diff / self.a1_buff_cooldown)

        icon_count = min(base_icon_count + self.a1_buff_count, 7)
        current_rate = min(
            1.0,
            base_rate + self.CONNECTING_CALL_CRITR * self.a1_buff_count + min(0.28, 0.04 * icon_count) + 0.1 * icon_count * int(in_s1),
        )
        proc_rate = current_rate * (1 - self.a1_cooldown_rate)
        self.a1_buff_count = min(self.a1_buff_count + proc_rate, self.a1_buff_types)
        self.a1_cooldown_rate = min(self.a1_cooldown_rate + proc_rate, 1.0)

        self.all_icon_avg = self.update_icon_avg(icon_count, *self.all_icon_avg)
        if in_s1:
            self.s1_icon_avg = self.update_icon_avg(icon_count, *self.s1_icon_avg)

        return 1.0 + current_rate * crit_dmg


variants = {None: Gala_Luca, "MAX": Gala_Luca_MAX, "50MC": Gala_Luca_50MC, "FAST": Gala_Luca_Fast}
