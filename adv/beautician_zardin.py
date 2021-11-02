from core.advbase import *


class Beautician_Zardin(Adv):
    def x_proc(self, e):
        if self.buff("s2"):
            self.afflics.stun.on(f"{e.name}_stunning_beauty", 1.0, 5.5)
            

variants = {None: Beautician_Zardin}
