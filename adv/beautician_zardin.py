from core.advbase import *
from slot.a import *

def module():
    return Beautician_Zardin

class Beautician_Zardin(Adv):
    comment = 'no s2'

    a3 = ('s',0.35,'hp70')

    conf = {}
    conf['slots.a'] = RR()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s1
        `s4, x=5
        """
    conf['coabs'] = ['Halloween_Elisanne','Lucretia','Peony']
    conf['share'] = ['Kleimann']

    def s1_proc(self, e):
        self.energy.add(1)
        Debuff(e.name, 0.05, 10, 0.3, 'attack').on()

    def s2_proc(self, e):
        self.energy.add(2)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)