from core.advbase import *

def module():
    return Valentines_Melody

class Valentines_Melody(Adv):
    conf = {}
    conf['slots.a'] = [
    'Summer_Paladyns',
    'Flash_of_Genius',
    'Kung_Fu_Masters',
    'The_Plaguebringer',
    'Chariot_Drift'
    ]
    conf['slots.d'] = 'Ariel'
    conf['acl'] = """
        `dragon(c3-s-end), s=1
        `s3, not buff(s3)
        `s1
        `s4
        `s2, cancel
        """
    conf['coabs'] = ['Blade','Eleonora','Dragonyule_Xainfried']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0

    def __init__(self, conf=None, duration=180, cond=None, altchain=None):
        super().__init__(conf=conf, duration=duration, cond=cond)
        self.slots.c.coabs['Axe2'] = [None, 'axe2']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
    