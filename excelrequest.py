import pandas as pd

# ------------------------------
# ၁. ဖိုင်ကို pandas ဖြင့်ဖတ်ခြင်း
# ------------------------------
filename = "Myanmar_PCodes.xlsm"

# ဖိုင်ရှိမရှိ စစ်ဆေးပါ
import os
if not os.path.exists(filename):
    print(f"❌ ဖိုင် {filename} မတွေ့ပါ။ ကျေးဇူးပြု၍ ဖိုင်ကို လက်ရှိလုပ်ကွက်ထဲ ထည့်ပါ။")
    exit()

# sheet_name=None ဖြင့် အားလုံးကိုဖတ်ပြီး စာမျက်နှာအမည်များကိုစစ်ဆေးပါ
xls = pd.ExcelFile(filename, engine='openpyxl')
print("📄 Sheet names:", xls.sheet_names)

# ပထမဆုံး sheet ကိုဖတ်ပါ (index 0)
df = xls.parse(sheet_name=0, engine='openpyxl')
print(f"\n📊 စုစုပေါင်းအတန်းအရေအတွက်: {len(df)}")
print("📋 ကော်လံအမည်များ:", df.columns.tolist())
print("\n🔍 ပထမ ၅ အတန်း:")
print(df.head())

# ------------------------------
# ၂. လိုချင်သော ကော်လံများကို ရှာဖွေခြင်း (သင့်တကယ့်ဖိုင်နှင့် ညှိပါ)
# ------------------------------
column_mapping = {
    'state': ['State/Region', 'State_Region', 'Region', 'State', 'တိုင်းဒေသကြီး/ပြည်နယ်'],
    'district': ['District', 'District Name', 'ခရိုင်'],
    'township': ['Township', 'Township Name', 'မြို့နယ်'],
    'village_tract': ['Village Tract', 'Village Tract Name', 'ကျေးရွာအုပ်စု'],
    'village': ['Village', 'Village Name', 'ကျေးရွာအုပ်စု', 'ကျေးရွာ'],
    'lat': ['Latitude', 'Lat', 'Y', 'လတ္တီကျု'],
    'lon': ['Longitude', 'Lon', 'Long', 'X', 'လောင်ဂျီကျု']
}

found_columns = {}
for target, candidates in column_mapping.items():
    for col in df.columns:
        if col in candidates:
            found_columns[target] = col
            break

print("\n✅ တွေ့ရှိသော ကော်လံအမည်များ:", found_columns)

# ------------------------------
# ၃. ဒေတာအသစ်ဖွဲ့စည်းခြင်း
# ------------------------------
selected = pd.DataFrame()
selected['country'] = 'Myanmar'

# State
if 'state' in found_columns:
    selected['state'] = df[found_columns['state']]
else:
    selected['state'] = ''

# City: မြို့နယ်ကို အဓိကထားသုံးပါ (တခါတရံ မြို့နယ်မှာ မြို့အမည်ပါတတ်သည်)
if 'township' in found_columns:
    selected['city'] = df[found_columns['township']]
else:
    selected['city'] = ''

# Village: ကျေးရွာအုပ်စု သို့မဟုတ် ကျေးရွာ
if 'village_tract' in found_columns:
    selected['village'] = df[found_columns['village_tract']]
elif 'village' in found_columns:
    selected['village'] = df[found_columns['village']]
else:
    selected['village'] = ''

# Latitude & Longitude
if 'lat' in found_columns:
    selected['latitude'] = df[found_columns['lat']]
else:
    selected['latitude'] = None

if 'lon' in found_columns:
    selected['longitude'] = df[found_columns['lon']]
else:
    selected['longitude'] = None

# အနည်းဆုံး state နှင့် city ရှိသောအတန်းများကိုသာ ထိန်းသိမ်းပါ
selected = selected.dropna(subset=['state', 'city'], how='all')

# ------------------------------
# ၄. ဒေတာကို CSV ဖိုင်အဖြစ်သိမ်းဆည်းခြင်း
# ------------------------------
output_file = "myanmar_locations.csv"
selected.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n✅ အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။ ဖိုင်အမည်: {output_file}")
print(f"📈 သိမ်းဆည်းထားသော အတန်းအရေအတွက်: {len(selected)}")
print("\n📌 နမူနာ ၁၀ အတန်း:")
print(selected.head(10))