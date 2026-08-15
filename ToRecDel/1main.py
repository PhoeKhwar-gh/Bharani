import sys
import os
import csv
import math
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QPushButton,
                             QFileDialog , QTextEdit, QVBoxLayout, QWidget,QHBoxLayout, QLabel )
from PyQt5.QtCore import QDate, QTime, Qt
from PyQt5.QtGui import QFont

# သီးခြားဖိုင်မှ Chart Widget ကို Import လုပ်ထားပါသည်
from chart_widget import BurmeseChartWidget 


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
    swe.SUN: '☉', swe.MOON: '☽', swe.MARS: '♂', swe.MERCURY: '☿', 
    swe.JUPITER: '♃', swe.VENUS: '♀', swe.SATURN: '♄', 
    swe.URANUS: '♅', swe.NEPTUNE: '♆', swe.PLUTO: '♇', 
    swe.TRUE_NODE: '☊', swe.MEAN_NODE: '☊',
    'RAHU': '☊', 'KETU': '☋', 'LAGNA': 'လ'
}

# ZODIAC_SIGNS_MM ကို chart_widget.py သို့ ရွှေ့ထားပြီဖြစ်သည်

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

        # === Load CSV Data ===
        self.load_location_data()
        
        # === IMPORTANT: Populate Timezone ===
        self.populate_timezone_combo()

        # === Connect Signals ===
        self.setup_connections()
        
        # Setup display areas
        self.setup_display_widgets()
        

    # သတိပြုပါ: Functions တို့ကို __init__ အပြင်ဘက်မှာ အဆင့်တူရေးသားထားသည်။
    
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
        
        # Create horizontal layout for three charts
        from PyQt5.QtWidgets import QHBoxLayout
        charts_layout = QHBoxLayout()  # Changed to QHBoxLayout for side-by-side
        
        # Create three chart widgets
        self.rasi_chart_widget = BurmeseChartWidget()
        self.bhava_chart_widget = BurmeseChartWidget()
        self.navamsa_chart_widget = BurmeseChartWidget()
        
        # Set fixed sizes to ensure proper layout
        self.rasi_chart_widget.setFixedSize(400, 400)
        self.bhava_chart_widget.setFixedSize(400, 400)
        self.navamsa_chart_widget.setFixedSize(400, 400)
        
        #Add labels above each chart
        from PyQt5.QtWidgets import QLabel
        rasi_label = QLabel("ရာသီစက်")
        rasi_label.setAlignment(Qt.AlignCenter)
        bhava_label = QLabel("ဘာဝစက်")
        bhava_label.setAlignment(Qt.AlignCenter)
        navamsa_label = QLabel("နဝင်းစက်")
        navamsa_label.setAlignment(Qt.AlignCenter)
        
        # Add label-chart pairs to layouts
        rasi_container = QVBoxLayout()
        rasi_container.addWidget(rasi_label)
        rasi_container.addWidget(self.rasi_chart_widget)
        
        bhava_container = QVBoxLayout()
        bhava_container.addWidget(bhava_label)
        bhava_container.addWidget(self.bhava_chart_widget)
        
        navamsa_container = QVBoxLayout()
        navamsa_container.addWidget(navamsa_label)
        navamsa_container.addWidget(self.navamsa_chart_widget)
        
        # Add containers to main horizontal layout
        charts_layout.addLayout(rasi_container)
        charts_layout.addLayout(bhava_container)
        charts_layout.addLayout(navamsa_container)
        
        # Add spacing between charts
        charts_layout.setSpacing(10)
        
        center_layout.addLayout(charts_layout)
        center_layout.addStretch(1)
        self.center_widget.setLayout(center_layout)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.center_widget)
        
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
                        'retro': is_retrograde
                    })
                except Exception as e:
                    print(f"Error calculating planet {pid}: {e}")
                    continue

            # 2. Calculate Ascendant (Lagna)
            try:
                houses = swe.houses(jd, latitude, longitude, house_system_code) 
                asc_long_tropical = houses[0][0]
                asc_long_sidereal = (asc_long_tropical - ayanamsa_val) % 360
                
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
                    'house': 1
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
                    'symbol': '☊',
                    'sign': rahu_sign,
                    'deg': rahu_deg,
                    'min': rahu_min,
                    'retro': False 
                }
                results.append(rahu_data)
                
                ketu_long = (rahu_long + 180) % 360
                ketu_sign = int(ketu_long / 30)
                ketu_deg = int(ketu_long % 30)
                ketu_min = int((ketu_long * 60) % 60)
                
                ketu_data = {
                    'id': 'Ketu',
                    'symbol': '☋',
                    'sign': ketu_sign,
                    'deg': ketu_deg,
                    'min': ketu_min,
                    'retro': False
                }
                results.append(ketu_data)
            except Exception as e:
                print(f"Node error: {e}")

            # Calculate houses for all planets
            for planet in results:
                if planet['id'] != 'Lagna':
                    planet_sign = planet['sign']
                    house_number = (planet_sign + 12 - asc_sign) % 12 + 1
                    planet['house'] = house_number

            # Calculate the three different chart types
            rasi_results = results  # This is the original zodiac chart
            bhava_results = self.calculate_bhava_chalit(results, asc_sign)
            navamsa_results = self.calculate_navamsa(results)

            # Display all three charts
            self.rasi_chart_widget.set_planet_data(rasi_results)
            self.bhava_chart_widget.set_planet_data(bhava_results)
            self.navamsa_chart_widget.set_planet_data(navamsa_results)

            # Update sidebar with Rasi chart by default
            self.update_sidebar_text(rasi_results, name, birth_date, birth_time, latitude, longitude, "Rasi (D1)")
            
            self.statusbar.showMessage(f"{name} ၏ ရာသီ၊ ဘာဝ၊ နဝင်း ဇာတာများ တွက်ချက်ပြီးပါပြီ")
            
        except Exception as e:
            QMessageBox.critical(self, "တွက်ချက်မှု အမှား", f"တွက်ချက်မှု မအောင်မြင်ပါ:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def update_sidebar_text(self, results, name, date, time, lat, lon, chart_type="Rasi (D1)"):
        date_str = date.toString("dd.MM.yyyy")
        time_str = time.toString("hh:mm AP")
        
        from chart_widget import ZODIAC_SIGNS_MM
        
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
        self.chart.update_chart()

    def new_chart(self):
        self.txtName.clear()
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        self.chart_widget.set_planet_data([]) 
        self.sidebar_text.clear()
        self.statusbar.showMessage("ဇာတာအသစ်အတွက် အဆင်သင့်ဖြစ်ပါပြီ")

    def open_chart(self):
        pass

    def save_chart(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Pyidaungsu", 10)
    app.setFont(font)

    window = BharaniApp()
    window.showMaximized()
    sys.exit(app.exec_())
    