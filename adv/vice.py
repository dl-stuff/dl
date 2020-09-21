from core.advbase import *

def module():
    return Vice

class Vice(Adv):
    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'The_Fires_of_Hate']
    conf['slots.d'] = 'Gala_Cat_Sith'
    conf['acl'] = """
        `dragon(c3-s-end), (fsc or self.sim_afflict) and self.trickery=0
        `s3, not buff(s3)
        `s4
        `s1
        `s2
        `fs, x=5
        """
    conf['coabs'] = ['Wand','Gala_Alex','Ieyasu']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
