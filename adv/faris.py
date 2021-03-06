from core.advbase import *
from module.template import SigilAdv


class Faris(SigilAdv):
    comment = "no dodge"
    conf = {
        "acl": """
        `s1
        """
    }

    @staticmethod
    def setup_uriel_wrath():
        return MultiLevelBuff(
            "uriel_wrath",
            [
                Debuff("uriel_wrath_lv1", -0.15, 15, mtype="attack", source="s1"),
                Debuff("uriel_wrath_lv2", -0.20, 15, mtype="attack", source="s1"),
                MultiBuffManager(
                    "uriel_wrath_lv3",
                    [
                        Debuff("uriel_wrath_lv3_debuff", -0.30, 10, mtype="attack", source="s1"),
                        AffResDebuff("uriel_wrath_lv3_scortch", -0.20, 10, affname="scorchrend", source="s1"),
                    ],
                ),
            ],
        )

    def prerun(self):
        self.config_sigil(duration=300, s1=True, x=True, fs=True)
        self.uriel_wrath = Faris.setup_uriel_wrath()

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.unlocked = True
        adv.uriel_wrath = Faris.setup_uriel_wrath()
        adv.current_s[dst] = "sigil"

    def s1_proc(self, e):
        if self.unlocked:
            self.uriel_wrath.on()


variants = {None: Faris}
