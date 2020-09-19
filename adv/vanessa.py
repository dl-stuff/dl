from core.advbase import *

def module():
    return Vanessa

class Vanessa(Adv):
    conf = {}
    conf['slots.a'] = ['Mega_Friends', 'Primal_Crisis']
    conf['slots.burn.a'] = ['Resounding_Rendition', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon, s
        `s3, not buff(s3)
        `s4, fsc
        `s1, fsc or not buff(s1)
        `s2, cancel
        `fs, buff(s1) and buff(s2) # alt fs and s2 def down
    """
    conf['coabs.base'] = ['Blade', 'Marth', 'Wand']
    conf['share'] = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
