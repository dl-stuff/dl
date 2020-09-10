from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Durant

class Durant(Adv):
    a1 = ('a',0.13,'hp100')
    a3 = ('cd',0.17,'hp100')

    conf = {}
    conf['slots.a'] = The_Fires_of_Hate()+Howling_to_the_Heavens()
    conf['slots.d'] = Fatalis()

    conf['slots.poison.a'] = Proper_Maintenance()+The_Plaguebringer()
    conf['slots.poison.d'] = Epimetheus()
    
    conf['acl'] = """
        `dragon, s=1
        `s3, not buff(s3)
        `s1
        `s2, x=5
        `s4
    """
    conf['coabs'] = ['Dagger2', 'Tobias', 'Axe2']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
