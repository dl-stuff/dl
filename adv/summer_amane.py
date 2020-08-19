from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Summer_Amane

class Summer_Amane(Adv):
    comment = 'no s1'
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Memory_of_a_Friend()
    conf['slots.poison.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['slots.d'] = Ariel()
    conf['acl'] = """
        `dragon.act("c3 s c2 end"), s=2
        `s2
        `s4
        `s3, cancel
        ## For healing
        #`s1, x=5
        """
    coab = ['Blade', 'Dragonyule_Xainfried', 'Lin_You']
    share = ['Ranzal', 'Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
