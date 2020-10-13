from core.advbase import *
from module.x_alt import X_alt
import wep.lance

def module():
    return Halloween_Elisanne

class Halloween_Elisanne(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s2, not charged_in(s2, s1) or not charged_in(s2, s4)
        `s4
        `s1, cancel
        `fs, x=5
        """
    conf['coabs'] = ['Lucretia','Sharena','Peony']
    conf['share'] = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
