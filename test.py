import sys
from datetime import datetime

# myanmar_calendar.py ဖိုင်နှင့် တစ်ဖိုင်တည်းရှိပါက အောက်ပါအတိုင်း import လုပ်ပါ
try:
    from myanmar_calendar import ceMmDateTime, ceMmTranslate
except ImportError:
    print("Error: 'myanmar_calendar.py' ဖိုင်ကို မတွေ့ပါ။ ဤ test.py နှင့် တစ်ဖိုင်တည်းတွင် ရှိမရှိ စစ်ဆေးပါ။")
    sys.exit(1)

def main():
    print("=" * 40)
    print("  Myanmar Calendar Converter Test")
    print("=" * 40)
    print("အင်္ဂလိပ်ရက်စွဲထည့်ပါ (ဥပမာ - 2024-04-17)")
    print("ဘာမှမထည့်ဘဲ Enter နှိပ်ပါက ယနေ့ရက်စွဲကို တွက်ချက်ပေးပါမည်။")
    print("-" * 40)
    
    date_input = input("Date (YYYY-MM-DD): ").strip()
    
    if not date_input:
        today = datetime.now()
        year, month, day = today.year, today.month, today.day
    else:
        try:
            dt = datetime.strptime(date_input, "%Y-%m-%d")
            year, month, day = dt.year, dt.month, dt.day
        except ValueError:
            print("\n[Error] ရက်စွဲပုံစံ မှားယွင်းနေပါသည်။ YYYY-MM-DD ပုံစံဖြင့် ထည့်သွင်းပါ။")
            return

    print(f"\n📅 Gregorian Date : {year}-{month:02d}-{day:02d}")
    print("-" * 40)
    
    # Myanmar Date သို့ ပြောင်းလဲခြင်း (Myanmar Timezone UTC+6.5)
    mm_date = ceMmDateTime.from_gregorian(year, month, day, tz=6.5)
    
    # ရလဒ်များကို ဖော်ပြခြင်း
    print(f"🇲🇲 Myanmar Date   : {mm_date.ToMString('&yyyy ခုနှစ်၊ &M လ &P &ff ရက်')}")
    print(f"🔢 Myanmar Year   : {mm_date.my} ({mm_date.my_name})")
    print(f"🛕 Sasana Year    : {mm_date.sy}")
    print(f"🌙 Moon Phase     : {mm_date.mp} (0=လဆန်း, 1=လပြည့်, 2=လဆုတ်, 3=လကွယ်)")
    print(f"📆 Fortnight Day  : {mm_date.mf}")
    
    # နက္ခတ်နှင့် အထူးနေ့များ
    astro = mm_date.astro
    if astro:
        print(f"✨ Astrological  : {', '.join(astro)}")
    else:
        print("✨ Astrological  : None")
        
    print(f"🧭 Nagahle        : {mm_date.nagahle}")
    print(f"👑 Mahabote       : {mm_date.mahabote}")
    print(f"👹 Nakhat         : {mm_date.nakhat}")
    print(f"📿 Sabbath        : {mm_date.sabbath if mm_date.sabbath else 'None'}")
    
    # ရုံးပိတ်ရက်များ
    holidays = mm_date.holidays
    if holidays:
        print(f"🎉 Holidays       : {', '.join(holidays)}")
        
    print("=" * 40)

if __name__ == "__main__":
    main()