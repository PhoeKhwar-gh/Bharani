"""
DivisionalChartCalculator.py - D1-D60 အထိ Divisional Charts တွက်ချက်ရန် Class
အသုံး: from divisionChart import DivisionalChartCalculator
calculator = DivisionalChartCalculator()
chart_data = calculator.calculate_divisional(jd, lat, lon, house_flag=b'W', div_num=9)
"""
import swisseph as swe
from typing import Dict, Optional

class DivisionalChartCalculator:
    def __init__(self, sid_mode: int = swe.SIDM_LAHIRI, ephe_path: Optional[str] = None):
        """မြန်မာ Pon Na အတွက် စံနှုန်း ဆက်တင်များ"""
        if ephe_path:
            swe.set_ephe_path(ephe_path)
        swe.set_sid_mode(sid_mode, 0, 0)

        self.planets = {
            'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
            'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
            'Venus': swe.VENUS, 'Saturn': swe.SATURN,
            'Rahu': swe.TRUE_NODE
        }

        self.burmese_names = {
            swe.SUN: '၁', swe.MOON: '၂', swe.MARS: '၃', swe.MERCURY: '၄',
            swe.JUPITER: '၅', swe.VENUS: '၆', swe.SATURN: '၇',
            swe.TRUE_NODE: '၈', 100: '၉'  # Ketu အတွက် Custom ID 100
        }

    def get_planet_positions(self, jd_ut: float, flags: int = swe.FLG_SWIEPH | swe.FLG_SIDEREAL) -> Dict[int, float]:
        """ဂြိုဟ် sidereal longitude များ ရယူခြင်း"""
        positions = {}
        flags |= swe.FLG_TRUE_NODE
        
        for planet_id in self.planets.values():
            result = swe.calc_ut(jd_ut, planet_id, flags)
            lon = result[0][0] % 360
            positions[planet_id] = lon
            
            if planet_id in [swe.TRUE_NODE, swe.MEAN_NODE]:
                positions[100] = (lon + 180) % 360  # Ketu တွက်ထည့်ခြင်း
                
        return positions

    def calculate_divisional(self, jd_ut: float, lat: float, lon: float, 
                             house_flag: bytes = b'W', div_num: int = 1) -> Dict:
        """D# chart တွက်ချက်ခြင်း (div_num: 1=D1, 9=D9, 60=D60)"""
        # Houses (Whole Sign)
        houses = swe.houses_ex(jd_ut, lat, lon, house_flag)[0]
        cusps = houses[:13]
        
        # Planets
        planet_lons = self.get_planet_positions(jd_ut)
        
        # ✅ မှန်ကန်သော Varga တွက်ချက်နည်း
        div_positions = {}
        for p_id, plon in planet_lons.items():
            div_total_lon = (plon * div_num) % 360
            div_sign = int(div_total_lon / 30)
            div_degree = div_total_lon % 30
            
            # Whole Sign House Logic (D1 Lagna ကို House 1 အဖြစ်ထား)
            asc_sign = int(houses[0] / 30)
            house_num = ((div_sign - asc_sign) % 12) + 1
            
            div_positions[p_id] = {
                'sign': div_sign,
                'degree': div_degree,
                'house': house_num,
                'lon': plon
            }
        
        ayan = swe.get_ayanamsa_ut(jd_ut)
        
        return {
            'jd': jd_ut, 'houses': cusps, 'planets': div_positions,
            'ayanamsa': ayan, 'div_num': div_num
        }

    def get_all_divisions(self, jd_ut: float, lat: float, lon: float, 
                          house_flag: bytes = b'W') -> Dict[str, Dict]:
        """D1-D60 အားလုံး တွက်ချက်ခြင်း"""
        return {f'D{d}': self.calculate_divisional(jd_ut, lat, lon, house_flag, d) for d in range(1, 61)}

    def print_chart_summary(self, chart_data: Dict, burmese: bool = True):
        """Chart အကျဉ်း ပုံနှိပ်ခြင်း"""
        d_num = chart_data['div_num']
        print(f"\n=== D{d_num} Chart (Ayanamsa: {chart_data['ayanamsa']:.2f}°) ===")
        print(f"{'ဂြိုဟ်':<5} | {'ရာသီ':<5} | {'ဒီဂရီ':<7} | {'ဘာဝ':<4}")
        print("-" * 40)
        for p_id, data in chart_data['planets'].items():
            name = self.burmese_names.get(p_id, f'P{p_id}')
            print(f"{name:<5} | {data['sign']:<5} | {data['degree']:<7.1f}° | {data['house']:<4}")