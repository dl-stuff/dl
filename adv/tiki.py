from core.advbase import *

class Tiki(Adv):
    comment = 'dragon damage does not work on divine dragon'
    def prerun(self):
        self.divine_dragon = self.dragonform.set_dragondrive(ModeManager(
            group='ddrive',
            # buffs=[Selfbuff('divine_dragon', self.dragonform.ddamage(), -1, 'att', 'dragon')], # reeee
            x=True, s1=True, s2=True
        ), max_gauge=1800, shift_cost=560, drain=40)
        Event('dragon_end').listener(self.a_dragondrive_on)
        Event('dragondrive_end').listener(self.a_dragondrive_off)

    def a_dragondrive_on(self, e):
        self.a_fs_dict['fs'].set_enabled(False)
        self.s3.set_enabled(False)
        self.s4.set_enabled(False)
        self.charge_p('divine_dragon', 100)

    def a_dragondrive_off(self, e):
        self.a_fs_dict['fs'].set_enabled(True)
        self.s3.set_enabled(True)
        self.s4.set_enabled(True)

    def s1_proc(self, e):
        self.dragonform.charge_gauge(0, utp=True)

    def s2_proc(self, e):
        self.dragonform.charge_gauge(0, utp=True)

class Tiki_DDAMAGE(Tiki):
    comment = 'if dragon damage worked on tiki'
    def prerun(self):
        self.divine_dragon = self.dragonform.set_dragondrive(ModeManager(
            group='ddrive',
            buffs=[Selfbuff('divine_dragon', self.dragonform.ddamage(), -1, 'att', 'dragon')],
            x=True, s1=True, s2=True
        ), max_gauge=1800, shift_cost=560, drain=40)
        Event('dragon_end').listener(self.a_dragondrive_on)
        Event('dragondrive_end').listener(self.a_dragondrive_off)


variants = {
    None: Tiki,
    'DDAMAGE': Tiki_DDAMAGE
}
