from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Aldred

aldred_conf = {
    'x1_ddrive.utp': 120,
    'x2_ddrive.utp': 120,
    'x3_ddrive.utp': 120,
    'x4_ddrive.utp': 180,
    'x5_ddrive.utp': 180,
    # old c5 because fuck you
    'x5_ddrive.sp': 660,
    'x5_ddrive.dmg': 1.94,
}
class Aldred(Adv):
    comment = 'maintain dragondrive'

    conf = aldred_conf
    conf['slots.a'] = Heralds_of_Hinomoto()+Primal_Crisis()
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `s3, not buff(s3)
        `s2
        `dragon, not dragondrive.get()
        `s4
        `s1, x=5
    """
    conf['coabs'] = ['Wand','Summer_Patia','Curran']
    conf['share'] = ['Veronica']

    def d_slots(self):
        if self.duration <= 60:
            self.conf['slots.a'] = The_Chocolatiers()+Primal_Crisis()
            self.conf['slots.poison.a'] = The_Chocolatiers()+Primal_Crisis()

    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(
            self, 'ddrive',
            buffs=[Selfbuff('dragondrive', 0.30, -1, 's', 'passive')],
            x=True, s1=True, s2=True
        ))

    def s2_before(self, e):
        if self.hp > 30:
            if e.group == 'default':
                self.dragonform.charge_gauge(3000*(self.hp-30)/100, utp=True, dhaste=False)

    def x_proc(self, e):
        if e.group == 'ddrive':
            self.dragonform.charge_gauge(self.conf[e.name].utp, utp=True)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)