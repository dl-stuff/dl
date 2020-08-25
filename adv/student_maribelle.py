from core.advbase import *

def module():
    return Student_Maribelle

class Student_Maribelle(Adv):
    a1 = ('s', 0.4, 'hp100')
    a3 = ('bk',0.3)
    
    conf = {}
    conf['acl'] = """
        `dragon,s
        `s3, not self.s3_buff and x=5
        `s4
        `s1
        `s2,cancel
        """
    coab = ['Blade', 'Marth', 'Gala_Sarisse']
    share = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
