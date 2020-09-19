from core.advbase import *

def module():
    return Yurius

class Yurius(Adv):
    conf = {}
    conf['slots.a'] = ['Primal_Crisis', 'Candy_Couriers']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        if self.afflics.frostbite.get()
        `dragon, not dragondrive.get() and (self.duration<=120 or self.dragonform.dragon_gauge>=2130 or self.dragonform.shift_count>0)
        else
        `dragon, dragondrive.get()
        end
        queue prep and self.duration>120
        `s3; s2; s1; s4
        end
        `s3, cancel
        `s2, cancel
        `s4, cancel
        `s1, cancel
    """
    conf['coabs'] = ['Blade','Hunter_Sarisse','Xander']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    # conf['sim_afflict.efficiency'] = 1
    # conf['sim_afflict.type'] = 'frostbite'

    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(
            group='ddrive',
            buffs=[
                Selfbuff('dragondrive_sd', 0.35, -1, 's', 'passive'),
                Selfbuff('dragondrive_sp',0.30, -1, 'sp', 'buff')
            ],
            s1=True, s2=True
        ), drain=75)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
