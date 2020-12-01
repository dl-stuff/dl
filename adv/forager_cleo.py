from core.advbase import *

class Forager_Cleo(Adv):
    def prerun(self):
        self.starlit_dining = 0
    
    def s1_proc(self, e):
        self.starlit_dining = min(4, self.starlit_dining+1)
    
    def fs_foragercleo_proc(self, e):
        self.starlit_dining = 0

variants = {None: Forager_Cleo}
