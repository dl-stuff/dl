from core.advbase import *

def module():
    return Mikoto

class Mikoto(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['slots.burn.a'] = ['Resounding_Rendition', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon, s=2 
        queue prep
        `s2;s4;s1
        end
        `s3, not buff(s3)
        `s4
        `s1, cancel
        `s2, x=5
        """
    conf['coabs'] = ['Halloween_Mym', 'Dagger2', 'Marth']
    conf['share'] = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
