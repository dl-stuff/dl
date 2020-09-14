from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Laranoa

class Laranoa(Adv):
    comment = 'no haste buff for teammates'

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Breakfast_at_Valerios()
    conf['slots.frostbite.a'] = Resounding_Rendition()+His_Clever_Brother()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end),s
        `s3
        `s2
        `s4
        `s1
        `fs, seq=4
    """
    conf['coabs'] = ['Renee', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    def prerun(self):
        self.ahits = 0

    def add_combo(self):
        super().add_combo()
        if self.hits // 20 > self.ahits:
            self.ahits = self.hits // 20
            Selfbuff('sylvan critdmg',0.10,20,'crit','damage').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)