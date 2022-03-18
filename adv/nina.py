from core.advbase import *
from conf import DEFAULT


class Nina(Adv):
    def prerun(self):
        self.shopkeeper = 100

    @property
    def shopkeeper_charge(self):
        if self.shopkeeper < 33:
            return 0
        if self.shopkeeper < 66:
            return 1
        if self.shopkeeper < 100:
            return 2
        return 3

    def subtract_shopkeeper_charge(self, count):
        if self.shopkeeper_charge == 3:
            count -= 1
            self.shopkeeper -= 34 + count * 33
        else:
            self.shopkeeper -= count * 33
        if self.shopkeeper < 0:
            self.shopkeeper = 0
        if not self.is_set_cd("a3_amp", 45):
            self.add_amp(max_level=1, target=2)

    @allow_acl
    def s(self, n, s1_kind=None):
        if n == 1:
            if self.shopkeeper_charge > 0:
                self.current_s["s1"] = f"mode{self.shopkeeper_charge+1}"
                if s1_kind == "shopkeeper" and self.s1.charged < self.s1.sp:
                    self.subtract_shopkeeper_charge(1)
                    self.s1.charged = self.s1.sp
            else:
                self.current_s["s1"] = DEFAULT
        elif n == 2 and self.shopkeeper_charge < 3:
            return False
        return super().s(n)

    def s1_before(self, e):
        self.shopkeeper = min(100, self.shopkeeper + 13)

    def s2_before(self, e):
        self.subtract_shopkeeper_charge(3)


variants = {None: Nina}
