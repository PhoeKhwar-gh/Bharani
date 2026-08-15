"""
DivisionalChartCalculator.py - D1-D60 အထိ Divisional Charts တွက်ချက်ရန် Class
အသုံး: from DivisionalChartCalculator import DivisionalChartCalculator
calculator = DivisionalChartCalculator()
chart_data = calculator.calculate(jd, lat, lon, house_flag=b'W')
"""

import swisseph as swe
from ToDel_divisional_calculations import DivisionalCalculator
from typing import Dict, List, Tuple, Optional
import math

class DivisionalChartCalculator:
    def __init__(self, sid_mode: int = swe.SIDM_LAHIRI, ephe_path: Optional[str] = None):
        """
        မြန်မာ Pon Na အတွက် စံနှုန်း ဆက်တင်များ
        sid_mode: 1 = Lahiri (အကောင်းဆုံး), house_flag: b'W' = Whole Sign
        """
        swe.set_ephe_path(ephe_path)  # ephe files path
        swe.set_sid_mode(sid_mode, 0, 0)  # Lahiri sidereal
        
        # ဂြိုဟ် ID များ (True Rahu/Ketu အပါအဝင်)
        self.planets = {
            'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
            'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
            'Venus': swe.VENUS, 'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE  # True node လိုရင် FLG_TRUE_NODE
        }
        self.burmese_names = {
            swe.SUN: '၁', swe.MOON: '၂', swe.MARS: '၃', swe.MERCURY: '၄',
            swe.JUPITER: '၅', swe.VENUS: '၆', swe.SATURN: '၀',
            swe.MEAN_NODE: '၈'
        }

    def get_planet_positions(self, jd_ut: float, flags: int = swe.FLG_SWIEPH | swe.FLG_SIDEREAL) -> Dict[int, float]:
        """ဂြိုဟ် sidereal longitude များ ရယူခြင်း (degree)"""
        positions = {}
        for planet_id in self.planets.values():
            if planet_id == swe.MEAN_NODE:  # Rahu
                lon, speed = swe.calc_ut(jd_ut, planet_id, flags)[0]
                positions[planet_id] = lon[0] % 360
                # Ketu = Rahu + 180°
                ketu_lon = (lon[0] + 180) % 360
                positions[swe.KETU] = ketu_lon if 'Ketu' not in positions else positions[swe.KETU]
            else:
                lon, _ = swe.calc_ut(jd_ut, planet_id, flags)[0]
                positions[planet_id] = lon[0] % 360
        return positions

    def calculate_divisional(self, jd_ut: float, lat: float, lon: float, 
                           house_flag: bytes = b'W', div_num: int = 1) -> Dict:
        """
        D# chart တွက်ချက်ခြင်း
        div_num: 1=D1, 3=D3, 9=D9, 60=D60
        """
        # Houses (Whole Sign အကောင်းဆုံး)
        houses = swe.houses_ex(jd_ut, lat, lon, house_flag)[0]
        cusps = houses[:13]  # 12 houses + asc
        
        # Planets
        planet_lons = self.get_planet_positions(jd_ut)
        
        # Divisional positions (longitude / div_num)
        div_positions = {}
        for p_id, plon in planet_lons.items():
            div_lon = (plon / div_num) % 30  # Each sign 30° in varga
            div_sign = int((plon / 30) % 12)  # Rasi index 0-11
            div_house = self.get_house(div_lon + div_sign * 30, houses)
            div_positions[p_id] = {
                'sign': div_sign, 'degree': div_lon,
                'house': div_house, 'lon': plon
            }
        
        # Ayanamsa
        ayan = swe.get_ayanamsa_ut(jd_ut)
        
        return {
            'jd': jd_ut, 'houses': cusps, 'planets': div_positions,
            'ayanamsa': ayan, 'div_num': div_num
        }

    def get_house(self, longitude: float, houses: List[float]) -> int:
        """Longitude အရ House ရှာခြင်း (Whole Sign)"""
        sign = int(longitude / 30)
        return sign % 12 + 1  # House 1-12

    def get_all_divisions(self, jd_ut: float, lat: float, lon: float, 
                         house_flag: bytes = b'W') -> Dict[int, Dict]:
        """D1-D60 အားလုံး တွက်ချက်ခြင်း"""
        charts = {}
        for d in range(1, 61):  # D1 to D60
            charts[f'D{d}'] = self.calculate_divisional(jd_ut, lat, lon, house_flag, d)
        return charts

    def print_chart_summary(self, chart_data: Dict, burmese: bool = True):
        """Chart အကျဉ်း ပုံနှိပ်ခြင်း"""
        d_num = chart_data['div_num']
        print(f"\n=== D{d_num} Chart ===")
        print(f"Ayanamsa: {chart_data['ayanamsa']:.2f}°")
        print("Planet | Sign | Deg | House")
        for p_id, data in chart_data['planets'].items():
            name = self.burmese_names.get(p_id, f'P{p_id}')
            print(f"{name} | {data['sign']} | {data['degree']:.1f}° | {data['house']}")

# အသုံးပြုနည်း main.py မှာ
"""
from DivisionalChartCalculator import DivisionalChartCalculator
import swisseph as swe

calc = DivisionalChartCalculator(sid_mode=swe.SIDM_LAHIRI)

# ဥပမာ JD (1974-06-16 21:55 ကျောက်မဲ)
jd = swe.julday(1974, 6, 16, 21.9167 - 6.5/24)  # Local to UT
lat, lon = 22.0437, 97.0337  # ကျောက်မဲ

# D9 တွက်ခြင်း
d9_chart = calc.calculate_divisional(jd, lat, lon, b'W', 9)
calc.print_chart_summary(d9_chart)

# အားလုံး D1-D60
all_charts = calc.get_all_divisions(jd, lat, lon, b'W')
print(f"Total charts calculated: {len(all_charts)}")
"""

# Usage notes:
# pip install pyswisseph PyQt5
# ephe files download: https://www.astro.com/ftp/swisseph/ephe/
# Default: Lahiri + Whole Sign (Pon Na စံ)
# main.py မှ import သုံးပါ [cite:80][cite:82]

class DivisionalModel:
    @staticmethod
    def calculate(rasi_results: List[Dict], chart_name: str) -> List[Dict]:
        return DivisionalCalculator.calculate_division_chart(rasi_results, chart_name)
