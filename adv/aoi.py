from core.advbase import *
from slot.a import *

def module():
    return Aoi

class Aoi(Adv):
    a1 = ('od',0.15)
    
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s=2
        `s3, not self.s3_buff
        `s4
        `s1
        `s2
    """
    conf['coabs'] = ['Wand', 'Marth', 'Yuya']
    conf['afflict_res.burn'] = 0
    conf['share'] = ['Kleimann']

    def s1_proc(self, e):
        self.afflics.burn(e.name,100,0.803)
    
    def s2_proc(self, e):
        self.afflics.burn(e.name,100,0.803)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)