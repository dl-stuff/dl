from core.advbase import *

def module():
    return Sylas

class Sylas(Adv):
    comment = 'no skill haste for team'
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3, not buff(s3)
        `s4
        `s1
        `s2
        `fs, x=5
        """
    conf['coabs'] = ['Eleonora','Dragonyule_Xainfried','Blade']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0

    def d_coabs(self):
        if self.duration <= 60:
            self.conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
