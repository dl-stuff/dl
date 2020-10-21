from core.advbase import Adv, Teambuff

class Fjorm(Adv):
    comment = 'last bravery once at start'
    def prerun(self):
        Teambuff('last_bravery',0.3,15).on()
        Teambuff('last_bravery_defense', 0.40, 15, 'defense').on()

variants = {None: Fjorm}

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
