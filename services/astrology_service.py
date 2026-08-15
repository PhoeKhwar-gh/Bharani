# services/astrology_service.py

import swisseph as swe
from models.divisional_model import DivisionalModel


class AstrologyService:

    def __init__(self):
        swe.set_ephe_path("ephe")

    def calculate_full_chart(self, data):

        jd = swe.julday(
            data["year"],
            data["month"],
            data["day"],
            data["hour"]
        )

        rasi = self.calculate_rasi(jd, data)
        d9   = DivisionalModel.calculate(rasi, "D9")

        return {
            "D1": rasi,
            "D9": d9
        }

    def calculate_rasi(self, jd, data):
        planets = []
        xx, _ = swe.calc_ut(jd, swe.SUN)
        planets.append({"longitude": xx[0]})
        return planets
