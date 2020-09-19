from core.advbase import *

def module():
    return Nefaria

class Nefaria(Adv):
    comment = 's2 fs(precharge) s1 s1'
    
    conf = {}
    conf['slots.a'] = ['Forest_Bonds', 'The_Fires_of_Hate']
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3, not buff(s3) and x=4
        `fs, c_fs(enhanced) > 0 and x=4
        `s1, fsc or x=1 or s=4 or not buff(s3)
        `s4
        `s2
        """
    conf['coabs'] = ['Wand','Gala_Alex','Heinwald']
    conf['share'] = ['Curran']

    conf['afflict_res.blind'] = 80
    conf['afflict_res.poison'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
