from core.advbase import *

def module():
    return Gala_Zena

class Gala_Zena(Adv):
    conf = {}
    conf['slots.a'] = [
        'Here_Come_the_Sealers',
        'Endless_Waltz',
        'Dazzling_Duet',
        'A_Small_Courage',
        'Beautiful_Nothingness'
    ]
    conf['slots.d'] = 'Gala_Thor'
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s4
        `fs5, c_fs(auspex)
        `s1, cancel
        `s2, cancel
        """
    conf['coabs'] = ['Blade','Grace','Peony']
    conf['share'] = ['Hunter_Sarisse']

    def prerun(self):
        self.auspex_count = 0
        self.a3_modifier = Modifier('zena_a3', 'att', 'passive', 0.0)
        self.a3_modifier.get = self.a3_get
        self.fs_alt = FSAltBuff('a1_auspex', 'auspex', uses=1)

    def update_auspex(self):
        if not self.fs_alt.get():
            self.auspex_count += 1
        if self.auspex_count >= 2:
            self.fs_alt.on()
            self.auspex_count = 0

    def s1_proc(self, _):
        self.update_auspex()

    def s2_proc(self, _):
        self.update_auspex()

    def a3_get(self):
        if self.hp > 70:
            return self.sub_mod('maxhp', 'passive') * ((self.hp-70)/30 * 0.5 + 0.5)
        else:
            return self.sub_mod('maxhp', 'passive') * (self.hp/70 * 0.4 + 0.1)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
