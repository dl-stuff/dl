from core.advbase import *


class Elisanne_55MC(Adv):
    SAVE_VARIANT = False
    comment = "55MC"
    conf = {
        "c": {"att": 497, "hp": 812, "spiral": False, "a": [["bt", 0.25]]},
        "s1": {
            "recovery": 1.0,
            "attr": [{"buff": ["team", 0.2, 15.0, "att", "buff"], "iv": 0.16667}],
        },
        "s2": {"attr": [{"dmg": 7.54, "iv": 0.96667}]},
    }
    ### TEST ###
    conf["prefer_baseconf"] = True
    conf[
        "acl"
    ] = """
    `dragon
    `ds
    `s1
    """

    def prerun(self):
        Modifier("bolb", "sp_s1", "passive", 1.0)

    ### TEST ###


variants = {None: Adv, "55MC": Elisanne_55MC}
