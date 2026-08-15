# narayana_dasha.py
from datetime import datetime, timedelta

class NarayanaDashaCalculator:
    """Jaimini Narayana Dasha တွက်ချက်မှု Class"""
    
    SIGN_NAMES_MM = ["မိဿ", "ပြိဿ", "‌မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်",
                     "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုံ", "မိန်"]
    SIGN_LORDS = {
        0:'Mars', 1:'Venus', 2:'Mercury', 3:'Moon', 4:'Sun', 5:'Mercury',
        6:'Venus', 7:'Mars', 8:'Jupiter', 9:'Saturn', 10:'Saturn', 11:'Jupiter'
    }
    MOVABLE = [0, 3, 6, 9]   # မိဿ၊ ကရကဋ်၊ တူ၊ မကာရ
    FIXED   = [1, 4, 7, 10]  # ပြိဿ၊ သိဟ်၊ ဗြိစ္ဆာ၊ ကုံ
    DUAL    = [2, 5, 8, 11]  # မိထုန်၊ ကန်၊ ဓနု၊ မိန်

    def __init__(self, lagna_sign_idx, birth_dt):
        self.lagna = lagna_sign_idx
        self.birth_dt = birth_dt

    def _get_start_and_direction(self):
        """လဂ်နာအမျိုးအစားအလိုက် အစပြုရာသီနှင့် လားရာသတ်မှတ်ခြင်း"""
        if self.lagna in self.MOVABLE:
            return self.lagna, 1
        elif self.lagna in self.FIXED:
            return (self.lagna + 8) % 12, -1  # 9 လုံးမြောက်မှ နောက်ပြန်
        else:
            return (self.lagna + 4) % 12, 1   # 5 လုံးမြောက်မှ ရှေ့သို့

    def _get_duration_years(self, sign_idx, lord_positions):
        """ရာသီတစ်ခု၏ ဒဿာနှစ်အရေအတွက် တွက်ချက်ခြင်း"""
        lord_name = self.SIGN_LORDS[sign_idx]
        lord_sign = lord_positions.get(lord_name, 0)
        years = (sign_idx - lord_sign) % 12
        return 12 if years == 0 else years

    def calculate(self, planet_positions, levels=3):
        """
        Narayana Dasha အဆင့်ဆင့် တွက်ချက်ခြင်း
        planet_positions: {'Sun': 0, 'Moon': 1, ...} (Sign Index 0-11)
        """
        start_sign, direction = self._get_start_and_direction()
        result = []
        current_date = self.birth_dt
        main_sign = start_sign

        for _ in range(12):
            years = self._get_duration_years(main_sign, planet_positions)
            end_date = current_date + timedelta(days=years * 365.25)

            main_period = {
                'sign_idx': main_sign, 'sign_name': self.SIGN_NAMES_MM[main_sign],
                'start': current_date, 'end': end_date, 'years': years, 'antardashas': []
            }

            # အန္တရဒဿာ (Antardasha) - ရာသီ ၁၂ ခုစာ ခွဲခြားခြင်း
            if levels >= 2:
                antar_sign = main_sign
                antar_start = current_date
                antar_dur = years / 12.0  # တိကျမှုအတွက် အချိုးညီခွဲဝေခြင်း

                for _ in range(12):
                    antar_end = antar_start + timedelta(days=antar_dur * 365.25)
                    antar_period = {
                        'sign_idx': antar_sign, 'sign_name': self.SIGN_NAMES_MM[antar_sign],
                        'start': antar_start, 'end': antar_end, 'years': antar_dur, 'pratyantardashas': []
                    }

                    # ပြတန္တရဒဿာ (Pratyantardasha)
                    if levels >= 3:
                        praya_sign = antar_sign
                        praya_start = antar_start
                        praya_dur = antar_dur / 12.0
                        
                        for _ in range(12):
                            praya_end = praya_start + timedelta(days=praya_dur * 365.25)
                            antar_period['pratyantardashas'].append({
                                'sign_idx': praya_sign, 'sign_name': self.SIGN_NAMES_MM[praya_sign],
                                'start': praya_start, 'end': praya_end, 'years': praya_dur
                            })
                            praya_start = praya_end
                            praya_sign = (praya_sign + direction) % 12

                    main_period['antardashas'].append(antar_period)
                    antar_start = antar_end
                    antar_sign = (antar_sign + direction) % 12

            result.append(main_period)
            current_date = end_date
            main_sign = (main_sign + direction) % 12

        return result