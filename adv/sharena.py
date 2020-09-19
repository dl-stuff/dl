from core.advbase import *

def module():
    return Sharena

class Sharena(Adv):
    comment = 'fs guard not considered'

    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s4
        `s1, cancel
        `s2, cancel
        `fs, x=5
    """
    conf['coabs'] = ['Malora','Lucretia','Peony']
    conf['afflict_res.paralysis'] = 0
    conf['share'] = ['Ranzal']

    def d_coabs(self):
        if self.duration <= 60:
            self.conf['coabs'] = ['Blade','Lucretia','Peony']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
