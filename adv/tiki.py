from core.advbase import *

def module():
    return Tiki

class Tiki(Adv):
    comment = 'dragon damage does not work on divine dragon'

    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'The_Prince_of_Dragonyule']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = 'Dragonyule_Jeanne'
    conf['acl'] = """
        if divine_dragon.get()
        `s1
        `s2
        `dodge, x=3
        else
        `s3, not buff(s3) and fsc
        `dragon, dgauge>=1800
        `s4, x=5
        `s2
        `s1, fsc
        `fs,x=5
        end
    """
    conf['coabs'] = ['Blade', 'Xander', 'Catherine']
    conf['share'] = ['Kleimann']
    

    def d_slots(self):
        if self.duration <= 60:
            self.conf['slots.a'] = ['Twinfold_Bonds', 'The_Chocolatiers']
            self.conf['slots.frostbite.a'] = self.conf['slots.a']

    def prerun(self):
        self.divine_dragon = self.dragonform.set_dragondrive(ModeManager(
            group='ddrive',
            # buffs=[Selfbuff('divine_dragon', self.dragonform.ddamage(), -1, 'att', 'dragon')], # reeee
            x=True, s1=True, s2=True
        ), max_gauge=1800, shift_cost=560, drain=40)
        Event('dragon_end').listener(self.dragondrive_on)
        Event('dragondrive_end').listener(self.dragondrive_off)

    def dragondrive_on(self, e):
        self.a_fs_dict['fs'].set_enabled(False)
        self.s3.set_enabled(False)
        self.s4.set_enabled(False)
        self.charge_p('divine_dragon', 100)

    def dragondrive_off(self, e):
        self.a_fs_dict['fs'].set_enabled(True)
        self.s3.set_enabled(True)
        self.s4.set_enabled(True)

    def s1_proc(self, e):
        self.dragonform.charge_gauge(0, utp=True)

    def s2_proc(self, e):
        self.dragonform.charge_gauge(0, utp=True)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
