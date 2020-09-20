from core.advbase import *

def module():
    return Gala_Mym

class Gala_Mym(Adv):
    a3 = ('dt', 0.20)

    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Red_Impulse']
    conf['slots.d'] = 'Gala_Mars'
    conf['acl'] = """
        if s
        `dragon(c3-s-end), self.dragonform.shift_count<1
        `dragon
        end
        `s3, not buff(s3)
        `s1
        `s2, cancel
        `s4, cancel
        `fs, x=5
    """
    conf['share'] = ['Kleimann']
    conf['coabs'] = ['Verica', 'Marth', 'Yuya']
    
    def prerun(self):
        self.a1_buff = MultiBuffManager('flamewyrm', buffs=[
            Selfbuff('flamewyrm', 0.15, -1, 'att', 'buff'),
            SAltBuff(group='flamewyrm', base='s2')
        ])
        Event('dragon').listener(self.a1_on)

    def a1_on(self, e):
        if not self.a1_buff.get():
            self.a1_buff.on()
        else:
            self.dragonform.conf.update(self.conf.dragonform2)
            self.dragonform.shift_spd_mod = Modifier('flamewyrm_spd', 'spd', 'passive', 0.15).off()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)