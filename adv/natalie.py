from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Natalie

class Natalie(Adv):
    a1 = ('eextra', 0.8)
    a3 = ('crisisattspd', 3)

    conf = {}
    conf['slots.a'] = HoH() + Primal_Crisis()
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
            `dragon.act("c3 s end"), (x=5 and self.slots.tmp.d.trickery <= 1) or self.hp=0
            `s3, not self.s3_buff
            `s2, s=3 or x=5
            `s1
            `s4
        """
    coab = ['Wand','Curran','Summer_Patia']
    share = ['Veronica']

    def d_slots(self):
        if self.duration <= 60:
            self.conf['slots.a'] = The_Chocolatiers()+Primal_Crisis()
            self.conf['slots.poison.a'] = The_Chocolatiers()+Primal_Crisis()

    def s1_proc(self, e):
        with CrisisModifier(e.name, 1, self.hp):
            self.dmg_make(e.name, 10.62)

        self.energy.add(1)
        # self.energy.add(1)
        # if random.random() < 0.8:
        #     self.energy.add(1)

    def s2_proc(self, e):
        if self.hp > 30:
            self.set_hp(20)
        else:
            Selfbuff(e.name, 0.15, 10).on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
