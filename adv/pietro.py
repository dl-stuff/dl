from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Pietro

class Pietro(Adv):
#    comment = 'no s2'
    
    a1 = ('cd',0.13)

    conf = {}
    conf['slots.a'] = Summer_Paladyns()+Primal_Crisis()
    conf['slots.frostbite.a'] = Resounding_Rendition()+His_Clever_Brother()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon.act('c3 s c3 end'),cancel
        `s3
        `s4
        `s1
        `fs, cancel and (s3.charged>=s3.sp-self.sp_val('fs') or s4.charged>=s4.sp-self.sp_val('fs')) and not x=2
        """
    conf['coabs'] = ['Tiki', 'Summer_Celliera', 'Yurius']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)