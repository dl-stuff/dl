from core.advbase import *


class Isaac(Adv):
    @staticmethod
    def verdure_zone_scharge(adv):
        adv.charge_p("verdue_zone_scharge", 0.02, no_autocharge=False)
        adv.verdure_team_sp += 2

    @staticmethod
    def setup_verdure(adv, dst="s1"):
        verdure_scharge_self = Timer(
            lambda _: adv.charge_p("verdure_scharge", 0.02, no_autocharge=False),
            1.0,
            True
        )
        verdure_scharge_self.name = "verdure_scharge"
        verdure_scharge_zone = ZoneTeambuff("verdure_scharge_zone", 0, 10.001, 'scharge_p', source=dst)
        verdure_scharge_zone.modifier = Timer(
            lambda _: Isaac.verdure_zone_scharge(adv),
            1.0,
            True
        )
        verdure_scharge_zone.name = "verdure_scharge_zone"
        return (
            (
                ZoneTeambuff("verdure_str_zone", 0.1, 10, "att", "buff", source=dst),
                Selfbuff("verdure_str", 0.05, 10, "att", "buff", source=dst)
            ),
            (
                ZoneTeambuff("verdure_spd_zone", 0.1, 10, "spd", "buff", source=dst),
                Selfbuff("verdure_spd", 0.05, 10, "spd", "buff", source=dst)
            ),
            (
                ZoneTeambuff("verdure_regen_zone", 20, 10, "regen", "buff", source=dst),
                Selfbuff("verdure_regen", 10, 10, "regen", "buff", source=dst)
            ),
            (
                verdure_scharge_zone,
                EffectBuff(
                    "verdure_scharge",
                    10.001,
                    verdure_scharge_self.on,
                    verdure_scharge_self.off,
                    source=dst
                )
            )
        )

    def prerun(self):
        self.wealdfury_amp = self.add_one_att_amp
        self.verdure_team_sp = 0
        self.verdure_buff = None # this is probably fine?

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.wealdfury_amp = lambda: None
        adv.verdure_team_sp = 0
        adv.verdure_buff = None

    def s1_before(self, e):
        self.wealdfury_amp()
        self.verdure_buff = random.choice(Isaac.setup_verdure(self, e.name))
        Timer(lambda _: self.verdure_buff[0].on(), 0.9).on()

    def s1_hit5(self, e, f, g, h):
        self.verdure_buff[1].on()

    def post_run(self, end):
        self.comment = f"total {self.verdure_team_sp}% SP to team from s1"


variants = {None: Isaac, "mass": Isaac}
