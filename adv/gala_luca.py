from core.advbase import *
from slot.a import *

def module():
    return Gala_Luca

class Gala_Luca(Adv):
    a3 = ('cc',0.13,'hit15')

    conf = {}
    conf['slots.a'] = The_Wyrmclan_Duo()+Primal_Crisis()
    conf['acl'] = """
        `dragon, cancel
        `s3, not buff(s3)
        `s2
        `s1
        `s4, x=5
        """
    conf['coabs'] = ['Axe2','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']

    def prerun(self):
        self.crit_mod = self.custom_crit_mod
        self.in_s1 = False
        self.a1_buff_types = 3
        self.a1_states = {(None,) * self.a1_buff_types: 1.0}

        self.ds_proc_o = self.dragonform.ds_proc
        self.dragonform.ds_proc = self.ds_crit_proc
        self.shared_crit = False
        self.all_icon_avg = (0, 0)
        self.s1_icon_avg = (0, 0)

    def update_icon_avg(self, n_avg, count, c_avg):
        return count + 1, (count * c_avg + n_avg) / (count + 1)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.rebind_function(Gala_Luca, 'ds_crit_proc')
        adv.rebind_function(Gala_Luca, 'buff_icon_count')
        adv.ds_proc_o = adv.dragonform.ds_proc
        adv.dragonform.ds_proc = adv.ds_crit_proc
        adv.shared_crit = True

    def ds_crit_proc(self):
        if self.shared_crit:
            crit_mod = Modifier('gala_luca_share', 'crit', 'chance', 0.1 * self.buff_icon_count())
            crit_mod.on()
            dmg = self.ds_proc_o()
            crit_mod.off()
            self.in_s1 = False
        else:
            self.in_s1 = True
            dmg = self.ds_proc_o()
            self.in_s1 = False
        return dmg

    def buff_icon_count(self):
        # not accurate to game
        icon_count = len(set([b.name for b in self.all_buffs if b.get() and not b.hidden and b.bufftype == 'self' or b.bufftype == 'team']))
        if self.conf['sim_buffbot.count'] is not None:
            icon_count += self.conf.sim_buffbot.count
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

        icon_avg = 0
        state_p_sum = 0
        for start_state, state_p in self.a1_states.items():
            state = tuple([b if b is not None and t - b <= 20.0 else None for b in start_state])  # expire old stacks
            current_rate = base_rate
            a1_buff_count = len([b for b in state if b is not None])  # active a1buff count
            icon_count = min(base_icon_count+a1_buff_count, 7)
            current_rate += 0.03 * a1_buff_count  # a1buff crit
            current_rate += min(0.28, 0.04 * icon_count)  # a1 icon crit
            if self.in_s1:
                current_rate += 0.1 * icon_count  # s1 icon crit
            current_rate = min(1.0, current_rate)
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
        if self.in_s1:
            self.s1_icon_avg = self.update_icon_avg(icon_avg, *self.s1_icon_avg)
        
        self.a1_states = new_states

        return 1.0 + mean_rate * crit_dmg

    def s1_before(self, e):
        if self.shared_crit:
            crit_mod = Modifier('gala_luca_share', 'crit', 'chance', 0.1 * self.buff_icon_count())
            crit_mod.on()
        else:
            self.in_s1 = True

    def s1_proc(self, e):
        if self.shared_crit:
            crit_mod.off()
        else:
            self.in_s1 = False

    def post_run(self, end):
        self.comment = f'avg buff icon {self.all_icon_avg[1]:.2f} (s1 {self.s1_icon_avg[1]:.2f})'

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)