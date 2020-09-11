from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Summer_Patia

class Summer_Patia(Adv):
    comment = 'cannot build combo for Cat Sith; uses up 15 stacks by 46.94s'
    conf = {}
    conf['slots.a'] = Kung_Fu_Masters()+The_Plaguebringer()
    conf['slots.poison.a'] = conf['slots.a']
    conf['slots.d'] = Shinobi()
    conf['acl'] = """
        # use dragon if using Cat Sith
        # `dragon(c3-s-end), fsc
        `s3, not buff(s3)
        `s1, fsc
        `s2, fsc
        `s4, fsc
        `dodge, fsc
        `fs3
    """
    conf['coabs'] = ['Summer_Patia', 'Blade', 'Wand', 'Curran']
    conf['share'] = ['Curran']

    def d_slots(self):
        if self.duration <= 120:
            self.conf['slots.d'] = Gala_Cat_Sith()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)