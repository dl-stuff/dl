from core.advbase import *

def module():
    return Naveed

class Naveed(Adv):
    conf = {}
    
    conf['acl'] = """
        `dragon, s
        `s3, not buff(s3)
        `s2, naveed_bauble < 5
        `s1, (cancel and naveed_bauble < 5) or (naveed_bauble=5)
        `s4, fsc
        `s2, fsc
        `fs, x=2
        """
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'The_Red_Impulse',
    'Sisters_of_the_Anvil',
    'Dueling_Dancers'
    ]
    conf['slots.burn.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'Me_and_My_Bestie',
    'Sisters_of_the_Anvil',
    'Dueling_Dancers'
    ]
    conf['coabs'] = ['Nobunaga', 'Wand', 'Yuya']
    conf['share'] = ['Gala_Mym']

    def prerun(self):
        self.naveed_bauble = 0

    def s2_proc(self, e):
        if self.naveed_bauble < 5:
            self.naveed_bauble += 1

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
