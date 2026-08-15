"""
Ashtakavarga Calculator - Bhinnashtakavarga (BAV) & Sarvashtakavarga (SAV)
User Provided Table အတိအကျ အသုံးပြုထားသည်။
"""

class AshtakavargaCalculator:
    """Ashtakavarga တွက်ချက်ခြင်း"""

    def __init__(self):
        # ဂြိုဟ်ကနေ ကြည့်ရင် အကျိုးပေး ရာသီ (1-12) - User Provided Table
        self.table = {
            # Sun (48 bindu)
            'sun': {
                'sun': [1,2,4,7,8,9,10,11],
                'moon': [3,6,10,11],
                'mars': [1,2,4,7,8,9,10,11],
                'mercury': [3,5,6,9,10,11,12],
                'jupiter': [5,6,9,11],
                'venus': [6,7,12],
                'saturn': [1,2,4,7,8,9,10,11],
                'ascendant': [3,4,6,10,11,12]
            },
            # Moon (49 bindu)
            'moon': {
                'sun': [3,6,7,8,10,11],
                'moon': [1,3,6,7,10,11],
                'mars': [2,3,5,6,9,10,11],
                'mercury': [1,3,4,5,7,8,10,11],
                'jupiter': [1,4,7,8,10,11,12],
                'venus': [3,4,5,7,9,10,11],
                'saturn': [3,5,6,11],
                'ascendant': [3,6,10,11]
            },
            # Mars (39 bindu)
            'mars': {
                'sun': [3,5,6,10,11],
                'moon': [3,6,11],
                'mars': [1,2,4,7,8,10,11],
                'mercury': [3,5,6,11],
                'jupiter': [6,10,11,12],
                'venus': [6,8,11,12],
                'saturn': [1,4,7,8,9,10,11],
                'ascendant': [1,3,6,10,11]
            },
            # Mercury (54 bindu)
            'mercury': {
                'sun': [5,6,9,11,12],
                'moon': [2,4,6,8,10,11],
                'mars': [1,2,4,7,8,9,10,11],
                'mercury': [1,3,5,6,9,10,11,12],
                'jupiter': [6,8,11,12],
                'venus': [1,2,3,4,5,8,9,11],
                'saturn': [1,2,4,7,8,9,10,11],
                'ascendant': [1,2,4,6,8,10,11]
            },
            # Jupiter (56 bindu)
            'jupiter': {
                'sun': [1,2,3,4,7,8,9,10,11],
                'moon': [2,5,7,9,11],
                'mars': [1,2,4,7,8,10,11],
                'mercury': [1,2,4,5,6,9,10,11],
                'jupiter': [1,2,3,4,7,8,10,11],
                'venus': [2,5,6,9,10,11],
                'saturn': [3,5,6,12],
                'ascendant': [1,2,4,5,6,7,9,10,11]
            },
            # Venus (52 bindu)
            'venus': {
                'sun': [8,11,12],
                'moon': [1,2,3,4,5,8,9,11,12],
                'mars': [3,5,6,9,11,12],
                'mercury': [3,5,6,9,11],
                'jupiter': [5,8,9,10,11],
                'venus': [1,2,3,4,5,8,9,10,11],
                'saturn': [3,4,5,8,9,10,11],
                'ascendant': [1,2,3,4,5,8,9,11]
            },
            # Saturn (39 bindu)
            'saturn': {
                'sun': [1,2,4,7,8,10,11],
                'moon': [3,6,11],
                'mars': [3,5,6,10,11,12],
                'mercury': [6,8,9,10,11,12],
                'jupiter': [5,6,11,12],
                'venus': [6,11,12],
                'saturn': [3,5,6,11],
                'ascendant': [1,3,4,6,10,11]
            }
        }
        
        # Contributors list (ဂြိုဟ် ၇ လုံး + လဂ်)
        self.contributors = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'ascendant']

    def calculate_bav(self, target_planet, planet_positions):
        """
        Bhinnashtakavarga (BAV) တွက်ချက်ခြင်း
        
        Args:
            target_planet: ဘယ်ဂြိုဟ်အတွက် BAV တွက်မလဲ (e.g., 'sun')
            planet_positions: ဂြိုဟ်အားလုံး၏ ရာသီနေရာများ {planet_name: sign_index_0_to_11}
            
        Returns: [12 integers] - ရာသီ ၁၂ ခုအတွက် ဗိန္ဒုအမှတ်များ (Index 0 = Aries)
        """
        bav_scores = [0] * 12
        target_key = target_planet.lower()
        
        if target_key not in self.table:
            return bav_scores

        # Contributor ဂြိုဟ်တစ်ခုချင်းစီမှ ဗိန္ဒုပေးပုံ တွက်ချက်ခြင်း
        for contributor_key in self.contributors:
            # Contributor ဂြိုဟ်၏ ရာသီအညွှန်း (0-11) ကို ရယူခြင်း
            # ဂြိုဟ်အမည်ကို lowercase သို့ ပြောင်းပြီး ရှာဖွေခြင်း
            contributor_key_lower = contributor_key.lower()
            contributor_sign_index = planet_positions.get(contributor_key_lower, 0)
            
            # ဇယားမှ Favorable Houses (1-12) ကို ရယူခြင်း
            # Table Keys များကို lowercase ဖြင့် ရှာဖွေခြင်း
            favorable_houses = self.table[target_key].get(contributor_key_lower, [])
            
            for house_num in favorable_houses:
                # house_num သည် 1-based (1-12)
                # contributor_sign_index သည် 0-based (0-11)
                # ပစ်မှတ်ရာသီကို တွက်ချက်ခြင်း
                target_sign_index = (contributor_sign_index + house_num - 1) % 12
                bav_scores[target_sign_index] += 1
                
        return bav_scores

    def calculate_sav(self, planet_positions):
        """
        Sarvashtakavarga (SAV) တွက်ချက်ခြင်း
        ဂြိုဟ် ၇ လုံး၏ BAV များကို ပေါင်းစပ်ခြင်း
        """
        sav_scores = [0] * 12
        
        planets_to_sum = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn']
        
        for planet in planets_to_sum:
            bav = self.calculate_bav(planet, planet_positions)
            for i in range(12):
                sav_scores[i] += bav[i]
                
        return sav_scores

    def calculate_all_for_widget(self, planet_positions):
        """
        Widget အတွက် ဒေတာပြင်ဆင်ခြင်း
        
        Returns: dict with keys: SAV, As, Su, Mo, Ma, Me, Ju, Ve, Sa
        """
        result = {}
        
        # 1. SAV (Sarvashtakavarga)
        sav_scores = self.calculate_sav(planet_positions)
        result['SAV'] = self._format_for_chart(sav_scores)
        
        # 2. BAV for each planet and Lagna
        # Widget မှာ ပြသမည့် အမည်များ (Symbols)
        planet_keys = {
            'sun': '☉', 'moon': '☽', 'mars': '♂', 'mercury': '☿', 
            'jupiter': '♃', 'venus': '♀', 'saturn': '♄', 'ascendant': 'လဂ်'
        }
        
        for p_key, p_symbol in planet_keys.items():
            bav_scores = self.calculate_bav(p_key, planet_positions)
            result[p_symbol] = self._format_for_chart(bav_scores)
            
        return result

    def _format_for_chart(self, scores_12):
        """
        12-element list (Index 0-11) ကို Widget ၏ key format သို့ ပြောင်းလဲခြင်း
        
        North Indian Chart Layout Mapping:
        - 0 (Aries) -> TM (Top Middle)
        - 1 (Taurus) -> TL_top (Top Left, Top Triangle)
        - 2 (Gemini) -> TL_left (Top Left, Bottom Triangle)
        - 3 (Cancer) -> ML (Middle Left)
        - 4 (Leo) -> BL_left (Bottom Left, Top Triangle)
        - 5 (Virgo) -> BL_bottom (Bottom Left, Bottom Triangle)
        - 6 (Libra) -> BM (Bottom Middle)
        - 7 (Scorpio) -> BR_bottom (Bottom Right, Bottom Triangle)
        - 8 (Sagittarius) -> BR_right (Bottom Right, Top Triangle)
        - 9 (Capricorn) -> MR (Middle Right)
        - 10 (Aquarius) -> TR_right (Top Right, Bottom Triangle)
        - 11 (Pisces) -> TR_top (Top Right, Top Triangle)
        """
        key_map = {
            0: "TM",          # Aries
            1: "TL_top",      # Taurus
            2: "TL_left",     # Gemini
            3: "ML",          # Cancer
            4: "BL_left",     # Leo
            5: "BL_bottom",   # Virgo
            6: "BM",          # Libra
            7: "BR_bottom",   # Scorpio
            8: "BR_right",    # Sagittarius
            9: "MR",          # Capricorn
            10: "TR_right",   # Aquarius
            11: "TR_top"      # Pisces
        }
        
        formatted = {}
        for i, score in enumerate(scores_12):
            key = key_map.get(i, f"pos_{i}")
            formatted[key] = str(score)
            
        return formatted