from core.advbase import *
from slot.a import *

def module():
    return Johanna

class Johanna(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Breakfast_at_Valerios()
    conf['slots.poison.a'] = Kung_Fu_Masters()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3 s end)
        `s3, not self.s3_buff 
        `s4
        `s1 
        `s2
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)