from core.advbase import *
from slot.a import *

def module():
    return Valentines_Orion

class Valentines_Orion(Adv):
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon,s
        `s3, fsc and not buff(s3)
        `s4,fsc
        `s1,cancel
        `fs, x=2
    """
    conf['coabs'] = ['Blade', 'Marth', 'Wand']
    conf['afflict_res.burn'] = 0
    conf['share'] = ['Kleimann']

    def s1_proc(self, e):
        self.afflics.burn(e.name,100,0.803)

    def s2_proc(self, e):
        Teambuff(e.name+'_defense', 0.15, 15, 'defense').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
