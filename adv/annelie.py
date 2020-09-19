from core.advbase import *

def module():
    return Annelie

class Annelie(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['acl'] = """
        `dragon, self.energy()=3
        `s3, not buff(s3)
        `s4
        `s1
        `s2, self.energy()<5
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Lucretia','Peony']
    conf['share'] = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)