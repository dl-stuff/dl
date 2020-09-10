from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import X_alt, Fs_alt

def module():
    return Bellina

# 2x crisis mods on autos and fs
dragondrive_auto_conf = {
    'x1.dmg': 189 / 100.0,
    'x1.sp': 290,
    'x1.utp': 180,
    'x1.startup': 27 / 60.0,
    'x1.recovery': 0,
    'x1.hit': 1,

    'x2.dmg': 227 / 100.0,
    'x2.sp': 350,
    'x2.utp': 180,
    'x2.startup': 35 / 60.0,
    'x2.recovery': 0,
    'x2.hit': 1,

    'x3.dmg': 340 / 100.0,
    'x3.sp': 520,
    'x3.utp': 240,
    'x3.startup': 40 / 60.0,
    'x3.recovery': 40 / 60.0,
    'x3.hit': 1,
}

dragondrive_fs_conf = {
    'fs.dmg': 0 / 100.0,
    'fs.sp': 360,
    'fs.utp': 900,
    'fs.charge': 120 / 60.0,
    'fs.startup': 4 / 60.0,
    'fs.recovery': 31 / 60.0,
    'fs.hit': -1,

    'x1fs.charge': 120 / 60.0,
    'fsf.charge': 5 / 60.0,
    'fsf.startup': 20 / 60.0, # unsure about this, might be lower
    'fsf.recovery': 0 / 60.0
}

class Bellina(Adv):
    a3 = ('crisisattspd', 3)

    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+Howling_to_the_Heavens()
    conf['slots.poison.a'] = Twinfold_Bonds()+The_Plaguebringer()
    conf['acl'] = """
        `s2, duration-now<1.5
        `s3, not self.s3_buff
        if self.dragondrive_buff.get()
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

    def fs_proc_alt(self, e):
        with CrisisModifier(e.name, 1.00, self.hp):
            self.dmg_make('fs', 5.65)
        self.dragonform.charge_gauge(self.conf.fs.utp, utp=True)

    def l_dragondrive_x(self, e):
        xalt = self.dragondrive_x
        xseq = e.name
        dmg_coef = xalt.conf[xseq].dmg
        sp = xalt.conf[xseq].sp
        hit = xalt.conf[xseq].hit
        utp = xalt.conf[xseq].utp
        log('x', xseq, 'dragondrive')
        self.add_hits(hit)
        with CrisisModifier('x', 1.00, self.hp):
            self.dmg_make(xseq, dmg_coef)
        self.charge(xseq, sp)
        self.dragonform.charge_gauge(utp, utp=True)

    def prerun(self):
        self.dragondrive_buff = Selfbuff('dragondrive', 0.35, -1, 's', 'passive')
        self.dragonform.set_dragondrive(self.dragondrive_buff)
        Event('dragon_end').listener(self.dragondrive_on) # cursed
        Event('dragondrive_end').listener(self.dragondrive_off)

        self.dragondrive_x = X_alt(self, 'dragondrive', dragondrive_auto_conf, x_proc=self.l_dragondrive_x)
        self.fs_alt = Fs_alt(self, dragondrive_fs_conf, self.fs_proc_alt)
        
        self.a_s1 = self.s1.ac
        self.a_s1a = S('s1', Conf({'startup': 0.10, 'recovery': 1.10}))

        self.a_s2 = self.s2.ac
        self.a_s2a = S('s2', Conf({'startup': 0.10, 'recovery': 2.26}))

        self.fsf_a = Fs('fsf', self.conf.fsf)
        self.queue_gauge = 0

    def dragondrive_on(self, e):
        self.s1.ac = self.a_s1a
        self.s2.ac = self.a_s2a
        self.fs_alt.on(-1)
        self.dragondrive_x.on()
        self.a_fsf = Fs('fsf', self.conf.fsf)

    def dragondrive_off(self, e):
        self.s1.ac = self.a_s1
        self.s2.ac = self.a_s2
        self.fs_alt.off()
        self.dragondrive_x.off()

    def s1_proc(self, e):
        if self.dragondrive_buff.get():
            with CrisisModifier(e.name, 0.50, self.hp):
                self.dmg_make(e.name, 2.02 * 5)
                self.add_hits(5)
            self.s1.charge(self.conf.s1.sp)
            self.queue_gauge = -750
        else:
            with CrisisModifier(e.name, 0.50, self.hp):
                self.dmg_make(e.name, 8.40)
                self.add_hits(1)

    def s2_proc(self, e):
        if self.dragondrive_buff.get():
            with CrisisModifier(e.name, 2.00, self.hp):
                self.dmg_make(e.name, 12.12)
                self.add_hits(1)
            self.queue_gauge = -3000
            # -3000 gauge
            # 2.7666666507720947 (?)
            # 1212 mod, 3x crisis
        else:
            # 2% hp loss = 1% gauge gain, cannot dhaste
            if self.hp > 30:
                # TODO: but at this time self.hp = 40, should we keep this? or use 100hp->30hp = 1051 utp
                #self.dragonform.charge_gauge(3000 * (self.hp-30)/200, utp=True)
                self.dragonform.charge_gauge(1051, utp=True, dhaste=False)
                self.set_hp(30)
            self.dragonform.charge_gauge(1200, utp=True)  # ingame logic, hp2utp before 1200
            # regular buff duration (?)

    def s_proc(self, e):
        if self.dragondrive_buff.get():
            s = getattr(self, e.name)
            self.dragonform.add_drive_gauge_time(s.ac.getstartup()+s.ac.getrecovery(), skill_pause=True)
            self.dragonform.charge_gauge(self.queue_gauge, utp=True)
            self.queue_gauge = 0

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
