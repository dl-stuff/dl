from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Peony

peony_conf = {
    'x3.recovery': 44/60.0, # c4 0.9523809552192688 -> 0.761904776096344, need confirm

    'fs_dream.dmg':0,
    'fs_dream.sp' :0,
    'fs_dream.charge': 30/60.0,
    'fs_dream.startup': 20/60.0,
    'fs_dream.recovery': 60/60.0,
}

class Peony(Adv):
    comment = 'team skill prep not considered'

    conf = peony_conf.copy()
    conf['slots.a'] = Valiant_Crown()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, self.energy()=5
        `fs, self.fs_alt.uses > 0 and self.s2.check()
        `s2, cancel
        `s1, cancel and self.energy()!=5
        `s4, cancel
        `s3, cancel
    """
    conf['coabs'] = ['Blade','Sharena','Lucretia']
    conf['share'] = ['Kleimann']
    conf['afflict_res.paralysis'] = 0

    def fs_proc(self, e):
        if e.group == 'dream':
            self.fs_buffs.on()
            self.a1_is_cd = True
            self.a1_cd_timer.on(20)

    def a1_cd(self, t):
        self.a1_is_cd = False
        if self.a1_charge_defer:
            self.fs_alt.on()
            self.a1_charge_defer = False

    def prerun(self):
        self.phase['s1'] = 0
        self.fs_alt = FSAltBuff('dream', uses=1)
        self.fs_buffs = MultiBuffManager('dream', [
            Teambuff('fs_str', 0.10, 10, 'att', 'buff'),
            Spdbuff('fs_spd', 0.10, 10, wide='team'),
            Teambuff('fs_def', 0.20, 10, 'defense')
        ])

        self.a1_is_cd = False
        self.a1_charge_defer = False
        self.a1_cd_timer = Timer(self.a1_cd)

    @staticmethod
    def prerun_skillshare(self, dst_key):
        self.a1_is_cd = False
        self.fs_alt = Dummy()

    def s1_proc(self,e):
        self.afflics.paralysis(e.name,120,0.97)
        if self.phase['s1'] > 0:
            Selfbuff(e.name+'_defense', 0.10, 10, 'defense').on()
        if self.phase['s1'] > 1:
            Teambuff(e.name,0.10,10,'att','buff').on()
        self.phase['s1'] = (self.phase['s1'] + 1) % 3

    def s2_proc(self,e):
        with KillerModifier('s2_killer','hit',0.2,['paralysis']):
            self.dmg_make(e.name,9.64)
        Spdbuff(f'{e.name}_spd',0.10,10,wide='team').on()
        Teambuff(f'{e.name}_str',0.10,10,'att','buff').on()

        if self.a1_is_cd:
            self.a1_charge_defer = True
        else:
            self.fs_alt.on()

        # Using Gentle Dream grants the user the \"Empowering Dreams\" effect. 
        # When this effect is active, the user's next force strike will fill 40% of skill gauges for each team member's initial skill (with the exception of Peony), and grant the following effects to all team members for 10 seconds, none of which will stack: 
        # Increases strength by 10% 
        # Increases attack rate by 10% 
        # Increases defense by 20% 
        # Adds 5% to shadow resistance 
        # Increases movement speed by 5%. 
        # The Empowering Dreams effect cannot stack, will be consumed on use, and will not activate again for 20 seconds after activating.

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None,*sys.argv)
