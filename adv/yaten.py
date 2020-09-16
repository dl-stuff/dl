from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Yaten

class Yaten(Adv):
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), fsc and self.energy() < 5
        `s3, not buff(s3)
        `s4
        `s1
        `s2, fsc and self.energy() < 4
        `fs, x=2
    """
    conf['coabs.base'] = ['Ieyasu','Wand','Delphi']
    conf['coabs.poison'] = ['Ieyasu','Wand','Bow']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']

    def prerun(self):
        Event('energy').listener(self.s1_upgrade)
        Event('energy_end').listener(self.s1_downgrade)

    def s1_upgrade(self, e):
        if e.stack >= 5:
            log('debug', 'upgrade')
            self.current_s['s1'] = 'energized'

    def s1_downgrade(self, e):
        log('debug', 'downgrade (no energy)')
        self.current_s['s1'] = 'default'

    def s1_proc(self, e):
        if e.group == 'energized':
            log('debug', 'downgrade (s1 proc)')
            self.current_s['s1'] = 'default'


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
