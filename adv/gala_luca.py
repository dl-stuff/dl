from core.advbase import *

def module():
    return Gala_Luca

class Gala_Luca(Adv):
    # conf = {}
    # conf['slots.a'] = ['The_Wyrmclan_Duo', 'Primal_Crisis']
    # conf['acl'] = """
    #     `dragon, cancel
    #     `s3, not buff(s3)
    #     `s2
    #     `s1
    #     `s4, x=5
    #     """
    # conf['coabs'] = ['Axe2','Lucretia','Peony']
    # conf['share'] = ['Summer_Patia']

    def prerun(self):
        self.crit_mod = self.custom_crit_mod
        self.a1_buff_types = 3
        self.a1_states = {(None,) * self.a1_buff_types: 1.0}

        self.shared_crit = False
        self.all_icon_avg = (0, 0)
        self.s1_icon_avg = (0, 0)

    def update_icon_avg(self, n_avg, count, c_avg):
        return count + 1, (count * c_avg + n_avg) / (count + 1)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.rebind_function(Gala_Luca, 'buff_icon_count')
        # mayb need to do some check for existing ds_before/ds_proc
        adv.rebind_function(Gala_Luca, 'ds_before')
        adv.rebind_function(Gala_Luca, 'ds_proc')
        adv.shared_crit = True
        adv.gluca_crit_mods = {}

    def buff_icon_count(self):
        # not accurate to game
        icons = [b.name for b in self.all_buffs if b.get() and not b.hidden and b.bufftype == 'self' or b.bufftype == 'team']
        icon_count = len(set(icons))
        if self.conf['sim_buffbot.count'] is not None:
            icon_count += self.conf.sim_buffbot.count
        if self.shared_crit:
            log('debug', 'buff_icon_count', icon_count, str(icons))
        return min(icon_count, 7)

    def custom_crit_mod(self, name):
        if name == 'test':
            return self.solid_crit_mod(name)

        base_rate, crit_dmg = self.combine_crit_mods()
        crit_dmg -= 1
        new_states = defaultdict(lambda: 0.0)
        t = now()
        base_icon_count = self.buff_icon_count()
        mean_rate = 0.0

        in_s1 = name[0] == 's' or name == 'ds'

        icon_avg = 0
        for start_state, state_p in self.a1_states.items():
            state = tuple([b if b is not None and t - b <= 20.0 else None for b in start_state]) # expire old stacks
            a1_buff_count = sum(b is not None for b in state) # active a1buff count
            icon_count = min(base_icon_count+a1_buff_count, 7)
            current_rate = min(1.0, base_rate + 0.03 * a1_buff_count + min(0.28, 0.04 * icon_count) + 0.1 * icon_count * int(in_s1))
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
                    new_states[(t,) + state[0:i] + state[i + 1:]] += current_rate * state_p / self.a1_buff_types

        self.all_icon_avg = self.update_icon_avg(icon_avg, *self.all_icon_avg)
        if in_s1:
            self.s1_icon_avg = self.update_icon_avg(icon_avg, *self.s1_icon_avg)

        self.a1_states = new_states

        return 1.0 + mean_rate * crit_dmg

    def s1_before(self, e):
        if self.shared_crit:
            self.gluca_crit_mods[e.name] = Modifier(e.name, 'crit', 'chance', 0.1 * self.buff_icon_count()).off()
            self.extra_actmods.append(self.gluca_crit_mods[e.name])

    def s1_proc(self, e):
        if self.shared_crit:
            self.extra_actmods.remove(self.gluca_crit_mods[e.name])
            del self.gluca_crit_mods[e.name]

    def ds_before(self, e):
        if self.shared_crit:
            self.gluca_crit_mods[e.name] = Modifier(e.name, 'crit', 'chance', 0.1 * self.buff_icon_count()).off()
            self.extra_actmods.append(self.gluca_crit_mods[e.name])

    def ds_proc(self, e):
        if self.shared_crit:
            self.extra_actmods.remove(self.gluca_crit_mods[e.name])
            del self.gluca_crit_mods[e.name]

    def post_run(self, end):
        self.comment = f'avg buff icon {self.all_icon_avg[1]:.2f} (s1 {self.s1_icon_avg[1]:.2f})'

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
