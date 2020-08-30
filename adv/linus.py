from core.advbase import *
from slot.a import *

def module():
    return Linus

class Linus(Adv):
    # comment = 'do not use weapon skill'
    conf = {}
    conf['slots.a'] = Summer_Paladyns()+The_Red_Impulse()
    conf['slots.paralysis.a'] = RR()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon
        `s3
        `s1 
        `s4, x=4
        `s2, x=4
        `fs, x=4
        """
    coab = ['Raemond','Lucretia','Peony']
    share = ['Kleimann']

    def d_slots(self):
        if self.duration <= 120:
            self.conf['slots.a'] = Resounding_Rendition() + Breakfast_at_Valerios()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)