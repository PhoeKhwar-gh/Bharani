# yuga_calculator.py
from datetime import datetime

class YugaCalculator:
    """
    Vedic Yuga Calculation System
    Swiss Ephemeris Julian Day (JD) ကို အသုံးပြု တိကျစွာ တွက်ချက်ခြင်း
    """
    
    # Kali Yuga စတင်သည့် Julian Day (Feb 18, 3102 BCE Julian / Jan 23, 3102 BCE Gregorian)
    KALI_YUGA_START_JD = 588465.5
    
    # ယုဂ်များ၏ သက်တမ်း (နှစ်)
    YUGA_DURATIONS = {
        'Satya': 1728000,
        'Treta': 1296000,
        'Dvapara': 864000,
        'Kali': 432000
    }
    MAHA_YUGA_TOTAL = 4320000
    
    # ယုဂ်အုပ်စိုးဂြိုဟ်
    YUGA_LORDS = {
        'Satya': 'Jupiter (ကြာသပတေး)',
        'Treta': 'Sun (နေ)',
        'Dvapara': 'Venus (သောကြာ)',
        'Kali': 'Saturn (စနေ)'
    }

    @staticmethod
    def get_yuga_html(jd):
        """
        ပေးထားသော Julian Day အတွက် ုဂ်အချက်အလက် HTML ြင့် ပြန်ပေးခြင်း
        """
        try:
            # ကလီယုဂ်စတင်ချိန်မှ ကြာမြင့်သော နေ့ရက်များ
            days_elapsed = jd - YugaCalculator.KALI_YUGA_START_JD
            years_elapsed = days_elapsed / 365.25
            
            # လက်ရှိ ယုဂ်ကို ရှာဖွေခြင်း
            yuga_name, years_in_yuga, progress = YugaCalculator._find_current_yuga(years_elapsed)
            
            lord = YugaCalculator.YUGA_LORDS.get(yuga_name, "Unknown")
            
            # HTML Format ဖြင့် ပြန်ထုတ်ခြင်း
            html = f"""
            <div style="background:#f0f4f8; padding:8px; border-radius:5px; border-left: 4px solid #2c3e50; margin-top:5px;">
                <p style="margin:2px; font-weight:bold; color:#2c3e50; font-size:11pt;"> ယုဂ်အချက်အလက် (Yuga Info)</p>
                <p style="margin:2px; color:#555;">• <b>လက်ရှိယုဂ်:</b> {yuga_name}</p>
                <p style="margin:2px; color:#555;">• <b>ယုဂ်အုပ်စိုး:</b> {lord}</p>
                <p style="margin:2px; color:#555;">• <b>ကြာမြင့်ချိန်:</b> {years_in_yuga:,.0f} နှစ် ({progress:.2f}%)</p>
            </div>
            """
            return html
            
        except Exception as e:
            return f"<p style='color:red;'>Yuga Error: {str(e)}</p>"

    @classmethod
    def _find_current_yuga(cls, years_elapsed):
        """
        နှစ်အရေအတွက်အရ လက်ရှိယုဂ်ကို သတ်မှတ်ခြင်း
        (အတိတ်နှင့် အနာဂတ် နှစ်မျိုးလုံး အလုပ်လုပ်သည်)
        """
        # အနာဂတ် (Kali Yuga စတင်ပြီးနောက်)
        if years_elapsed >= 0:
            if years_elapsed < cls.YUGA_DURATIONS['Kali']:
                return 'Kali (ကလီ)', years_elapsed, (years_elapsed / cls.YUGA_DURATIONS['Kali']) * 100
            elif years_elapsed < cls.YUGA_DURATIONS['Kali'] + cls.YUGA_DURATIONS['Satya']:
                rem = years_elapsed - cls.YUGA_DURATIONS['Kali']
                return 'Satya (သတျာ)', rem, (rem / cls.YUGA_DURATIONS['Satya']) * 100
            # ... (လိုအပ်ပါက Treta/Dvapara ထပ်ထည့်နိုင်)
            else:
                return 'Next Cycle', years_elapsed, 0

        # အတိတ် (Kali Yuga စတင်ခါနီး)
        else:
            abs_years = abs(years_elapsed)
            if abs_years < cls.YUGA_DURATIONS['Dvapara']:
                # Dvapara  အဆုံးပိုင်း
                rem = cls.YUGA_DURATIONS['Dvapara'] - abs_years
                return 'Dvapara (ဒွာပရ)', rem, (rem / cls.YUGA_DURATIONS['Dvapara']) * 100
            elif abs_years < cls.YUGA_DURATIONS['Dvapara'] + cls.YUGA_DURATIONS['Treta']:
                rem = (cls.YUGA_DURATIONS['Dvapara'] + cls.YUGA_DURATIONS['Treta']) - abs_years
                return 'Treta (တြေတာ)', rem, (rem / cls.YUGA_DURATIONS['Treta']) * 100
            else:
                return 'Satya (သတျာ)', 0, 0