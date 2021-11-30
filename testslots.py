from core.slots import *
from conf import get_adv
from pprint import pprint

adv = "Xania"
conf = get_adv(adv)
slot = Slots(adv, conf.c)
coabs = ["Laxi", "Gala_Laxi", "Marth"]
slot.c.set_coabs(coabs)
print(slot.c.coabs.keys())
pprint(slot.c.abilities)
