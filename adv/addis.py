from core.advbase import *
from module.bleed import Bleed, mBleed

def module():
    return Addis

class Addis(Adv):
    comment = 'c5fsf; hold s2s1 until bleed under 3'
    conf = {}
    conf['slots.a'] = [
        'Resounding_Rendition',
        'Flash_of_Genius',
        'Levins_Champion',
        'The_Plaguebringer',
        'A_Small_Courage'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s=4 and not buff(s2)
        `s3, not buff(s3)
        `s2, charged_in(2, s1)
        `s1, not charged_in(3, s2) and bleed_stack < 3 and buff(s2)
        `s4, not buff(s2) and ((xf and not self.sim_afflict) or (xf=5 and self.sim_afflict))
        `fsf, xf=5
        """
    conf['coabs'] = ['Akasha','Dragonyule_Xainfried','Lin_You']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']
    
    conf['mbleed'] = True

    def getbleedpunisher(self):
        if self.bleed_stack > 0:
            return 0.08
        return 0

    def prerun(self):
        random.seed()
        # self.s2buff = Selfbuff('s2_shapshifts1',1, 10,'ss','ss')
        # self.s2str = Selfbuff('s2_str',0.25,10)
        self.bleedpunisher = Modifier('bleed','att','killer',0.08)
        self.bleedpunisher.get = self.getbleedpunisher
        # self.crit_mod = self.rand_crit_mod

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)