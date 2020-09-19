from core.advbase import *
from module.template import SigilAdv

def module():
    return Pinon


class Pinon(SigilAdv):    
    conf = {}
    conf['slots.a'] = ['Primal_Crisis', 'His_Clever_Brother']
    conf['slots.d'] = 'Dragonyule_Jeanne'
    conf['acl'] = """
        # `dragon(c3-s-end), s
        `s3, not buff(s3)
        if self.unlocked
        if x=8 or fsc
        `s2
        `s4
        `s1, self.energy()>=5
        end
        else
        if fsc
        `s2
        `s4
        `s1
        `dodge
        end
        `fs2
        end
    """
    conf['coabs'] = ['Dagger2', 'Axe2', 'Xander']
    conf['share'] = ['Gala_Elisanne']

    def fs2_proc(self, e):
        self.update_sigil(-13)

    def prerun(self):
        self.config_sigil(duration=300, x=True)

    def x(self):
        x_min = 1
        prev = self.action.getprev()
        if self.unlocked and isinstance(prev, X) and prev.index >= 5:
            x_min = 8
        return super().x(x_min=x_min)

    def post_run(self, end):
        if self.unlocked:
            self.comment += f'unlock at {self.unlocked:.02f}s; only s1 if energized after unlock'
        else:
            self.comment += f'not unlocked'

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)