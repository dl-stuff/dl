#unused now
import slot
from slot.a import *
import slot.w

def set(slots):
    ele = slots.c.ele
    wt = slots.c.wt
    stars = slots.c.stars
    name = slots.c.name
    if ele == 'flame':
        slots.d = slot.d.flame.Cerberus()
    elif ele == 'water':
        slots.d = slot.d.water.DJ()
    elif ele == 'wind':
        slots.d = slot.d.wind.Zephyr()
    elif ele == 'light':
        slots.d = slot.d.light.Cupid()
    elif ele == 'shadow':
        slots.d = slot.d.shadow.Marishiten()

    typeweapon = getattr(slot.w, wt)
    weapon = getattr(typeweapon, ele)

    slots.w = weapon()

    slots.a = RR()+LC()
    return


