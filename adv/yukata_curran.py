from core.advbase import *

def module():
    return Yukata_Curran

class Yukata_Curran(Adv):
    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s2
        `s4, x=5
        `s1, not self.energy()=5 and cancel
        `fs, x=5
        """
    conf['coabs'] = ['Sharena','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0
    conf['attenuation.hits'] = 1

    def prerun(self):
        self.s1_ehits = 0
        self.comment = f'assume {self.conf.attenuation.hits+1} hits per s1 bullet'

    def add_combo(self, name='#'):
        super().add_combo(name)
        if name.startswith('s1'):
            self.s1_ehits += 1
        if self.s1_ehits >= 10:
            self.s1_ehits -= 10
            self.energy.add(5, queue=True)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)