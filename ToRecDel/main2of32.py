# main.py
import sys
import os
import csv
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, 
                             QFileDialog, QTextEdit, QVBoxLayout, QWidget)
from PyQt5.QtCore import QDate, QTime, Qt, QRectF, QPointF, QRect
from PyQt5.QtGui import QFont, QPen, QPainter, QColor, QPixmap
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

ZODIAC_SIGNS_MM = [
    "မိဿ", "ပြိဿ", "မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်",
    "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုမ်", "မိန်"
]

ZODIAC_SYMBOLS = [
    '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'
]

class BurmeseChartWidget(QWidget):
    """
    Center Frame တွင် ပုံဖော်ပြရန် Widget (400x400)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.planet_data = [] 
        
        # === Size ကို 400x400 သတ်မှတ်ခြင်း ===
        self.setFixedSize(400, 400)
        
        # Grid အတွက် Cell Size
        self.cell_size = 60 
        
        # Scale factor (0.7 သို့လျှော့ချခြင်းအားဖြင့် စာသား မထွက်ရအောင် စောင့်ရှောက်သည်)
        self.scale_factor = 0.7 
        
        # Center Point (400 / 2)
        self.center_x = 200
        self.center_y = 200
        

    def set_planet_data(self, data):
        self.planet_data = data
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background Fill
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # 1. Grid ဆွဲခြင်း
        self.draw_grid(painter)
        
        # 2. အလယ်တွင် "ရာသီ" စာတန်းထည့်ခြင်း
        font_sign = QFont("Pyidaungsu", 12, QFont.Bold)
        painter.setFont(font_sign)
        painter.setPen(Qt.black)
        painter.drawText(QRectF(160, 184, 80, 32), Qt.AlignCenter, "ရာသီ")

        # 3. ဂြိုဟ်များ ဖော်ပြခြင်း
        self.draw_planets(painter)

    def draw_grid(self, painter):
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        
        c_x, c_y, cell = self.center_x, self.center_y, self.cell_size
        
        # TypeError ကာကွယ်ရန် int() သုံးထားပါသည်
        # Vertical Lines
        painter.drawLine(int(c_x - cell), int(c_y - 5*cell), int(c_x - cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y - 5*cell), int(c_x + cell), int(c_y + 5*cell))
        # Horizontal Lines
        painter.drawLine(int(c_x - 5*cell), int(c_y - cell), int(c_x + 5*cell), int(c_y - cell))
        painter.drawLine(int(c_x - 5*cell), int(c_y + cell), int(c_x + 5*cell), int(c_y + cell))
        
        # Diagonal Lines (Diamond Shape)
        painter.drawLine(int(c_x - 5*cell), int(c_y - 5*cell), int(c_x - cell), int(c_y - cell))
        painter.drawLine(int(c_x + 5*cell), int(c_y - 5*cell), int(c_x + cell), int(c_y - cell))
        painter.drawLine(int(c_x - cell), int(c_y + cell), int(c_x - 5*cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y + cell), int(c_x + 5*cell), int(c_y + 5*cell))

    def get_zodiac_positions(self):
        # Coordinates roughly mapped to 12 positions around the center
        base_coords = [
            ("မိဿ", 260, 20), ("ပြိဿ", 155, 20), ("မေထုန်", 75, 80),
            ("ကရကဋ်",75, 195), ("သိဟ်", 75, 345), ("ကန်", 165, 415),
            ("တူ", 260, 345), ("ဗြိစ္ဆာ", 405, 405), ("ဓနု", 485, 345),
            ("မကာရ", 405, 195), ("ကုမ်", 485, 101), ("မိန်", 405, 20)
        ]

        pos_dict = {}
        scale = 0.8
        
        for i, (name, bx, by) in enumerate(base_coords):
            x = (bx - 250) * scale + self.center_x
            y = (by - 250) * scale + self.center_y
            pos_dict[name] = QPointF(x, y)
            
        return pos_dict

    def draw_planets(self, painter):
        if not self.planet_data:
            return

        # Group planets by sign
        planets_by_sign = {}
        for p in self.planet_data:
            sign_name = ZODIAC_SIGNS_MM[p['sign']]
            if sign_name not in planets_by_sign:
                planets_by_sign[sign_name] = []
            planets_by_sign[sign_name].append(p)

        # Font settings
        font = QFont("Segoe UI Symbol", 9)
        painter.setFont(font)
        painter.setPen(Qt.black)
        
        line_height = 15
        zodiac_positions = self.get_zodiac_positions()

        # Draw planet texts at their designated zodiac positions
        for sign_name, planets in planets_by_sign.items():
            if sign_name not in zodiac_positions:
                continue

            base_pos = zodiac_positions[sign_name]
            
            # Draw planets starting from the zodiac position
            for i, p in enumerate(planets):
                # === RETROGRADE CHECK & FORMATTING ===
                # ပုံစံဥပမာ: ♃ 17°36' R
                retro_char = " R" if p.get('retro', False) else ""
                text = f"{p['symbol']} {p['deg']}°{p['min']}'{retro_char}"
                
                # Position text relative to the zodiac coordinate
                # x_pos ကို လက်ရာထက်လျှော့၍ စာလုံးရှည်လျှင် ပုံပြင်မထွက်အောင် စီစဉ်ထားသည်
                x_pos = base_pos.x() - 60 
                y_pos = base_pos.y() + i * line_height 
                
                # Draw text left-aligned
                painter.drawText(QPointF(x_pos, y_pos), text)







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
        
        # === IMPORTANT: Populate Timezone (ပြင်ဆင်ချက်) ===
        self.populate_timezone_combo()

        # === Connect Signals ===
        self.setup_connections()
        
        # Setup display areas (Replaced TextEdit with ChartWidget)
        self.setup_display_widgets()

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
        
        # Clear and add timezones
        self.cboTimezone.clear()
        for tz_name, tz_offset in timezones:
            self.cboTimezone.addItem(tz_name, tz_offset)
        
        # Set default to UTC+06:30 (Myanmar Time)
        default_index = -1
        for i in range(self.cboTimezone.count()):
            if self.cboTimezone.itemData(i) == 6.5:
                default_index = i
                break
        
        if default_index >= 0:
            self.cboTimezone.setCurrentIndex(default_index)
        else:
            # Fallback to UTC±00:00 if not found
            for i in range(self.cboTimezone.count()):
                if self.cboTimezone.itemData(i) == 0.0:
                    self.cboTimezone.setCurrentIndex(i)
                    break
        
        self.statusbar.showMessage("ဇာတာတွက်ချက်ရန် အဆင်သင့်ဖြစ်ပါပြီ")

    def setup_display_widgets(self):
        # Center display area - ဇာတာပုံ (BurmeseChartWidget)
        self.center_widget = QWidget()
        center_layout = QVBoxLayout()
        
        # Create our custom chart widget
        self.chart_widget = BurmeseChartWidget()
        
        center_layout.addWidget(self.chart_widget, 0, Qt.AlignLeft)
        center_layout.addStretch(1)
        
        self.center_widget.setLayout(center_layout)
        
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.center_widget)
        
        # Right sidebar display - အသေးစိတ်အချက်အလက်များ
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
        
        # Menu actions
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
            # Save logic here...

    def get_ayanamsa_flag(self):
        """UI မှ Ayanamsa အမည်ကို ဖတ်၍ Swisseph Flag ပြန်ပေးခြင်း"""
        ayanamsa_name = self.cboAyana.currentText()
        if "Lahiri" in ayanamsa_name or "လဟိရီ" in ayanamsa_name:
            return swe.SIDM_LAHIRI
        elif "Raman" in ayanamsa_name:
            return swe.SIDM_RAMAN
        elif "Fagan" in ayanamsa_name:
            return swe.SIDM_FAGAN_BRADLEY
        else:
            # Default Lahiri
            return swe.SIDM_LAHIRI


    def get_house_system_code(self):
        """UI မှ ဘာဝစနစ်အမည်ကို ဖတ်၍ Swisseph Code ပြန်ပေးခြင်း"""
        house_system_name = self.cboHouseSys.currentText()
        mapping = {
            "Whole Sign": b'W',
            "Vehlow Equal": b'E',  # or b'V' depending on Swisseph version
            "Equal": b'A',
            "Placidus": b'P',
            "Sripati": b'S',
            "Porphyry": b'O'
        }
        return mapping.get(house_system_name, b'E')  # default to Placidus
    
    def calculate_chart(self):
        try:
            name = self.txtName.text().strip()
            if not name:
                QMessageBox.warning(self, "အမည်ထည့်ရန်", "ကျေးဇူးပြု၍ အမည်ထည့်သွင်းပါ")
                return

            # Get Date Time
            birth_date = self.cboDate.date()
            birth_time = self.cboTime.time()
            
            year = birth_date.year()
            month = birth_date.month()
            day = birth_date.day()
            hour = birth_time.hour()
            minute = birth_time.minute()
            second = birth_time.second()
            
            # === Get Timezone Offset ===
            tz_offset = self.cboTimezone.currentData()
            if tz_offset is None:
                tz_offset = 6.5  # Default to Myanmar Time
            
            # Local time to UTC conversion
            local_hour = hour + minute/60.0 + second/3600.0
            utc_hour = local_hour - tz_offset
            
            # Handle day rollover
            if utc_hour < 0:
                utc_hour += 24
                dt = datetime(year, month, day) - timedelta(days=1)
                year, month, day = dt.year, dt.month, dt.day
            elif utc_hour >= 24:
                utc_hour -= 24
                dt = datetime(year, month, day) + timedelta(days=1)
                year, month, day = dt.year, dt.month, dt.day
            
            # Calculate Julian Day with UTC time
            jd = swe.julday(year, month, day, utc_hour)
            
            print(f"Date: {day}/{month}/{year}")
            print(f"Local Time: {hour}:{minute}:{second} (Offset: {tz_offset})")
            print(f"UTC Time: {utc_hour:.2f} hours")
            print(f"Julian Day: {jd}")
            
            # Get house system code
            house_system_code = self.get_house_system_code()
            
            lat_str = self.txtLat.text().strip()
            lon_str = self.txtLon.text().strip()
            
            if not lat_str or not lon_str:
                QMessageBox.warning(self, "တည်နေရာ အမှား", "လတ္တီတွဒ်/လောင်ဂျီတွဒ် မရှိပါ။ တည်နေရာကို ရွေးချယ်ပါ။")
                return
                
            try:
                latitude = float(lat_str)
                longitude = float(lon_str)
            except ValueError:
                QMessageBox.warning(self, "တည်နေရာ အမှား", "လတ္တီတွဒ်/လောင်ဂျီတွဒ် မှားယွင်းနေပါသည်")
                return

            ayanamsa_flag = self.get_ayanamsa_flag()
            swe.set_sid_mode(ayanamsa_flag)
            
            # === CRITICAL FIX: Get Ayanamsa value for Lagna calculation ===
            ayanamsa_val = swe.get_ayanamsa(jd)
            print(f"Ayanamsa: {ayanamsa_val:.6f}")

            results = []
            
            # 1. Calculate Planets (Sun to Pluto)
            PLANET_IDS_NO_NODE = [
                swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, 
                swe.VENUS, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO
            ]
            
            for pid in PLANET_IDS_NO_NODE:
                try:
                    # Add FLG_SPEED flag to get accurate speed information
                    xx, retflag = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
                    
                    planet_long = xx[0] % 360
                    sign_num = int(planet_long / 30)
                    degree = int(planet_long % 30)
                    minute_val = int((planet_long * 60) % 60)
                    
                    # Retrograde detection (xx[3] is speed, negative is retrograde)
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
            # === FIXED: Convert Tropical Lagna to Sidereal ===
            try:
                # swe.houses returns Tropical positions by default
                houses = swe.houses(jd, latitude, longitude, house_system_code) 
                asc_long_tropical = houses[0][0]
                
                # Convert to Sidereal
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
                    'retro': False,  # Lagna is never retrograde
                    'house': 1  # Ascendant is always in house 1
                }
                results.insert(0, lagna_data)
                
                print(f"Lagna Tropical: {asc_long_tropical:.2f}, Sidereal: {asc_long_sidereal:.2f}")
                
                # Calculate house for each planet
                for planet in results:
                    if planet['id'] != 'Lagna':
                        planet_sign = planet['sign']
                        # Formula from main2of4.py: house = (sign_num + 12 - asc_sign) % 12 + 1
                        house_number = (planet_sign + 12 - asc_sign) % 12 + 1
                        planet['house'] = house_number
                        
                print(f"House system: {house_system_code.decode()}")
                              
            except Exception as e:
                print(f"Houses error: {e}")
                QMessageBox.warning(self, "Lagna တွက်ချက်မှု အမှား", f"Lagna တွက်ချက်ရာတွင် အမှားဖြစ်နေပါသည်: {str(e)}")
                return

            # 3. Calculate Rahu (True Node)
            try:
                xx_rahu, retflag_rahu = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SIDEREAL | swe.FLG_SPEED)
                rahu_long = xx_rahu[0] % 360
                
                rahu_sign = int(rahu_long / 30)
                rahu_deg = int(rahu_long % 30)
                rahu_min = int((rahu_long * 60) % 60)
                
                # === FIXED: Rahu is always considered Retrograde in this system ===
                rahu_data = {
                    'id': 'Rahu',
                    'symbol': '☊',
                    'sign': rahu_sign,
                    'deg': rahu_deg,
                    'min': rahu_min,
                    'retro': False 
                }
                results.append(rahu_data)
            except Exception as e:
                print(f"Rahu error: {e}")
                QMessageBox.warning(self, "Rahu တွက်ချက်မှု အမှား", f"Rahu တွက်ချက်ရာတွင် အမှားဖြစ်နေပါသည်: {str(e)}")
                return
            
            # 4. Calculate Ketu
            try:
                ketu_long = (rahu_long + 180) % 360
                
                ketu_sign = int(ketu_long / 30)
                ketu_deg = int(ketu_long % 30)
                ketu_min = int((ketu_long * 60) % 60)
                
                # === FIXED: Ketu is always considered Retrograde ===
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
                print(f"Ketu error: {e}")
                QMessageBox.warning(self, "Ketu တွက်ချက်မှု အမှား", f"Ketu တွက်ချက်ရာတွင် အမှားဖြစ်နေပါသည်: {str(e)}")
                return

            # Debug: Print all retrograde planets
            print("\n=== ALL RETROGRADE PLANETS ===")
            retro_count = 0
            for r in results:
                if r.get('retro', False):
                    retro_count += 1
                    print(f"  {r['symbol']} is RETROGRADE")
            
            if retro_count == 0:
                print("  No retrograde planets found")
            
            print("="*50)

            self.chart_widget.set_planet_data(results)
            self.update_sidebar_text(results, name, birth_date, birth_time, latitude, longitude)
            self.statusbar.showMessage(f"{name} ၏ ဇာတာ တွက်ချက်ပြီးပါပြီ")
            
        except Exception as e:
            QMessageBox.critical(self, "တွက်ချက်မှု အမှား", f"တွက်ချက်မှု မအောင်မြင်ပါ:\n{str(e)}")
            import traceback
            traceback.print_exc()


    def update_sidebar_text(self, results, name, date, time, lat, lon):
        date_str = date.toString("dd.MM.yyyy")
        time_str = time.toString("hh:mm AP")
        
        text = f"အမည်: {name}\n"
        text += f"မွေးနေ့: {date_str} {time_str}\n"
        text += f"တည်နေရာ: {lat:.4f}, {lon:.4f}\n\n"
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

    def new_chart(self):
        self.txtName.clear()
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        self.chart_widget.set_planet_data([]) # Clear Chart
        self.sidebar_text.clear()
        self.statusbar.showMessage("ဇာတာအသစ်အတွက် အဆင်သင့်ဖြစ်ပါပြီ")

    def open_chart(self):
        # Placeholder for open logic
        pass

    def save_chart(self):
        # Placeholder for save logic
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Pyidaungsu", 10)
    app.setFont(font)

    window = BharaniApp()
    window.showMaximized()
    sys.exit(app.exec_())
