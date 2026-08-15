# divisional_calculations.py
from constants import *
from zodiac_utils import compute_nth_sign

class DivisionalCalculator:

    @staticmethod
    def calculate_hora_d2(sign_num, degrees):
        is_odd = sign_num in ODD_SIGNS

        if degrees < 15:
            div_sign = 5 if is_odd else 4
        else:
            div_sign = 4 if is_odd else 5

        div_deg = degrees if degrees < 15 else degrees - 15
        return div_sign, div_deg

    @staticmethod
    def calculate_navamsa_d9(sign_num, degrees):
        amsa = 3 + 20/60
        part = int(degrees / amsa)

        if sign_num in MOVABLE_SIGNS:
            base = sign_num
        elif sign_num in FIXED_SIGNS:
            base = compute_nth_sign(sign_num, 9)
        else:
            base = compute_nth_sign(sign_num, 5)

        div_sign = compute_nth_sign(base, part + 1)
        div_deg = degrees % amsa
        return div_sign, div_deg

    @staticmethod
    def calculate_division_chart(rasi_results, chart_name):
        function_map = {
            "D2": DivisionalCalculator.calculate_hora_d2,
            "D9": DivisionalCalculator.calculate_navamsa_d9,
        }

        if chart_name not in function_map:
            return rasi_results

        calc = function_map[chart_name]
        results = []

        for p in rasi_results:
            lon = p.get("longitude", 0)
            sign = int(lon / 30) + 1
            deg  = lon % 30

            new_sign, new_deg = calc(sign, deg)

            new_p = p.copy()
            new_p["longitude"] = (new_sign - 1) * 30 + new_deg
            results.append(new_p)

        return results
