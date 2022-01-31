from core.advbase import *


class Gala_Emile(Adv):
    DISABLE_DACL = True
    comment = "always get team amp on s1 s2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sr = ReservoirSkill(name="s1", true_sp=4980, maxcharge=3)
        self.a_s_dict["s1"] = self.sr
        self.a_s_dict["s2"] = self.sr

    @property
    def skills(self):
        return (self.sr, self.s3, self.s4)

    def prerun(self):
        # ddrive end immediately
        self.l_ddrive = Listener("dragondrive", self.dragonform.d_shift_end)
        # a3 ss mod
        self.emile_ss_sd = Modifier("emile_ss_sd", "s", "passive", 0.0)
        self.extra_actmods.append(self.get_emile_ss_sd)
        # a3 fb
        for skill in self.a_s_dict.values():
            for s_act in skill.act_dict.values():
                if s_act.conf["owner"] and s_act.conf["attr"]:
                    for attr in s_act.conf.attr:
                        if "dmg" in attr:
                            share_fb_attr = {
                                "afflic": ["frostbite", 110, 0.31, 42],
                                "dmg_name": "a3",
                                "dtype": "#",
                                "iv": attr.get("iv", 0) + 0.00001,
                                "msl": attr.get("msl", 0),
                            }
                            s_act.conf.attr.append(share_fb_attr)
                            break

    def get_emile_ss_sd(self, name, base, group, aseq, attr):
        try:
            self.emile_ss_sd.mod_value = 1.5 if self.a_s_dict[name].owner else 0
        except KeyError:
            self.emile_ss_sd.mod_value = 0
        return self.emile_ss_sd


variants = {None: Gala_Emile}
