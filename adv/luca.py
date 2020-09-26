from core.advbase import *
from adv.gala_luca import Gala_Luca

def module():
    return Luca

class Luca(Adv):
    conf = {}
    conf['slots.a'] = ["Flash_of_Genius", "Spirit_of_the_Season", "Resounding_Rendition", "A_Small_Courage", "Chariot_Drift"]
    conf['acl'] = """
        `dragon, energy()>3
        `s3, not buff(s3) and fsc
        `s2, cancel
        `s4, cancel
        `s1, x>2 or fsc
        `fs, x=5
        """
    conf['coabs'] = ['Sharena','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)