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
        `s2, duration-now<1.5
        `s3, not self.s3_buff
        if self.dragondrive.get()
        `s4, self.dragonform.dragon_gauge>1050 and x=3
        `s1, self.dragonform.dragon_gauge>1100 and x=3
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

        # self.dragondrive_x = XAltBuff(self, 'ddrive')
        # self.fs_alt = Fs_alt(self, dragondrive_fs_conf, self.fs_proc_alt)
        
        # self.a_s1 = self.s1.ac
        # self.a_s1a = S('s1', Conf({'startup': 0.10, 'recovery': 1.10}))

        # self.a_s2 = self.s2.ac
        # self.a_s2a = S('s2', Conf({'startup': 0.10, 'recovery': 2.26}))

        # self.fsf_a = Fs('fsf', self.conf.fsf)
        # self.queue_gauge = 0

    # def dragondrive_on(self, e):
    #     self.s1.ac = self.a_s1a
    #     self.s2.ac = self.a_s2a
    #     self.fs_alt.on(-1)
    #     self.dragondrive_x.on()
    #     self.a_fsf = Fs('fsf', self.conf.fsf)

    # def dragondrive_off(self, e):
    #     self.s1.ac = self.a_s1
    #     self.s2.ac = self.a_s2
    #     self.fs_alt.off()
    #     self.dragondrive_x.off()

    # def s1_proc(self, e):
    #     if self.dragondrive_buff.get():
    #         with CrisisModifier(e.name, 0.50, self.hp):
    #             self.dmg_make(e.name, 2.02 * 5)
    #             self.add_hits(5)
    #         self.s1.charge(self.conf.s1.sp)
    #         self.queue_gauge = -750
    #     else:
    #         with CrisisModifier(e.name, 0.50, self.hp):
    #             self.dmg_make(e.name, 8.40)
    #             self.add_hits(1)

    def s2_before(self, e):
        if self.hp > 30:
            if e.group == 'default':
                # estimate assuming ~3000 max hp
                self.dragonform.charge_gauge(3000*(self.hp-30)/100, utp=True, dhaste=False)

        # if self.dragondrive_buff.get():
        #     pass
            # with CrisisModifier(e.name, 2.00, self.hp):
            #     self.dmg_make(e.name, 12.12)
            #     self.add_hits(1)
            # self.queue_gauge = -3000
            # -3000 gauge
            # 2.7666666507720947 (?)
            # 1212 mod, 3x crisis
        # else:
            # 2% hp loss = 1% gauge gain, cannot dhaste
            # if self.hp > 30:
            #     # TODO: but at this time self.hp = 40, should we keep this? or use 100hp->30hp = 1051 utp
            #     #self.dragonform.charge_gauge(3000 * (self.hp-30)/200, utp=True)
            #     self.dragonform.charge_gauge(1051, utp=True, dhaste=False)
            #     self.set_hp(30)
            # self.dragonform.charge_gauge(1200, utp=True)  # ingame logic, hp2utp before 1200
            # regular buff duration (?)

    # def s_proc(self, e):
    #     if self.dragondrive_buff.get():
    #         s = getattr(self, e.name)
    #         self.dragonform.add_drive_gauge_time(s.ac.getstartup()+s.ac.getrecovery(), skill_pause=True)
    #         self.dragonform.charge_gauge(self.queue_gauge, utp=True)
    #         self.queue_gauge = 0

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
