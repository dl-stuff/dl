from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Durant

class Durant(Adv):
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
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
