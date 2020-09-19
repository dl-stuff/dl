from core.advbase import *

def module():
    return Valentines_Melody

class Valentines_Melody(Adv):
    comment = 'c4fsf c5 c4 s1'
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['slots.d'] = 'Ariel'
    conf['acl'] = """
        `dragon(c3-s-end),s=1
        `s3, not buff(s3)
        `s1
        `s4
        `s2, cancel
        """
    conf['coabs'] = ['Blade','Eleonora','Dragonyule_Xainfried']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0

    def __init__(self, conf=None, cond=None):
        super().__init__(conf=conf, cond=cond)
        self.slots.c.coabs['Axe2'] = [None, 'axe2']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
    