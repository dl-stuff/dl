from core.advbase import *

def module():
    return Bellina

class Bellina(Adv):
    conf = {}
    conf['slots.a'] = [
        'Twinfold_Bonds',
        'Flash_of_Genius',
        'Seaside_Princess',
        'The_Plaguebringer',
        'Dueling_Dancers'
    ]
    conf['acl'] = """
        `s2, duration-now<1.5
        `s3, not buff(s3)
        if dragondrive.get()
        `s4, dgauge>500 and x=3
        `s1, dgauge>1000 and x=3
        `fsf, x=3
        else
        `s2
        `dragon
        `fs, x=4
        end
    """
    conf['slots.d'] = 'Fatalis'
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
        if self.hp > 30 and e.group == 'default':
            self.dragonform.charge_gauge(3000*(self.hp-30)/100, utp=True, dhaste=False)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
