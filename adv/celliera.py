from core.advbase import Adv

class Celliera(Adv):
    def s2_proc(self, e):
        if e.group == 'enhanced':
            self.dragonform.disabled = False
        else:
            self.dragonform.disabled = True

    def fs_enhanced_proc(self, e):
        self.dragonform.disabled = False

variants = {None: Celliera}

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)