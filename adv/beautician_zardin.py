from core.advbase import *

def module():
    return Beautician_Zardin

class Beautician_Zardin(Adv):
    comment = 'no s2'

    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s1
        `s4, x=5
        """
    conf['coabs'] = ['Halloween_Elisanne','Lucretia','Peony']
    conf['share'] = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)