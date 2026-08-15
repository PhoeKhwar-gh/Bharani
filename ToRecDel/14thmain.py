# main.py
import sys
import os
import csv
import math
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QPushButton, QStyledItemDelegate, 
                             QCheckBox, QVBoxLayout, QListView, QFileDialog, QTextEdit, QWidget,
                             QHBoxLayout, QLabel, QComboBox, QTableView, QAbstractItemView)
from PyQt5.QtCore import QDate, QTime, Qt, QItemSelectionModel
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem  # Keep QStandardItemModel here
from todel_divisionChart import DivisionalChartCalculator  # Remove DivisionChartSelector from this import

# သီးခြားဖိုင်မှ Chart Widget ကို Import လုပ်ထားပါသည်
from chart_widget  import BurmeseChartWidget 


# UI File မှလည်း Import လုပ်ထားသည်
from Ui_mainApp import Ui_MainWindow

# === Swisseph Import ===
import swisseph as swe


# === Constants ===
PLANET_IDS = [
    swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, 
    swe.VENUS, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO
]

PLANET_SYMBOLS = {
    swe.SUN: '၁', swe.MOON: '၂', swe.MARS: '၃', swe.MERCURY: '၄', 
    swe.JUPITER: '၅', swe.VENUS: '၆', swe.SATURN: '၀', 
    swe.URANUS: 'U', swe.NEPTUNE: 'N', swe.PLUTO: 'P', 
    swe.TRUE_NODE: '၈', swe.MEAN_NODE: '၈',
    'RAHU': '၈', 'KETU': '၉', 'LAGNA': 'လ'
}



class BharaniApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # === Set Swisseph Path ===
        ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
        swe.set_ephe_path(ephe_path)

        # Initialize variables
        self.location_data = defaultdict(list)
        self.custom_locations = []
        
        # Set default date and time
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        
        # Latitude/Longitude fields
        self.txtLat.setReadOnly(True)
        self.txtLon.setReadOnly(True)
        
        self.current_houses_cusps = None  # ဒီလိုင်းကို ထည့်ပါ

        # === Load CSV Data ===
        self.load_location_data()
        
        # === IMPORTANT: Populate Timezone ===
        self.populate_timezone_combo()

        # === Connect Signals ===
        self.setup_connections()
        
        # Setup display areas
        self.setup_display_widgets()
        
       
    
        
        



    # သတိပြုပါ: Functions တို့ကို __init__ အပြင်ဘက်မှာ အဆင့်တူရေးသားထားသည်။
    
    def calculate_division_chart(self, rasi_results, division_factor, chart_name=""):
        """
        Calculate division chart positions based on correct astrological formulas
        chart_name: D2, D7, D9, D10, D12, D20, D30, D60 etc.
        """
        division_results = []
        
        for p in rasi_results:
            p_long = p.get('longitude', 0)
            sign_num = int(p_long / 30)          # လက်ရှိရာသီ (0-11)
            deg_in_sign = p_long % 30             # ရာသီထဲက ဒီဂရီ (0-30)
            
            # ==================== D2 - Hora ====================
            if chart_name == "D2" or division_factor == 2:
                # Hora: 0-15° = 1st Hora (Sun), 15-30° = 2nd Hora (Moon)
                hora_num = 0 if deg_in_sign < 15 else 1
                
                # Odd signs (မိဿ, မေထုန်, သိဟ်, တူ, ဓနု, ကုံ)
                if sign_num % 2 == 0:  # Odd signs (0,2,4,6,8,10)
                    if hora_num == 0:  # 1st Hora
                        new_sign = sign_num
                    else:               # 2nd Hora
                        new_sign = (sign_num + 1) % 12
                else:  # Even signs (ပြိဿ, ကရကဋ်, ကန်, ဗြိစ္ဆာ, မကာရ, မိန်)
                    if hora_num == 0:  # 1st Hora
                        new_sign = (sign_num + 6) % 12
                    else:               # 2nd Hora
                        new_sign = (sign_num + 7) % 12
                
                new_long = new_sign * 30 + (deg_in_sign % 15) * 2
            
            # ==================== D7 - Saptamsa ====================
            elif chart_name == "D7" or division_factor == 7:
                # D7: Each sign divided into 7 parts of ~4.2857° each
                saptamsa_num = int(deg_in_sign / (30/7))
                
                # ရာသီအမျိုးအစားအလိုက် mapping
                # Movable signs (ကရကဋ်, တူ, မကာရ, မိဿ)
                if sign_num in [0, 3, 6, 9]:  # Mesha, Karka, Tula, Makara
                    navamsa_signs = [0, 1, 2, 3, 4, 5, 6]
                # Fixed signs (ပြိဿ, သိဟ်, ဗြိစ္ဆာ, ကုံ)
                elif sign_num in [1, 4, 7, 10]:  # Vrishabha, Simha, Vrishchika, Kumbha
                    navamsa_signs = [1, 2, 3, 4, 5, 6, 7]
                # Dual signs (မေထုန်, ကန်, ဓနု, မိန်)
                else:  # Mithuna, Kanya, Dhanu, Meena
                    navamsa_signs = [2, 3, 4, 5, 6, 7, 8]
                
                new_sign = (sign_num + navamsa_signs[saptamsa_num]) % 12
                new_long = new_sign * 30 + (deg_in_sign % (30/7)) * 7
            
            # ==================== D10 - Dasamsa ====================
            elif chart_name == "D10" or division_factor == 10:
                # D10: Each sign divided into 10 parts of 3° each
                dasamsa_num = int(deg_in_sign / 3)
                
                # Dasamsa mapping table (12 signs x 10 parts)
                dasamsa_table = [
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],   # 0: Aries (Odd)
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # 1: Taurus (Even)
                    [2, 3, 4, 5, 6, 7, 8, 9, 10, 11], # 2: Gemini (Odd)
                    [3, 4, 5, 6, 7, 8, 9, 10, 11, 0], # 3: Cancer (Even)
                    [4, 5, 6, 7, 8, 9, 10, 11, 0, 1], # 4: Leo (Odd)
                    [5, 6, 7, 8, 9, 10, 11, 0, 1, 2], # 5: Virgo (Even)
                    [6, 7, 8, 9, 10, 11, 0, 1, 2, 3], # 6: Libra (Odd)
                    [7, 8, 9, 10, 11, 0, 1, 2, 3, 4], # 7: Scorpio (Even)
                    [8, 9, 10, 11, 0, 1, 2, 3, 4, 5], # 8: Sagittarius (Odd)
                    [9, 10, 11, 0, 1, 2, 3, 4, 5, 6], # 9: Capricorn (Even)
                    [10, 11, 0, 1, 2, 3, 4, 5, 6, 7], # 10: Aquarius (Odd)
                    [11, 0, 1, 2, 3, 4, 5, 6, 7, 8],  # 11: Pisces (Even)
                ]
                
                new_sign = dasamsa_table[sign_num][dasamsa_num]
                new_long = new_sign * 30 + (deg_in_sign % 3) * 10
            
            # ==================== D12 - Dwadasamsa ====================
            elif chart_name == "D12" or division_factor == 12:
                # D12: Each sign divided into 12 parts of 2°30' each
                dwadasamsa_num = int(deg_in_sign / 2.5)
                
                # Odd signs: counting from same sign
                # Even signs: counting from 9th sign
                if sign_num % 2 == 0:  # Odd signs
                    new_sign = (sign_num + dwadasamsa_num) % 12
                else:  # Even signs
                    new_sign = (sign_num + 9 + dwadasamsa_num) % 12
                
                new_long = new_sign * 30 + (deg_in_sign % 2.5) * 12
            
            # ==================== D30 - Trimsamsa ====================
            elif chart_name == "D30" or division_factor == 30:
                # D30: 5 parts with different rulers
                if deg_in_sign < 5:
                    trimshamsa_num = 0  # 0-5°
                elif deg_in_sign < 10:
                    trimshamsa_num = 1  # 5-10°
                elif deg_in_sign < 18:
                    trimshamsa_num = 2  # 10-18°
                elif deg_in_sign < 25:
                    trimshamsa_num = 3  # 18-25°
                else:
                    trimshamsa_num = 4  # 25-30°
                
                # Odd/Even signs have different mappings
                if sign_num % 2 == 0:  # Odd signs
                    mapping = [0, 1, 2, 3, 4]  # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
                else:  # Even signs
                    mapping = [4, 3, 2, 1, 0]  # Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces
                
                new_sign = (sign_num + mapping[trimshamsa_num]) % 12
                new_long = new_sign * 30 + (deg_in_sign % (30/5)) * 6
            
            # ==================== D60 - Shashtyamsa ====================
            elif chart_name == "D60" or division_factor == 60:
                # D60: Each sign divided into 60 parts of 0.5° each
                shashtyamsa_num = int(deg_in_sign * 2)  # 0-59
                
                # From BPHS: count from the same sign for all
                # (Jhoro စနစ်အရ counting from same sign)
                new_sign = (sign_num + (shashtyamsa_num // 12)) % 12
                new_long = new_sign * 30 + (deg_in_sign % 0.5) * 60
            
            # ==================== Default Simple Formula ====================
            else:
                div_long = (p_long * division_factor) % 360
                new_sign = int(div_long / 30)
                new_deg = div_long % 30
                new_long = div_long
            
            # Create new entry
            new_p = p.copy()
            new_p['longitude'] = new_long
            new_p['sign'] = int(new_long / 30)
            new_p['deg'] = int(new_long % 30)
            new_p['min'] = int((new_long * 60) % 60)
            division_results.append(new_p)
        
        return division_results

    def calculate_navamsa(self, rasi_results):
        """
        Rasi Data များကို Navamsa (D9) အဖြစ် ပြောင်းလဲခြင်း
        Formula: Navamsa Long = (Planet Long * 9) % 360
        """
        navamsa_results = []
        for p in rasi_results:
            # စုစုပေါင်း Longitude ယူရန်
            p_long = p.get('longitude', 0)
            
            # Navamsa တွက်ချက်ခြင်း
            d9_long = (p_long * 9) % 360
            
            # D9 Sign နှင့် Degree/Min တို့ ပြန်ခွဲထုတ်ခြင်း
            d9_sign = int(d9_long / 30)
            d9_deg = int(d9_long % 30)
            d9_min = int((d9_long * 60) % 60)
            
            # Create new dict to avoid modifying original rasi_results
            new_p = {
                'id': p['id'],
                'symbol': p['symbol'],
                'longitude': d9_long, # Store new longitude
                'sign': d9_sign,
                'deg': d9_deg,
                'min': d9_min,
                'retro': p.get('retro', False),
                'house': 0 # Reset house, widget can recalculate or we can ignore
            }
            
            # If needed, you can calculate Navamsa Lagna and assign houses here.
            # But usually just the position is enough for display.
            
            navamsa_results.append(new_p)
                
        return navamsa_results

    def calculate_bhava_chalit(self, rasi_results, lagna_sign, houses_cusps):
        """
        Bhava Chalit အတွက် Data တွက်ချက်ခြင်း (Cusps အခြေခံ)
        """
        bhava_results = []
        
        for p in rasi_results:
            p_long = p.get('longitude', 0)
            
            # Determine House based on Cusps
            # houses_cusps is a list of 12 floats representing the start of each house
            planet_house = 0
            
            # Simple loop to find which house the longitude falls into
            for i in range(12):
                cusp_start = houses_cusps[i]
                cusp_end = houses_cusps[(i + 1) % 12]
                
                # Handle the wrap-around case (e.g. 350 deg to 10 deg)
                if cusp_end < cusp_start:
                    if p_long >= cusp_start or p_long < cusp_end:
                        planet_house = i + 1
                        break
                else:
                    if cusp_start <= p_long < cusp_end:
                        planet_house = i + 1
                        break
            
            # Default to Lagna house if calculation fails (fallback)
            if planet_house == 0: planet_house = 1
            
            # For Bhava Chalit chart visualization:
            # The chart is usually drawn with House 1 as the first box.
            # We map the calculated House to a "Virtual Sign" so the widget places it correctly.
            # Example: If Lagna is Leo (5), and Planet is in House 2.
            # Virtual Sign = 5 + 2 - 1 = 6 (Virgo).
            
            if p['id'] == 'Lagna':
                virtual_sign = lagna_sign # Lagna always in 1st House
                bhava_house = 1
            else:
                bhava_house = planet_house
                virtual_sign = (lagna_sign + bhava_house - 1) % 12
            
            new_p = p.copy()
            new_p['sign'] = int(virtual_sign)
            new_p['house'] = bhava_house # Store actual Bhava house
            bhava_results.append(new_p)
            
        return bhava_results

    def populate_timezone_combo(self):
        """Populate cboTimezone with world time zones"""
        timezones = [
            ("UTC-12:00", -12.0),
            ("UTC-11:00", -11.0),
            ("UTC-10:00", -10.0),
            ("UTC-09:30", -9.5),
            ("UTC-09:00", -9.0),
            ("UTC-08:00", -8.0),
            ("UTC-07:00", -7.0),
            ("UTC-06:00", -6.0),
            ("UTC-05:00", -5.0),
            ("UTC-04:30", -4.5),
            ("UTC-04:00", -4.0),
            ("UTC-03:30", -3.5),
            ("UTC-03:00", -3.0),
            ("UTC-02:00", -2.0),
            ("UTC-01:00", -1.0),
            ("UTC±00:00", 0.0),
            ("UTC+01:00", 1.0),
            ("UTC+02:00", 2.0),
            ("UTC+03:00", 3.0),
            ("UTC+03:30", 3.5),
            ("UTC+04:00", 4.0),
            ("UTC+04:30", 4.5),
            ("UTC+05:00", 5.0),
            ("UTC+05:30", 5.5),
            ("UTC+05:45", 5.75),
            ("UTC+06:00", 6.0),
            ("UTC+06:30", 6.5),  # Myanmar Time (Default)
            ("UTC+07:00", 7.0),
            ("UTC+08:00", 8.0),
            ("UTC+08:45", 8.75),
            ("UTC+09:00", 9.0),
            ("UTC+09:30", 9.5),
            ("UTC+10:00", 10.0),
            ("UTC+10:30", 10.5),
            ("UTC+11:00", 11.0),
            ("UTC+12:00", 12.0),
            ("UTC+12:45", 12.75),
            ("UTC+13:00", 13.0),
            ("UTC+14:00", 14.0),
        ]
        
        self.cboTimezone.clear()
        for tz_name, tz_offset in timezones:
            self.cboTimezone.addItem(tz_name, tz_offset)
        
        default_index = -1
        for i in range(self.cboTimezone.count()):
            if self.cboTimezone.itemData(i) == 6.5:
                default_index = i
                break
        
        if default_index >= 0:
            self.cboTimezone.setCurrentIndex(default_index)
        else:
            for i in range(self.cboTimezone.count()):
                if self.cboTimezone.itemData(i) == 0.0:
                    self.cboTimezone.setCurrentIndex(i)
                    break
        
        self.statusbar.showMessage("ဇာတာတွက်ချက်ရန် အဆင်သင့်ဖြစ်ပါပြီ")

   
    
    def setup_display_widgets(self):
        self.center_widget = QWidget()
        center_layout = QVBoxLayout()
        
        # Define chart types in rows
        chart_rows = [
            ['D1', 'D2', 'D7'],
            ['D9', 'D10', 'D12'],
            ['D20', 'D30', 'D60']
        ]
        
        # Store references for later use
        self.chart_widgets = {}
        # Store original chart widgets for backward compatibility
        self.rasi_chart_widget = None
        self.bhava_chart_widget = None
        self.navamsa_chart_widget = None

        # Create charts grid
        charts_grid_layout = QVBoxLayout()
        
        for row_index, chart_types in enumerate(chart_rows):
            row_layout = QHBoxLayout()
            
            for col_index, chart_type in enumerate(chart_types):
                chart_widget = BurmeseChartWidget()
                chart_widget.setFixedSize(400, 400)
                self.chart_widgets[chart_type] = chart_widget
                row_layout.addWidget(chart_widget)
                
             # Backward compatibility - assign to original variables
                if chart_type == 'D1':
                    self.rasi_chart_widget = chart_widget
                elif chart_type == 'D9':
                    self.navamsa_chart_widget = chart_widget
                elif chart_type == 'D10':
                    self.bhava_chart_widget = chart_widget   
            
            charts_grid_layout.addLayout(row_layout)
        
        charts_grid_layout.addStretch(1)
        
        center_layout.addLayout(charts_grid_layout)
        self.center_widget.setLayout(center_layout)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.center_widget)
        
        # Sidebar setup
        self.sidebar_text = QTextEdit()
        self.sidebar_text.setReadOnly(True)
        self.sidebar_text.setFont(QFont("Pyidaungsu", 9))
        self.scrollArea_2.setWidget(self.sidebar_text)
        self.scrollArea_2.setWidgetResizable(True)


        
               
        
    def setup_connections(self):
        self.cboState.currentTextChanged.connect(self.on_state_changed)
        self.cboCity.currentTextChanged.connect(self.on_town_changed)
        self.btnCalculate.clicked.connect(self.calculate_chart)
        self.btnEditPlace.clicked.connect(self.toggle_place_edit)
        self.actionNew.triggered.connect(self.new_chart)
        self.actionOpen.triggered.connect(self.open_chart)
        self.actionSave.triggered.connect(self.save_chart)
        self.actionExit.triggered.connect(self.close)
        
      

    def load_location_data(self):
        csv_path = os.path.join(os.path.dirname(__file__), "dataCSV.csv")
        try:
            with open(csv_path, encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sr = row["SRName"].strip()
                    town = row["TownName"].strip()
                    lat = row["Latitude"].strip()
                    lon = row["Longitude"].strip()
                    self.location_data[sr].append((town, lat, lon))
            states = sorted(self.location_data.keys())
            self.cboState.clear()
            self.cboState.addItems(states)
            if states:
                self.cboState.setCurrentText(states[0])
                self.on_state_changed(states[0])                    
        except FileNotFoundError:
            QMessageBox.warning(self, "ဖိုင်မတွေ့", "dataCSV.csv ဖိုင်မတွေ့ပါ။")
            self.create_sample_location_data()

    def create_sample_location_data(self):
        sample_data = {
            "ရန်ကုန်တိုင်း": [("ရန်ကုန်", "16.8661", "96.1951")],
            "မန္တလေးတိုင်း": [("မန္တလေး", "21.9588", "96.0891")]
        }
        self.location_data.update(sample_data)
        states = sorted(self.location_data.keys())
        self.cboState.clear()
        self.cboState.addItems(states)
        if states:
            self.cboState.setCurrentText(states[0])
            self.on_state_changed(states[0])

    def on_state_changed(self, state):
        self.cboCity.clear()
        self.txtLat.clear()
        self.txtLon.clear()
        if state in self.location_data:
            towns = [item[0] for item in self.location_data[state]]
            self.cboCity.addItems(towns)
            if towns:
                self.cboCity.setCurrentIndex(0)

    def on_town_changed(self, town):
        state = self.cboState.currentText()
        if not state or not town: return
        for t, lat, lon in self.location_data[state]:
            if t == town:
                self.txtLat.setText(lat)
                self.txtLon.setText(lon)
                break

    def toggle_place_edit(self):
        is_readonly = self.txtLat.isReadOnly()
        self.txtLat.setReadOnly(not is_readonly)
        self.txtLon.setReadOnly(not is_readonly)
        if is_readonly:
            self.btnEditPlace.setText("Save")
        else:
            self.btnEditPlace.setText("+/-")

    def get_ayanamsa_flag(self):
        ayanamsa_name = self.cboAyana.currentText()
        if "Lahiri" in ayanamsa_name or "လဟိရီ" in ayanamsa_name:
            return swe.SIDM_LAHIRI
        elif "Raman" in ayanamsa_name:
            return swe.SIDM_RAMAN
        elif "Fagan" in ayanamsa_name:
            return swe.SIDM_FAGAN_BRADLEY
        else:
            return swe.SIDM_LAHIRI

    def get_house_system_code(self):
        house_system_name = self.cboHouseSys.currentText()
        mapping = {
            "Whole Sign": b'W',
            "Vehlow Equal": b'E',
            "Equal": b'A',
            "Placidus": b'P',
            "Sripati": b'S',
            "Porphyry": b'O'
        }
        return mapping.get(house_system_name, b'E')
    
    def calculate_chart(self):
        try:
            name = self.txtName.text().strip()
            if not name:
                QMessageBox.warning(self, "အမည်ထည့်ရန်", "ကျေးဇူးပြု၍ အမည်ထည့်သွင်းပါ")
                return

            birth_date = self.cboDate.date()
            birth_time = self.cboTime.time()
            
            year = birth_date.year()
            month = birth_date.month()
            day = birth_date.day()
            hour = birth_time.hour()
            minute = birth_time.minute()
            second = birth_time.second()
            
            tz_offset = self.cboTimezone.currentData()
            if tz_offset is None: tz_offset = 6.5
            
            local_hour = hour + minute/60.0 + second/3600.0
            utc_hour = local_hour - tz_offset
            
            if utc_hour < 0:
                utc_hour += 24
                dt = datetime(year, month, day) - timedelta(days=1)
                year, month, day = dt.year, dt.month, dt.day
            elif utc_hour >= 24:
                utc_hour -= 24
                dt = datetime(year, month, day) + timedelta(days=1)
                year, month, day = dt.year, dt.month, dt.day
            
            jd = swe.julday(year, month, day, utc_hour)
            
            house_system_code = self.get_house_system_code()
            
            lat_str = self.txtLat.text().strip()
            lon_str = self.txtLon.text().strip()
            
            if not lat_str or not lon_str:
                QMessageBox.warning(self, "တည်နေရာ အမှား", "လတ္တီတွဒ်/လောင်ဂျီတွဒ် မရှိပါ။")
                return
                
            try:
                latitude = float(lat_str)
                longitude = float(lon_str)
            except ValueError:
                QMessageBox.warning(self, "တည်နေရာ အမှား", "လတ္တီတွဒ်/လောင်ဂျီတွဒ် မှားယွင်းနေပါသည်")
                return

            ayanamsa_flag = self.get_ayanamsa_flag()
            swe.set_sid_mode(ayanamsa_flag)
            
            ayanamsa_val = swe.get_ayanamsa(jd)

            results = []
            
            # 1. Calculate Planets
            PLANET_IDS_NO_NODE = [
                swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, 
                swe.VENUS, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO
            ]
            
            for pid in PLANET_IDS_NO_NODE:
                try:
                    xx, retflag = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
                    planet_long = xx[0] % 360
                    sign_num = int(planet_long / 30)
                    degree = int(planet_long % 30)
                    minute_val = int((planet_long * 60) % 60)
                    is_retrograde = (xx[3] < 0)
                    
                    results.append({
                        'id': pid,
                        'symbol': PLANET_SYMBOLS.get(pid, '?'),
                        'sign': sign_num,
                        'deg': degree,
                        'min': minute_val,
                        'retro': is_retrograde,
                        'longitude': planet_long  # Store longitude for bhava calculation
                    })
                except Exception as e:
                    print(f"Error calculating planet {pid}: {e}")
                    continue

            # 2. Calculate Ascendant (Lagna)
            try:
                houses = swe.houses(jd, latitude, longitude, house_system_code) 
                asc_long_tropical = houses[0][0]
                asc_long_sidereal = (asc_long_tropical - ayanamsa_val) % 360
                
                # Store houses cusps for Bhava calculation
                self.current_houses_cusps = houses[0]
                
                asc_sign = int(asc_long_sidereal / 30)
                asc_deg = int(asc_long_sidereal % 30)
                asc_min = int((asc_long_sidereal * 60) % 60)
                
                lagna_data = {
                    'id': 'Lagna',
                    'symbol': 'လ',
                    'sign': asc_sign,
                    'deg': asc_deg,
                    'min': asc_min,
                    'retro': False,
                    'house': 1,
                    'longitude': asc_long_sidereal  # Store longitude
                }
                results.insert(0, lagna_data)
                            
            except Exception as e:
                print(f"Houses error: {e}")
                QMessageBox.warning(self, "Lagna တွက်ချက်မှု အမှား", f"Lagna တွက်ချက်ရာတွင် အမှားဖြစ်နေပါသည်: {str(e)}")
                return

            # 3. Calculate Rahu & Ketu
            try:
                xx_rahu, retflag_rahu = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SIDEREAL | swe.FLG_SPEED)
                rahu_long = xx_rahu[0] % 360
                
                rahu_sign = int(rahu_long / 30)
                rahu_deg = int(rahu_long % 30)
                rahu_min = int((rahu_long * 60) % 60)
                
                rahu_data = {
                    'id': 'Rahu',
                    'symbol': '၈',
                    'sign': rahu_sign,
                    'deg': rahu_deg,
                    'min': rahu_min,
                    'retro': False,
                    'longitude': rahu_long  # Store longitude
                }
                results.append(rahu_data)
                
                ketu_long = (rahu_long + 180) % 360
                ketu_sign = int(ketu_long / 30)
                ketu_deg = int(ketu_long % 30)
                ketu_min = int((ketu_long * 60) % 60)
                
                ketu_data = {
                    'id': 'Ketu',
                    'symbol': '၉',
                    'sign': ketu_sign,
                    'deg': ketu_deg,
                    'min': ketu_min,
                    'retro': False,
                    'longitude': ketu_long  # Store longitude
                }
                results.append(ketu_data)
            except Exception as e:
                print(f"Node error: {e}")

            # Calculate houses for all planets (for Rasi chart)
            asc_sign = results[0]['sign']  # Lagna sign
            for planet in results:
                if planet['id'] != 'Lagna':
                    planet_sign = planet['sign']
                    house_number = (planet_sign + 12 - asc_sign) % 12 + 1
                    planet['house'] = house_number

            # ==================================================== #
            # === ဒီနေရာမှာ Division Charts တွက်ချက်ရန် ထည့်ပါ === #
            # ==================================================== #
            
            # Calculate divisional charts with correct names
            d1_results = results  # Rasi chart (D1)
            d2_results = self.calculate_division_chart(results, 2)   # Hora
            d7_results = self.calculate_division_chart(results, 7)   # Saptāṁśa
            d9_results = self.calculate_division_chart(results, 9)   # Navāṁśa
            d10_results = self.calculate_division_chart(results, 10) # Daśāṁśa
            d12_results = self.calculate_division_chart(results, 12) # Dvādashāṁśa
            d20_results = self.calculate_division_chart(results, 20) # Vimshāṁśa
            d30_results = self.calculate_division_chart(results, 30) # Trimshāṁśa
            d60_results = self.calculate_division_chart(results, 60) # Shashtyāṁśa

            # Update chart widgets using the dictionary
            self.chart_widgets['D1'].set_planet_data(d1_results, True, "D1 - Rāśi")
            self.chart_widgets['D2'].set_planet_data(d2_results, False, "D2 - Hora")
            self.chart_widgets['D7'].set_planet_data(d7_results, False, "D7 - Saptāṁśa")
            self.chart_widgets['D9'].set_planet_data(d9_results, False, "D9 - Navāṁśa")
            self.chart_widgets['D10'].set_planet_data(d10_results, False, "D10 - Daśāṁśa")
            self.chart_widgets['D12'].set_planet_data(d12_results, False, "D12 - Dvādashāṁśa")
            self.chart_widgets['D20'].set_planet_data(d20_results, False, "D20 - Vimshāṁśa")
            self.chart_widgets['D30'].set_planet_data(d30_results, False, "D30 - Trimshāṁśa")
            self.chart_widgets['D60'].set_planet_data(d60_results, False, "D60 - Shashtyāṁśa")

            # Update sidebar with D1 chart info
            self.update_sidebar_text(d1_results, name, birth_date, birth_time, latitude, longitude, "D1 - Rāśi")

            self.statusbar.showMessage(f"{name} ၏ ဇာတာများ တွက်ချက်ပြီးပါပြီ")
            
        except Exception as e:
            QMessageBox.critical(self, "တွက်ချက်မှု အမှား", f"တွက်ချက်မှု မအောင်မြင်ပါ:\n{str(e)}")
            import traceback
            traceback.print_exc()

    
#====================================================#
#               Calculate အဆုံးပါ                     #
#====================================================#

     

    def calculate_division_chart(self, rasi_results, division_factor, chart_name=""):
        """
        Calculate division chart positions based on division factor
        chart_name: D2, D7, D9, D10, D12, D20, D30, D60 etc.
        """
        division_results = []
        
        for p in rasi_results:
            p_long = p.get('longitude', 0)
            
            # Division formula: (Longitude * division_factor) % 360
            div_long = (p_long * division_factor) % 360
            
            # Calculate sign, degree, minute for division chart
            div_sign = int(div_long / 30)
            div_deg = int(div_long % 30)
            div_min = int((div_long * 60) % 60)
            
            # Create new entry for division chart
            new_p = p.copy()
            new_p['longitude'] = div_long
            new_p['sign'] = div_sign
            new_p['deg'] = div_deg
            new_p['min'] = div_min
            division_results.append(new_p)
        
        return division_results

    def update_sidebar_text(self, results, name, date, time, lat, lon, chart_type="Rasi (D1)"):
        date_str = date.toString("dd.MM.yyyy")
        time_str = time.toString("hh:mm AP")
        
        # chart_widget.py မှ ZODIAC_SIGNS_MM ကို import လုပ်ပါ
        # သို့မဟုတ် ဒီနေရာမှာ သတ်မှတ်ပါ
        ZODIAC_SIGNS_MM = [
            "မိဿ", "ပြိဿ", "မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်",
            "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုံ", "မိန်"
        ]
        
        text = f"အမည်: {name}\n"
        text += f"မွေးနေ့: {date_str} {time_str}\n"
        text += f"တည်နေရာ: {lat:.4f}, {lon:.4f}\n"
        text += f"ဇာတာအမျိုးအစား: {chart_type}\n\n"
        
        text += "ဂြိုဟ်တည်နေရာများ:\n"
        text += "-"*30 + "\n"
        
        for r in results:
            sign_name = ZODIAC_SIGNS_MM[r['sign']]
            
            if r['id'] == 'Lagna':
                display_name = 'လဂ်'
            elif r['id'] == 'Rahu':
                display_name = 'ရာဟု'
            elif r['id'] == 'Ketu':
                display_name = 'ကိတ်'
            else:
                display_name = r['symbol']
            
            retro_str = " R" if r.get('retro', False) else ""
            text += f"{display_name} {r['deg']}°{r['min']}'{retro_str} - {sign_name}\n"
        
        self.sidebar_text.setPlainText(text)
        
        # ဤလိုင်းကို ဖယ်ရှားပါ (သို့မဟုတ် comment လုပ်ပါ)
        # self.chart.update_chart()  # ← ဤလိုင်းကို ဖယ်ရှားပါ
        
        # Update chart widgets - use dictionary instead of direct attributes
        if hasattr(self, 'rasi_chart_widget') and self.rasi_chart_widget:
            self.rasi_chart_widget.update()
        if hasattr(self, 'bhava_chart_widget') and self.bhava_chart_widget:
            self.bhava_chart_widget.update()
        if hasattr(self, 'navamsa_chart_widget') and self.navamsa_chart_widget:
            self.navamsa_chart_widget.update()

    def new_chart(self):
        self.txtName.clear()
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        
        # Clear all chart widgets
        # Clear all chart widgets
        self.rasi_chart_widget.set_planet_data([])
        self.bhava_chart_widget.set_planet_data([])
        self.navamsa_chart_widget.set_planet_data([])
        
        self.chart_widget.set_planet_data([]) 
        self.sidebar_text.clear()
        self.statusbar.showMessage("ဇာတာအသစ်အတွက် အဆင်သင့်ဖြစ်ပါပြီ")

    def open_chart(self):
        pass

    def save_chart(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Pyidaungsu")
    app.setFont(font)

    window = BharaniApp()
    window.showMaximized()
    sys.exit(app.exec_())
    