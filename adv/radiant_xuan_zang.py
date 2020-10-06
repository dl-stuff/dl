from core.advbase import *

def module():
    return Radiant_Xuan_Zang

class Radiant_Xuan_Zang(Adv):
    conf = {}
    conf['slots.a'] = ['Candy_Couriers', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon, cancel
        `s3, not buff(s3)
        `s1
        `s2
        `s4, x>2
        `fs, c_fs(xihe)>0 and x=5
    """
    conf['coabs'] = ['Sharena', 'Blade', 'Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0

    def fs_xihe_proc(self, e):
        self.afflics.paralysis.res_modifier = 0.20
        Timer(self.fs_paralysis_rate_reset).on(20)

    def fs_paralysis_rate_reset(self, t):
        self.afflics.paralysis.res_modifier = 0

    def prerun(self):
        self.fs_alt = FSAltBuff(group='xihe', uses=1)
        self.xihe_gauge = 0
        self.xihe_gauge_gain = 50

    def s1_proc(self, e):
        if e.group == 'xihe':
            self.current_s['s1'] = 'default'

    def s2_proc(self, e):
        if e.group == 'xihe':
            self.current_s['s2'] = 'default'
        else:
            self.xihe_gauge += self.xihe_gauge_gain
            log('debug', 'xihe', self.xihe_gauge)
            if self.xihe_gauge >= 100:
                self.xihe_gauge = 0
                self.fs_alt.on()
                self.current_s['s1'] = 'xihe'
                self.current_s['s2'] = 'xihe'

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)