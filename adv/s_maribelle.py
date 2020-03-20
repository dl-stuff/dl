import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Student_Maribelle

class Student_Maribelle(Adv):
    comment = ''
    a1 = ('s', 0.4, 'hp100')
    a3 = ('bk',0.3)

    conf = {}
    conf['slot.a'] = CC() + PC()
    conf['slot.d'] = Sakuya()
    conf['acl'] = """
        `s3, not self.s3_buff
        `s1
        `s2
    """


if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

