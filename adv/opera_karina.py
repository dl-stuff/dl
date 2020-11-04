from core.advbase import *

class Opera_Karina(Adv):
    def prerun(self):
        self.a3_modifier = Modifier('a3_okarina', 'crit', 'damage', 0.3, get=self.a3_get)
    
    def a3_get(self):
        if self.zonecount:
            return 0.30
        return 0

variants = {None: Opera_Karina}
