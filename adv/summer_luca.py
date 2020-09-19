from core.advbase import *

def module():
    return Summer_Luca

class Summer_Luca(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Red_Impulse']
    conf['acl'] = """
        `dragon
        `s1
        `s3
        `s4, x=4
        `s2, cancel
        """
    conf['coabs.base'] = ['Raemond','Lucretia','Peony']
    conf['coabs.paralysis'] = ['Raemond','Cleo','Peony']
    conf['share'] = ['Ranzal']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
