from core.advbase import *

def module():
    return Sophie

class Sophie(Adv):
    conf = {}
    conf['slots.a'] = [
    'Resounding_Rendition',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s4.check() and buff(s1)
        `s3, not buff(s3)
        `s4
        `s2, cancel
        `s1, not buff(s1) and x=5
        """
    conf['coabs'] = ['Blade', 'Dragonyule_Xainfried', 'Akasha']
    conf['afflict_res.poison'] = 0
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
