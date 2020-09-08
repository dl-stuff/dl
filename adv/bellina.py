from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import X_alt, Fs_alt

def module():
    return Bellina

# 2x crisis mods on autos and fs
renegade_queen = {
    # 'x1.dmg': 189 / 100.0,
    # 'x1.sp': 290,
    # 'x1.utp': 180,
    'x1_ddrive.attr': [{'dmg': 1.89, 'sp': 290, 'utp': 180, 'crisis': 1}],
    'x1_ddrive.startup': 27 / 60.0,
    'x1_ddrive.recovery': 0,
    # 'x1.hit': 1,

    # 'x2.dmg': 227 / 100.0,
    # 'x2.sp': 350,
    # 'x2.utp': 180,
    'x2_ddrive.attr': [{'dmg': 2.27, 'sp': 350, 'utp': 180, 'crisis': 1}],
    'x2_ddrive.startup': 35 / 60.0,
    'x2_ddrive.recovery': 0,
    # 'x2.hit': 1,

    # 'x3.dmg': 340 / 100.0,
    # 'x3.sp': 520,
    # 'x3.utp': 240,
    'x3_ddrive.attr': [{'dmg': 2.27, 'sp': 350, 'utp': 240, 'crisis': 1}],
    'x3_ddrive.startup': 40 / 60.0,
    'x3_ddrive.recovery': 40 / 60.0,
    # 'x3.hit': 1,

    # 'fs.dmg': 0 / 100.0,
    # 'fs.sp': 360,
    # 'fs.utp': 900,
    'fs_ddrive.attr': [{'dmg': 5.65, 'sp': 360, 'utp': 900, 'crisis': 1, 'hit': -1}],
    'fs_ddrive.charge': 120 / 60.0,
    'fs_ddrive.startup': 4 / 60.0,
    'fs_ddrive.recovery': 31 / 60.0,
    # 'fs.hit': -1,
    'fs_ddrive.x1.charge': 120 / 60.0,

    'fsf.charge': 5 / 60.0,
    'fsf.startup': 20 / 60.0, # unsure about this, might be lower
    'fsf.recovery': 0 / 60.0
}

class Bellina(Adv):
    conf = renegade_queen.copy()
    conf['slots.a'] = Twinfold_Bonds()+Howling_to_the_Heavens()
    conf['slots.poison.a'] = Twinfold_Bonds()+The_Plaguebringer()
    conf['acl'] = """
        `s2, duration-now<2
        `s3, not self.s3_buff
        if self.dragondrive.get()
        `s4, dgauge>1000 and x=3
        `s1, dgauge>1200 and x=3
        `s1, s=4
        `fsf, x=3
        else
        `s2
        `dragon
        `fs, x=4
        end
    """
    conf['coabs'] = ['Ieyasu','Curran','Berserker']
    conf['share'] = ['Sha_Wujing']

    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(
            self, 'ddrive',
            buffs=[Selfbuff('dragondrive', 0.35, -1, 's', 'passive')],
            x=True, fs=True, s1=True, s2=True
        ))

    def s2_before(self, e):
        if self.hp > 30:
            if e.group == 'default':
                self.dragonform.charge_gauge(3000*(self.hp-30)/100, utp=True, dhaste=False)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
