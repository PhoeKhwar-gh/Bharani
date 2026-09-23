import sys
import re
from datetime import datetime
from myanmar_calendar import ceMmDateTime, ceMmTranslate

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_date(date_str):
    if not DATE_PATTERN.fullmatch(date_str):
        raise ValueError("Date must use YYYY-MM-DD format")
    return datetime.strptime(date_str, "%Y-%m-%d")


def get_mm_formatted_date(date_str):
    # ရက်စွဲကို Parse လုပ်ခြင်း
    dt = parse_date(date_str)
    y, m, d = dt.year, dt.month, dt.day
    
    # Myanmar Date Object ဖန်တီးခြင်း (မြန်မာစံတော်ချိန် UTC+6.5)
    mm_date = ceMmDateTime.from_gregorian(y, m, d, tz=6.5)
    translator = ceMmTranslate()
    
    # ၁။ မြန်မာနှစ် (ဂဏန်းများကို မြန်မာဂဏန်းသို့ ပြောင်းခြင်း)
    my_year_mm = translator.T(str(mm_date.my), 1, 0) + " ခု"
    
    # ၂။ မြန်မာလ
    mm_months = ["တန်ခူး", "ကဆုန်", "နယုန်", "ဝါဆို", "ဝါခေါင်", "တော်သလင်း", 
                 "သီတင်းကျွတ်", "တန်ဆောင်မုန်း", "နတ်တော်", "ပြာသို", "တပို့တွဲ", "တပေါင်း"]
    mm = mm_date.mm
    myt = mm_date.myt
    
    # ဝါထပ်နှစ်တွင် ဝါဆိုလကို ဒုတိယဝါဆိုဟု သတ်မှတ်ခြင်း
    if mm == 4 and myt > 0:
        mm_month = "ဒုတိယ ဝါဆို"
    elif mm == 13:
        mm_month = "နှောင်းတန်ခူး"
    else:
        mm_month = mm_months[mm - 1]
        
    # ၃။ လဆန်း/လပြည့်/လဆုတ်/လကွယ်
    mp_names = ["လဆန်း", "လပြည့်", "လဆုတ်", "လကွယ်"]
    mm_moon = mp_names[mm_date.mp]
    
    # ၄။ ရက် (မြန်မာဂဏန်းသို့ ပြောင်းခြင်း)
    mm_mf = translator.T(str(mm_date.mf), 1, 0) + " ရက်"
    moon_day = "" if mm_date.mp in (1, 3) else f" {mm_mf}"
    
    # ၅။ နေ့ (တနင်္ဂနွေနေ့ စသည်ဖြင့်)
    w_names = ["စနေ", "တနင်္ဂနွေ", "တနင်္လာ", "အင်္ဂါ", "ဗုဒ္ဓဟူး", "ကြာသပတေး", "သောကြာ"]
    mm_w = w_names[mm_date.w] + "နေ့"
    
    # ပုံစံတကျ ပေါင်းစပ်ခြင်း
    result = f"{my_year_mm} ၊ {mm_month}{mm_moon}{moon_day} - {mm_w}"
    return result

def main():
    print("=" * 55)
    print("  English Date to Myanmar Date Converter")
    print("=" * 55)
    print("အင်္ဂလိပ်ရက်စွဲထည့်ပါ (ဥပမာ - 1974-06-16)")
    print("ဘာမှမထည့်ဘဲ Enter နှိပ်ပါက ယနေ့ရက်စွဲကို တွက်ချက်ပေးပါမည်။")
    print("-" * 55)
    
    date_input = input("Date (YYYY-MM-DD): ").strip()
    
    if not date_input:
        today = datetime.now()
        date_input = today.strftime("%Y-%m-%d")
        
    try:
        # ရက်စွဲပုံစံ မှန်ကန်မှု ရှိ/မရှိ စစ်ဆေးခြင်း
        parse_date(date_input)
        result = get_mm_formatted_date(date_input)
        print(f"\n✅ Result : {result}")
    except ValueError:
        print("\n[Error] ရက်စွဲပုံစံ မှားယွင်းနေပါသည်။ YYYY-MM-DD ပုံစံဖြင့် ထည့်သွင်းပါ။")

if __name__ == "__main__":
    main()