from core.advbase import *

def module():
    return Lin_You


class Lin_You(Adv):
    conf = {}
    conf['slots.a'] = ['The_Wyrmclan_Duo', 'Primal_Crisis']
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3, not buff(s3)
        `s4
        `s2, s1.check()
        `s1
        `fs, self.hits <= 44 and c_fs(enhanced) > 0 and x=4
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Axe2']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)