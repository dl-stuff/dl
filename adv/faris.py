from core.advbase import *
from module.template import SigilAdv


class Faris(SigilAdv):
    ALLOWED_DODGE_PER_S2 = 1
    comment = f"allow {ALLOWED_DODGE_PER_S2} dodge by FS per s2 cast"

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
                        AffResDebuff("uriel_wrath_lv3_scortch", -0.25, 10, affname="scorchrend", source="s1"),
                    ],
                ),
            ],
        )

    def prerun(self):
        self.config_sigil(duration=300, s1=True, x=True, fs=True)
        self.uriel_wrath = Faris.setup_uriel_wrath()
        if self.ALLOWED_DODGE_PER_S2:
            self.s2_counter = FSAltBuff("fs_counter", "counter", uses=self.ALLOWED_DODGE_PER_S2, hidden=True)
            self.s2_sigilcounter = FSAltBuff("fs_sigilcounter", "sigilcounter", uses=self.ALLOWED_DODGE_PER_S2, hidden=True)
        self.a1_cd = False
        self.a1_sigil_cd = False

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.uriel_wrath = Faris.setup_uriel_wrath()
        adv.current_s[dst] = "sigil"

    def a1_cd_end(self, t):
        self.a1_cd = False

    def a1_sigil_cd_end(self, t):
        self.a1_sigil_cd = False

    def fs_counter_proc(self, e):
        if not self.a1_cd:
            self.a_update_sigil(-36)
            self.a1_cd = True
            Timer(self.a1_cd_end).on(10)

    def fs_sigilcounter_proc(self, e):
        if not self.a1_cd:
            self.uriel_wrath.on()
            self.a1_cd = True
            Timer(self.a1_cd_end).on(10)

    def s1_proc(self, e):
        if not isinstance(self, Faris) or self.unlocked:
            self.uriel_wrath.on()

    def s2_proc(self, e):
        if self.ALLOWED_DODGE_PER_S2:
            if self.unlocked:
                self.s2_sigilcounter.on()
            else:
                self.s2_counter.on()


class Faris_UNLOCKED(Faris):
    SAVE_VARIANT = False
    def prerun(self):
        super().prerun()
        self.a_update_sigil(-300)


variants = {None: Faris, "UNLOCKED": Faris_UNLOCKED}
