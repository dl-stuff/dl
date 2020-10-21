from core.advbase import Adv

class Delphi(Adv):    
    def prerun(self):        
        self.s1.autocharge_init(80000).on()
        self.s2.autocharge_init(50000).on()

variants = {None: Delphi}

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
