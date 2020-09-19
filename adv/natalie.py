from core.advbase import *

def module():
    return Natalie

class Natalie(Adv):
    conf = {}
    conf['slots.a'] = ['Heralds_of_Hinomoto', 'Primal_Crisis']
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end), (x=5 and self.trickery <= 1) or self.hp=0
        `s3, not buff(s3)
        `s2, s=3 or x=5
        `s1
        `s4
        """
    conf['coabs'] = ['Wand','Curran','Summer_Patia']
    conf['share'] = ['Veronica']

    def d_slots(self):
        if self.duration <= 60:
            self.conf['slots.a'] = ['The_Chocolatiers', 'Primal_Crisis']
            self.conf['slots.poison.a'] = ['The_Chocolatiers', 'Primal_Crisis']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
