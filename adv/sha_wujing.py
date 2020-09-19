from core.advbase import *

def module():
    return Sha_Wujing

class Sha_Wujing(Adv):
    conf = {}
    conf['slots.a'] = ['Dragon_and_Tamer', 'Primal_Crisis']
    conf['slots.paralysis.a'] = ['Resounding_Rendition', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s2, cancel
        `s1
        `s4
        `fs, x=5
    """
    conf['coabs'] = ['Blade','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']

    def prerun(self):
        self.a1_count = 3
        Timer(self.a3_start).on(self.duration*0.3)
        Event('s').listener(self.a1_check, order=2)

    def a3_start(self, t):
        Selfbuff('a3', 0.08, -1, 'att', 'assailant').on()

    def a1_check(self, e):
        if self.a1_count > 0:
            self.a1_count -= 1
            Selfbuff('a1', 0.06, -1, 's', 'buff').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)