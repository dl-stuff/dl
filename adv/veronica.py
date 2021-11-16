from core.advbase import *


class Veronica(Adv):
    comment = "last destruction teambuff not considered"

    def prerun(self):
        if not self.nihilism:
            SingleActionBuff("last_destruction", 0.1, 1, "s").on()


variants = {None: Veronica}
