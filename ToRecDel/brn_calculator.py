# brn_calculator.py အတွက် အဆင့်မြှင့်တင်ရန်

class ChartCalculator:
    def __init__(self):
        # ... existing code ...
        
        # Sign classifications
        self.MOVABLE_SIGNS = [1, 4, 7, 10]  # Aries, Cancer, Libra, Capricorn
        self.FIXED_SIGNS = [2, 5, 8, 11]    # Taurus, Leo, Scorpio, Aquarius
        self.DUAL_SIGNS = [3, 6, 9, 12]     # Gemini, Virgo, Sagittarius, Pisces
        self.ODD_SIGNS = [1, 3, 5, 7, 9, 11]
        self.EVEN_SIGNS = [2, 4, 6, 8, 10, 12]
    
    def calculate_navamsa_d9(self, sign_num, degrees):
        """D9 - Navamsa calculation (Vedic method)"""
        amsa = 3 + 20/60.0  # 3.3333°
        compartment = int(degrees / amsa)  # 0-8
        
        if sign_num in self.MOVABLE_SIGNS:  # Movable
            base_start = sign_num
        elif sign_num in self.FIXED_SIGNS:  # Fixed
            base_start = self.compute_nth_sign(sign_num, 9)
        else:  # Dual
            base_start = self.compute_nth_sign(sign_num, 5)
        
        div_sign_num = self.compute_nth_sign(base_start, compartment + 1)
        div_deg = degrees % amsa
        return div_sign_num, div_deg
    
    def calculate_division_chart(self, rasi_results, chart_name):
        """Calculate division chart using proper Vedic formulas"""
        # ... implementation ...