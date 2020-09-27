from core.advbase import *

def module():
    return Aldred

class Aldred(Adv):
    comment = 'maintain dragondrive'
    conf = {}
    conf['slots.a'] = [
        'Resounding_Rendition',
        'Flash_of_Genius',
        'Howling_to_the_Heavens',
        'The_Plaguebringer',
        'A_Small_Courage'
    ]
    conf['acl'] = """
        `s3, not buff(s3)
        `s2
        `dragon, not dragondrive.get()
        `s4
        `s1, x=5 or s
    """
    conf['coabs'] = ['Wand','Summer_Patia','Curran']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']

    def d_slots(self):
        if self.duration <= 60:
            self.conf['slots.a'] = ['The_Chocolatiers', 'Primal_Crisis']
            self.conf['slots.poison.a'] = ['The_Chocolatiers', 'Primal_Crisis']

    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(
            group='ddrive',
            buffs=[Selfbuff('dragondrive', 0.30, -1, 's', 'passive')],
            x=True, s1=True, s2=True
        ))
        self.hp = 100

    def s2_before(self, e):
        if self.hp > 30:
            if e.group == 'default':
                self.dragonform.charge_gauge(3000*(self.hp-30)/100, utp=True, dhaste=False)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
