from core.advbase import *

def module():
    return Forte

class Forte(Adv):
    conf = {}
    conf['slots.a'] = [
        'Dragon_and_Tamer',
        'Flash_of_Genius',
        'Moonlight_Party',
        'The_Plaguebringer',
        'Dueling_Dancers'
    ]
    conf['acl'] = """
        if self.sim_afflict
        `dragon(c3-s-end), x=5
        `s3, not buff(s3)
        `s2
        `s4, cancel or s=2
        `s1
        `fs, x=5
        else
        `dragon(c3-s-end), s2.charged<s2.sp/3 and cancel
        `s3, not buff(s3)
        `s2
        `s4
        `s1, cancel or self.afflics.poison.get()
        `fs, x=5
        end
        """
    conf['coabs'] = ['Ieyasu', 'Wand', 'Cleo']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']

    def prerun(self):
        Event('s').listener(self.s_dgauge)

    def s_dgauge(self, e):
        if e.name != 'ds':
            self.dragonform.charge_gauge(40, dhaste=False)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
