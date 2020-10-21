from core.advbase import *

class Audric(Adv):    
    def prerun(self):
        self.dragonform.shift_mods.append(Modifier('cursed_blood', 'crit', 'chance', 0.30).off())

variants = {None: Audric}

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
