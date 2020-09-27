from core.advbase import *

def module():
    return Audric

class Audric(Adv):    
    conf = {}
    conf['slots.a'] = [
        'The_Shining_Overlord',
        'Flash_of_Genius',
        'The_Red_Impulse',
        'The_Plaguebringer',
        'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), fsc and ((self.dragonform.shift_count<3) or ((self.dragonform.shift_count<=3) and self.trickery <= 1))
        `s3, not buff(s3)
        `s1
        `s4, cancel
        `s2, fsc
        `fs, x=3
    """
    conf['coabs'] = ['Wand','Cleo','Forte']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']

    def prerun(self):
        self.dragonform.shift_mods.append(Modifier('cursed_blood', 'crit', 'chance', 0.30).off())


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
