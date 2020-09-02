from core.advbase import *
from module.x_alt import Fs_alt
from slot.a import *
from slot.d import *

def module():
    return Pinon

pinon_conf = {
    'x_max': 8,

    'x6.dmg': 10.6,
    'x6.sp': 325,
    'x6.startup': 1.3333,
    'x6.recovery': 0.4333,
    'x6.hit': 1,

    'x7.dmg': 10.6,
    'x7.sp': 325,
    'x7.startup': 1.3333,
    'x7.recovery': 0.4333,
    'x7.hit': 1,

    'x8.dmg': 10.6,
    'x8.sp': 325,
    'x8.startup': 1.3333,
    'x8.recovery': 0.4333,
    'x8.hit': 1,
} # get real frames 1 day, maybe

class Pinon(Adv):
    a3 = ('spd',0.20,'hp70')
    
    conf = pinon_conf.copy()
    conf['slots.a'] = Primal_Crisis()+His_Clever_Brother()
    conf['slots.d'] = Dragonyule_Jeanne()
    conf['acl'] = """
        # `dragon.act('c3 s end'), s
        `s3, not self.s3_buff
        if self.unlocked
        if x=8 or fsc
        `s2
        `s4
        `s1, self.energy()>=5
        end
        else
        if fsc
        `s2
        `s4
        `s1
        `dodge
        end
        `fs2
        end
    """
    conf['coabs'] = ['Dagger2', 'Axe2', 'Xander']
    conf['share'] = ['Gala_Elisanne']

    def fs_proc_alt(self, e):
        if e.name == 'fs2':
            with KillerModifier('fs_killer', 'hit', 2.0, ['frostbite']):
                self.dmg_make(e.name, 3.00)
            self.update_sigil(-13)

    def prerun(self):
        self.conf.x_max = 5
        self.unlocked = False
        self.sigil = EffectBuff('locked_sigil', 300, lambda: None, self.unlock).no_bufftime()
        self.sigil.on()
        self.s2_buff = Selfbuff('s2_att', 0.20, 20, 'att', 'buff')

        conf_alt_fs = {
            'fs1': {
                'dmg': 110 / 100.0,
                'sp': 500,
                'charge': 30 / 60.0,
                'startup': 0.06666667,
                'recovery': 1.0,
                'hit': 1
            },
            'fs2': {
                'dmg': 0 / 100.0,
                'sp': 710,
                'charge': 150 / 60.0,
                'startup': 0.06666667,
                'recovery': 1.0,
                'hit': -1
            }
        }
        self.fs_alt = Fs_alt(self, conf_alt_fs, fs_proc=self.fs_proc_alt)
        self.fs_alt.on(-1)

    def unlock(self):
        self.conf.x_max = 8
        self.unlocked = True
        self.unlock_time = now()

    def update_sigil(self, time):
        duration = self.sigil.buff_end_timer.add(time)
        if duration <= 0:
            self.sigil.off()
            self.unlock()

    def x_proc(self, e):
        if self.unlocked and int(e.name[1]) > 5:
            self.energy.add(0.4)

    def x(self):
        if self.unlock:
            prev = self.action.getprev()
            x_next = 1
            if prev.name[0] == 'x':
                if prev.index != self.conf.x_max:
                    x_next = prev.index + 1
                else:
                    x_next = self.conf.x_max
            return getattr(self, 'x%d' % x_next)()
        else:
            return super().x()

    def s1_proc(self, e):
        self.afflics.frostbite(e.name,120,0.41)

    def s2_proc(self, e):
        self.s2_buff.on()
        # only counts as 1 buff
        Event('defchain')()

    def post_run(self):
        try:
            self.comment += f'unlock at {self.unlock_time:.02f}s; only s1 if energized after unlock'
        except AttributeError:
            self.comment += f'not unlocked'

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)