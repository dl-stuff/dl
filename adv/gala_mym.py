from core.advbase import *

def module():
    return Gala_Mym

class Gala_Mym(Adv):
    conf = {}
    conf['slots.a'] = [
    'Dragon_and_Tamer',
    'An_Ancient_Oath',
    'The_Red_Impulse',
    'His_Clever_Brother',
    'Dueling_Dancers'
    ]
    conf['slots.burn.a'] = [
    'Me_and_My_Bestie',
    'Dragon_and_Tamer',
    'The_Red_Impulse',
    'His_Clever_Brother',
    'Dueling_Dancers'
    ]
    conf['slots.d'] = 'Gala_Mars'
    conf['acl'] = """
        if s=1
        `dragon(c3-s-end), self.dragonform.shift_count<1
        `dragon
        end
        `s3, not buff(s3) and x=5
        `s1
        `s4
        `s2, x=5
        `fs, x=5
    """
    conf['share'] = ['Fjorm']
    conf['coabs'] = ['Verica', 'Serena', 'Yuya']
    
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