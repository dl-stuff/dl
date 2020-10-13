from core.advbase import *

def module():
    return Joe

class Joe(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon, s=1
        queue prep
        `s4;s1
        end
        `s3, x=5 and not buff(s3)
        `s4
        `s1, cancel and self.afflics.burn.timeleft()<5
        `s2, fsc
        `fs, x=5
    """
    conf['coabs'] = ['Blade', 'Wand', 'Marth']
    conf['share'] = ['Kleimann']
    

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)