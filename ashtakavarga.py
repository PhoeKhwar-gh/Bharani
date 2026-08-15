import swisseph as swe
from typing import Dict, List

class AshtakavargaCalculator:
    # ✅ ayanamsa_flag နဲ့ house_sys ကို parameter ထည့်ပါ
    def __init__(self, ayanamsa_flag: int = swe.SIDM_LAHIRI, house_sys: str = 'W'):
        """
        ayanamsa_flag: Ayanamsa အမျိုးအစား (swe.SIDM_LAHIRI, etc.)
        house_sys: House System ('W'=Whole Sign, 'E'=Vehlow Equal, 'P'=Placidus, etc.)
        """
        self.ayanamsa_flag = ayanamsa_flag
        self.house_sys = house_sys.encode() if isinstance(house_sys, str) else house_sys
        swe.set_sid_mode(self.ayanamsa_flag)
        
        # ✅ လဂ်အတွက် ဇယား (မူရင်းအတိုင်း)
        self.table = {
                # Sun (48 bindu)
                'sun': {
                    'sun': [1, 2, 4, 7, 8, 9, 10, 11],
                    'moon': [3, 6, 10, 11],
                    'mars': [1, 2, 4, 7, 8, 9, 10, 11],
                    'mercury': [3, 5, 6, 9, 10, 11, 12],
                    'jupiter': [5, 6, 9, 11],
                    'venus': [6, 7, 12],
                    'saturn': [1, 2, 4, 7, 8, 9, 10, 11],
                    'ascendant': [3, 4, 6, 10, 11, 12]
                },
                # Moon (49 bindu)
                'moon': {
                    'sun': [3, 6, 7, 8, 10, 11],
                    'moon': [1, 3, 6, 7, 10, 11],
                    'mars': [2, 3, 5, 6, 9, 10, 11],
                    'mercury': [1, 3, 4, 5, 7, 8, 10, 11],
                    'jupiter': [1, 4, 7, 8, 10, 11, 12],
                    'venus': [3, 4, 5, 7, 9, 10, 11],
                    'saturn': [3, 5, 6, 11],
                    'ascendant': [3, 6, 10, 11]
                },
                # Mars (39 bindu)
                'mars': {
                    'sun': [3, 5, 6, 10, 11],
                    'moon': [3, 6, 11],
                    'mars': [1, 2, 4, 7, 8, 10, 11],
                    'mercury': [3, 5, 6, 11],
                    'jupiter': [6, 10, 11, 12],
                    'venus': [6, 8, 11, 12],
                    'saturn': [1, 4, 7, 8, 9, 10, 11],
                    'ascendant': [1, 3, 6, 10, 11]
                },
                # Mercury (54 bindu)
                'mercury': {
                    'sun': [5, 6, 9, 11, 12],
                    'moon': [2, 4, 6, 8, 10, 11],
                    'mars': [1, 2, 4, 7, 8, 9, 10, 11],
                    'mercury': [1, 3, 5, 6, 9, 10, 11, 12],
                    'jupiter': [6, 8, 11, 12],
                    'venus': [1, 2, 3, 4, 5, 8, 9, 11],
                    'saturn': [1, 2, 4, 7, 8, 9, 10, 11],
                    'ascendant': [1, 2, 4, 6, 8, 10, 11]
                },
                # Jupiter (56 bindu)
                'jupiter': {
                    'sun': [1, 2, 3, 4, 7, 8, 9, 10, 11],
                    'moon': [2, 5, 7, 9, 11],
                    'mars': [1, 2, 4, 7, 8, 10, 11],
                    'mercury': [1, 2, 4, 5, 6, 9, 10, 11],
                    'jupiter': [1, 2, 3, 4, 7, 8, 10, 11],
                    'venus': [2, 5, 6, 9, 10, 11],
                    'saturn': [3, 5, 6, 12],
                    'ascendant': [1, 2, 4, 5, 6, 7, 9, 10, 11]
                },
                # Venus (52 bindu)
                'venus': {
                    'sun': [8, 11, 12],
                    'moon': [1, 2, 3, 4, 5, 8, 9, 11, 12],
                    'mars': [3, 5, 6, 9, 11, 12],
                    'mercury': [3, 5, 6, 9, 11],
                    'jupiter': [5, 8, 9, 10, 11],
                    'venus': [1, 2, 3, 4, 5, 8, 9, 10, 11],
                    'saturn': [3, 4, 5, 8, 9, 10, 11],
                    'ascendant': [1, 2, 3, 4, 5, 8, 9, 11]
                },
                # Saturn (39 bindu)
                'saturn': {
                    'sun': [1, 2, 4, 7, 8, 10, 11],
                    'moon': [3, 6, 11],
                    'mars': [3, 5, 6, 10, 11, 12],
                    'mercury': [6, 8, 9, 10, 11, 12],
                    'jupiter': [5, 6, 11, 12],
                    'venus': [6, 11, 12],
                    'saturn': [3, 5, 6, 11],
                    'ascendant': [1, 3, 4, 6, 10, 11]
                },
                # Ascendant (49 bindu)
                'ascendant': {
                    'sun': [3, 4, 6, 10, 11, 12],
                    'moon': [3, 6, 10, 11],
                    'mars': [1, 3, 6, 10, 11],
                    'mercury': [1, 2, 4, 6, 8, 10, 11],
                    'jupiter': [1, 2, 4, 5, 6, 7, 9, 10, 11],
                    'venus': [1, 2, 3, 4, 5, 8, 9, 11],
                    'saturn': [1, 3, 4, 6, 10, 11],
                    'ascendant': [3, 4, 6, 10, 11, 12]
                }
            }
        self.minor_planets = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'ascendant']
        self.signs = ['mesha','vrisha','mithuna','karka','simha','kanya','tula','vrischika','dhanu','makara','kumbha','meena']

    def sign_index(self, sign_name: str) -> int:
        return self.signs.index(sign_name.lower())

    def planet_sign(self, jd_ut: float, planet_id: int) -> str:
        swe.set_sid_mode(self.ayanamsa_flag)
        lon, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        sign_idx = int(lon[0] / 30) % 12
        return self.signs[sign_idx]

    def ascendant_sign(self, jd_ut: float, lat: float, lon: float) -> str:
        """✅ UI မှာရွေးထားတဲ့ House System ကိုသုံးပါ"""
        swe.set_sid_mode(self.ayanamsa_flag)
        # Get tropical house cusps and ascendant
        _, ascmc = swe.houses(jd_ut, lat, lon, self.house_sys)
        asc_lon = ascmc[0] % 360
        ayanamsa = swe.get_ayanamsa(jd_ut)
        # Sidereal conversion
        asc_sidereal = (asc_lon - ayanamsa) % 360
        sign_idx = int(asc_sidereal / 30) % 12
        return self.signs[sign_idx]

    def count_from_sign(self, start_sign: int, house_num: int) -> int:
        return (start_sign + house_num - 1) % 12

    def bhinnashtakavarga(self, main_planet: str, jd_ut: float, lat: float, lon: float) -> List[int]:
        if main_planet not in self.table:
            return [0] * 12
        bindu = [0] * 12
        
        # Pre-calculate all planet positions for efficiency and consistency
        positions = {}
        for minor in self.minor_planets:
            if minor == 'ascendant':
                positions[minor] = self.sign_index(self.ascendant_sign(jd_ut, lat, lon))
            else:
                minor_id = {'sun':swe.SUN, 'moon':swe.MOON, 'mars':swe.MARS,
                           'mercury':swe.MERCURY, 'jupiter':swe.JUPITER,
                           'venus':swe.VENUS, 'saturn':swe.SATURN}[minor]
                positions[minor] = self.sign_index(self.planet_sign(jd_ut, minor_id))

        for minor in self.minor_planets:
            minor_sign_idx = positions[minor]
            benefic_houses = self.table[main_planet][minor]
            for h in benefic_houses:
                target_sign_idx = self.count_from_sign(minor_sign_idx, h)
                bindu[target_sign_idx] += 1
        return bindu

    def sarvashtakavarga(self, jd_ut: float, lat: float, lon: float) -> List[int]:
        """
        Sarvashtakavarga (SAV) တွက်ချက်ခြင်း။
        Standard SAV သည် ဂြိုဟ် ၇ လုံး (Sun-Saturn) ၏ စုစုပေါင်းရမှတ် (337) သာ ဖြစ်ရပါမည်။
        လဂ်၏ BAV ကို ဇယားသီးသန့်တွင် ပြသသော်လည်း SAV ထဲတွင် ထည့်မပေါင်းရပါ။
        """
        total_bindu = [0] * 12
        for planet in ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn']:
            bindu = self.bhinnashtakavarga(planet, jd_ut, lat, lon)
            for i in range(12):
                total_bindu[i] += bindu[i]
        return total_bindu

    def _format_for_chart(self, scores_12):
        key_map = {
            0: "TM", 1: "TL_top", 2: "TL_left", 3: "ML", 4: "BL_left",
            5: "BL_bottom", 6: "BM", 7: "BR_bottom", 8: "BR_right",
            9: "MR", 10: "TR_right", 11: "TR_top"
        }
        formatted = {}
        for i, score in enumerate(scores_12):
            key = key_map.get(i, f"pos_{i}")
            formatted[key] = str(score)
        return formatted

    def calculate_all_for_widget(self, jd: float, lat: float, lon: float):
        result = {}
        result['SAV'] = self._format_for_chart(self.sarvashtakavarga(jd, lat, lon))
        
        planet_map = {
            'sun': '☉', 'moon': '☽', 'mars': '♂', 'mercury': '☿',
            'jupiter': '♃', 'venus': '♀', 'saturn': '♄', 'ascendant': 'လဂ်'
        }
        for p_key, p_symbol in planet_map.items():
            result[p_symbol] = self._format_for_chart(self.bhinnashtakavarga(p_key, jd, lat, lon))
        return result

    def print_table(self, bindu: List[int], planet_name: str = ""):
        signs_mm = ['မိဿ','ပြိဿ','မေထုန်','ကရကဋ်','သိဟ်','ကန်','တူ','ဗြိစ္ဆာ','ဓနု','မကာရ','ကုမ်','မိန်']
        print(f"\n{planet_name} Bhinnashtakavarga:")
        print("ရာသီ    | ဗိန္ဓု")
        for i, b in enumerate(bindu):
            print(f"{signs_mm[i]:6} | {b:2d} ({'ကောင်း' if b >=4 else 'နည်း'})")