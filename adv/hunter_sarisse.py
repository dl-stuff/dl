from core.advbase import *

def module():
    return Hunter_Sarisse

class Hunter_Sarisse(Adv):
    comment = '8hit FS on A&O sized enemy (see special for 20hit); needs combo time to keep combo'

    conf = {}
    conf['slots.a'] = ['The_Lurker_in_the_Woods', 'Primal_Crisis']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `s3, fsc
        `s1, fsc
        `s2, fsc
        `s4, fsc
        `dodge, fsc
        `fs4
    """
    conf['coabs'] = ['Dragonyule_Cleo', 'Xander', 'Grace']
    conf['share'] = ['Gala_Elisanne', 'Marty']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
