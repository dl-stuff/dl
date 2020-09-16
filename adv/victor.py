from core.advbase import *
from module.bleed import Bleed
from slot.a import *

def module():
    return Victor

class Victor(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Primal_Crisis()
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s4, x=5
        `s1, self.bleed._static['stacks'] < 3
        `s2, x=5
        """
    conf['coabs'] = ['Akasha','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']

    def prerun(self):
        self.bleed = Bleed('g_bleed',0).reset()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
