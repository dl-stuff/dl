from core.advbase import *

def module():
    return Grace

class Grace(Adv):
    conf = {}
    conf['slots.a'] = ['The_Lurker_in_the_Woods', 'The_Plaguebringer']
    conf['slots.d'] = 'Ramiel'
    conf['acl'] = """
        `dragon, fsc
        `s3, not buff(s3)
        `s4, fsc
        `dodge, fsc
        `fs, x=2
    """
    conf['coabs'] = ['Ieyasu', 'Gala_Alex', 'Forte']
    conf['share'] = ['Rodrigo']

    def prerun(self):
        self.hp = 100

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
