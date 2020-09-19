from core.advbase import *

def module():
    return Amane

class Amane(Adv):    
    conf = {}
    conf['slots.a'] = ['Candy_Couriers', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon, cancel
        queue prep
        `s2;s3;s1;s4
        end
        `s1
        `s4, x>3
        `s3, cancel
        `s2, x>3
        """
    conf['coabs'] = ['Blade','Sharena','Peony']
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
