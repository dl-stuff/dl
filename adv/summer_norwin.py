from core.advbase import *

def module():
    return Summer_Norwin

class Summer_Norwin(Adv):
    conf = {}
    conf['slots.a'] = [
    'Twinfold_Bonds',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'A_Passion_for_Produce'
    ]
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end), x=5 and s1.charged<2000
        `s3, not buff(s3)
        `s1, c_s(1, a) or c_s(1, c)
        `s2, x=5 and (c_s(2, b) or c_s(2, d))
        `s4, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Eleonora']
    conf['share'] = ['Curran']

    def prerun(self):
        self.doleful = 0
        self.current_s['s1'] = 'a'
        self.current_s['s2'] = 'a'

    def s1_before(self, e):
        if e.group == 'd':
            self.doleful = 0
            self.energy.disabled = False

    def s2_proc(self, e):
        if e.group == 'd':
            self.set_hp(self.hp*(1-self.doleful*0.20))
            self.doleful = min(self.doleful+1, 4)
            self.energy.disabled = True


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
