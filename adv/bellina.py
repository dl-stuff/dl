from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Bellina

class Bellina(Adv):
    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+Howling_to_the_Heavens()
    conf['slots.poison.a'] = Twinfold_Bonds()+The_Plaguebringer()
    conf['acl'] = """
        `s2, duration-now<2.0
        `s3, not buff(s3)
        if self.dragondrive.get()
        `s4, dgauge>1000 and x=3
        `s1, dgauge>1200 and x=3
        `fsf, x=3
        else
        `s2
        `dragon
        `fs, xf=4
        end
    """
    conf['slots.d'] = Fatalis()
    conf['coabs'] = ['Ieyasu','Curran','Berserker']
    conf['share'] = ['Veronica']

    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(
            group='ddrive',
            buffs=[Selfbuff('dragondrive', 0.35, -1, 's', 'passive')],
            x=True, fs=True, s1=True, s2=True
        ))
        self.hp = 100

    def s2_before(self, e):
        if self.hp > 30:
            if e.group == 'default':
                self.dragonform.charge_gauge(3000*(self.hp-30)/100, utp=True, dhaste=False)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
