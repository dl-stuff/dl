from core.advbase import *

def module():
    return Heinwald

class Heinwald(Adv):
    conf = {}
    conf['slots.a'] = [
        'Resounding_Rendition',
        'Flash_of_Genius',
        'Howling_to_the_Heavens',
        'The_Plaguebringer',
        'A_Small_Courage'
    ]
    conf['acl'] = """
        `dragon(c3-s-end),x=5
        queue prep and not buff(s3)
        `s3;s1;s4;s2
        end
        `s4
        `s1
        `s2, cancel
        """
    conf['coabs'] = ['Blade','Wand','Bow']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
