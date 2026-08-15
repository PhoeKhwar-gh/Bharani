# brn_data_manager.py

import csv
import json
import os

class DataManager:
    """
    တိုင်း/ပြည်နယ်၊ မြို့နယ်၊ တည်နေရာ ဒေတာများနဲ့
    ဇာတာဒေတာများကို စီမံခန့်ခွဲပေးတဲ့ class ဖြစ်ပါတယ်။
    """
    def __init__(self):
        # CSV ဖိုင်ကနေ တည်နေရာဒေတာများကို စတင်ချိန်မှာပဲ ဖတ်ရှုထားပါတယ်။
        self.location_data = self._load_location_data()

    def _load_location_data(self):
        """
        'res/data/dataCSV.csv' ဖိုင်ကနေ တည်နေရာဒေတာများကို
        nested dictionary အဖြစ်ဖတ်ရှုပေးပါတယ်။
        ဥပမာ: {'State': {'City': {'lat': ..., 'lon': ...}}}
        """
        data = {}
        # ဖိုင်လမ်းကြောင်းကို လုံခြုံစွာ ရှာဖွေပေးပါတယ်
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'res', 'data', 'dataCSV.csv')
        
        try:
            # --- ဒီနေရာမှာ encoding ကို 'utf-8-sig' နဲ့ ပြောင်းလဲထားပါတယ် ---
            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # --- ဒီနေရာမှာ စစ်ဆေးမှုအသစ်ထည့်လိုက်ပါတယ် ---
                # CSV ဖိုင်ရဲ့ header ထဲမှာ လိုအပ်တဲ့ ကော်လံအမည်များ ရှိမရှိ စစ်ပါတယ်။
                required_columns = ['State', 'City', 'Latitude', 'Longitude']
                if not all(col in reader.fieldnames for col in required_columns):
                    print("CSV ဖိုင်ရဲ့ header တွင် လိုအပ်တဲ့ ကော်လံအမည် မပါရှိပါ။")
                    print(f"လိုအပ်တဲ့ ကော်လံများ: {required_columns}")
                    print(f"ဖိုင်ထဲမှာ တွေ့ရှိတဲ့ ကော်လံများ: {reader.fieldnames}")
                    print("dataCSV.csv ဖိုင်ရဲ့ ပထမအကြိမ် (header) ကို စစ်ဆေးပြီး အမည်များ ကိုက်ညီအောင် ပြင်ဆင်ပေးပါ။")
                    return {} # ဒေတာမရှိတော့ဘဲ ပြန်ထွက်သွားပါတယ်။
                
                for row in reader:
                    state = row['State']
                    city = row['City']
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])

                    if state not in data:
                        data[state] = {}
                    data[state][city] = {'lat': lat, 'lon': lon}
        except FileNotFoundError:
            print(f"အမှား: {file_path} ဖိုင်ကို ရှာမတွေ့ပါ။")
        except ValueError as e:
            print(f"CSV ဖိုင်ထဲက Latitude သို့မဟုတ် Longitude တန်ဖိုးက ဂဏန်းမဟုတ်ပါ: {e}")
        except Exception as e:
            print(f"CSV ဖိုင်ဖတ်ရာမှာ မသိသော အမှားတစ်ခုရှိပါတယ်: {e}")
            
        return data

    def get_states(self):
        """
        တိုင်း/ပြည်နယ်များ၏ စာရင်းကို ပြန်ပေးပါတယ်။
        Duplicate များကို ဖယ်ရှားပြီး အစဉ်လိုက် စီပေးပါတယ်။
        """
        return sorted(list(set(self.location_data.keys())))

    def get_cities(self, state_name):
        """
        ရွေးချယ်ထားသော တိုင်း/ပြည်နယ်အတွက် မြို့များ၏ စာရင်းကို
        အက္ခရာစဉ်အလိုက် စီလျက် ပြန်ပေးပါတယ်။
        """
        return sorted(list(self.location_data.get(state_name, {}).keys()))

    def get_location(self, state_name, city_name):
        """တိုင်း/ပြည်နယ်နဲ့ မြို့အမည်အရ Latitude နဲ့ Longitude ကို ပြန်ပေးပါတယ်။"""
        return self.location_data.get(state_name, {}).get(city_name)

    def save_chart_data(self, file_path, data):
        """ဇာတာဒေတာများကို JSON ဖိုင်အဖြစ် သိမ်းဆည်းပေးပါတယ်။"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"ဖိုင်သိမ်းဆည်းရာမှာ အမှား: {e}")
            return False

    def load_chart_data(self, file_path):
        """JSON ဖိုင်မှ ဇာတာဒေတာများကို ဖတ်ရှုပေးပါတယ်။"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ဖိုင်ကို ရှာမတွေ့ပါ: {file_path}")
            return None
        except json.JSONDecodeError:
            print(f"JSON ဖိုင် format မှားနေပါတယ်: {file_path}")
            return None
        except Exception as e:
            print(f"ဖိုင်ဖွင့်ရာမှာ အမှား: {e}")
            return None