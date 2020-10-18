from core.advbase import *

def module():
    return Laranoa

class Laranoa(Adv):
    comment = 'no haste buff for teammates'

    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Breakfast_at_Valerios']
    conf['slots.frostbite.a'] = ['Resounding_Rendition', 'His_Clever_Brother']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end),s
        `s3
        `s2
        `s4
        `s1
        `fs, x=4
    """
    conf['coabs'] = ['Renee', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    def prerun(self):
        self.ahits = 0

    def add_combo(self, name='#'):
        super().add_combo(name)
        if self.hits // 20 > self.ahits:
            self.ahits = self.hits // 20
            Selfbuff(f'{name}_a1_att',0.02,15,'att','buff', source=None).on()
            Selfbuff(f'{name}_a1_crit',0.01,15,'crit','chance', source=None).on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)