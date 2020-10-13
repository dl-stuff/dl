from core.advbase import *

def module():
    return Alain

class Alain(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon, s=2
        `s3, not buff(s3)
        `s1, cancel
        `s2, cancel
        `s4, cancel
        `fs, x=5
        """
    conf['coabs'] = ['Blade', 'Wand', 'Marth']
    conf['share'] = ['Kleimann']

    def prerun(self):
        from core.ability import Last_Buff
        Last_Buff.HEAL_TO = 50


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
