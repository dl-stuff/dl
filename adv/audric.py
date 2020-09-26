from core.advbase import *

def module():
    return Audric

class Audric(Adv):    
    conf = {}
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'The_Red_Impulse',
    'Flash_of_Genius',
    'The_Plaguebringer',
    'His_Clever_Brother'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), fsc and ((self.dragonform.shift_count<3) or ((self.dragonform.shift_count<=3) and self.trickery <= 1))
        `s3, not buff(s3)
        `s2
        `s1, cancel
        `s4, fsc
        `fs, x=3
    """
    conf['coabs'] = ['Wand','Cleo','Forte']
    conf['share'] = ['Xander']

    def prerun(self):
        self.dragonform.shift_mods.append(Modifier('cursed_blood', 'crit', 'chance', 0.30).off())


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
