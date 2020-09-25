from core.advbase import *

def module():
    return Kirsty

class Kirsty(Adv):
    conf = {}
    conf['slots.a'] = [
    'Dragon_and_Tamer',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s4
        `s1
        `s2,x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Akasha']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']

    def prerun(self):
        if self.condition('maintain Dauntless Strength'):
            Timer(self.dauntless_strength).on(15)
            Timer(self.dauntless_strength).on(30)
            Timer(self.dauntless_strength).on(45)

    def dauntless_strength(self, t):
        Selfbuff('dauntless_strength',0.20,-1).on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)