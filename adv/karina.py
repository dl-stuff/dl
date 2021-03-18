from core.advbase import *


class Karina_FLEET(Adv):
    comment = "4 Karina comp"
    conf = {"fleet": 3}
    conf["prefer_baseconf"] = True
    conf["slots.d"] = "Gaibhne_and_Creidhne"
    conf["slots.a"] = [
        "Brothers_in_Arms",
        "Felyne_Hospitality",
        "Summer_Paladyns",
        "From_Whence_He_Comes",
        "Halidom_Grooms",
    ]
    conf[
        "acl"
    ] = """
        `s4
        `s3
        `s2
        `s1
        `dragon(c3-s-end)
    """
    conf["coabs"] = ["Summer_Estelle", "Renee", "Tobias"]
    conf["share"] = ["Patia", "Summer_Cleo"]


variants = {None: Adv, "FLEET": Karina_FLEET}
