import sys
import os
import csv
import math
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QPushButton, QStyledItemDelegate, 
                             QCheckBox, QVBoxLayout, QListView, QFileDialog, QTextEdit, QWidget,
                             QHBoxLayout, QLabel, QComboBox, QTableView, QAbstractItemView, QScrollArea)
from PyQt5.QtCore import QDate, QTime, Qt, QItemSelectionModel, QTimer
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem

from chart_widget import BurmeseChartWidget 
from Ui_mainApp import Ui_MainWindow

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

# ZODIAC_SIGNS_MM ကို chart_widget.py သို့ ရွှေ့ထားပြီဖြစ်သည်
# But we need it here too for sidebar display
ZODIAC_SIGNS_MM = [
    "မိဿ", "ပြိဿ", "မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်",
    "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုံ", "မိန်"
]

class BharaniApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # === Set Swisseph Path ===
        ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
        if os.path.exists(ephe_path):
            swe.set_ephe_path(ephe_path)
        else:
            print(f"Warning: Ephemeris path not found: {ephe_path}")

        # Initialize variables
        self.location_data = defaultdict(list)
        self.custom_locations = []
        self.current_calculation_results = None
        
        # Set default date and time
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        
        # Latitude/Longitude fields
        self.txtLat.setReadOnly(True)
        self.txtLon.setReadOnly(True)
        
        self.current_houses_cusps = None
        self.selected_division = "D1"  # Default division

        # === Load CSV Data ===
        self.load_location_data()
        
        # === IMPORTANT: Populate Timezone ===
        self.populate_timezone_combo()

        # === Connect Signals ===
        self.setup_connections()
        
        # Setup display areas
        self.setup_display_widgets()
        
        self.statusbar.showMessage("ဇာတာတွက်ချက်ရန် အဆင်သင့်ဖြစ်ပါပြီ")

    def setup_display_widgets(self):
        """Setup the main display widgets and layout"""
        self.center_widget = QWidget()
        center_layout = QVBoxLayout(self.center_widget)
        
        # Create a scroll area for the center widget
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.center_widget)
        
        # Initialize chart widgets
        self.rasi_chart_widget = BurmeseChartWidget()
        self.bhava_chart_widget = BurmeseChartWidget()
        self.navamsa_chart_widget = BurmeseChartWidget()
        
        # Set fixed sizes to ensure proper layout
        self.rasi_chart_widget.setFixedSize(400, 400)
        self.bhava_chart_widget.setFixedSize(400, 400)
        self.navamsa_chart_widget.setFixedSize(400, 400)
        
        # Create initial layout with three charts
        self.setup_three_chart_layout()
        
        # Setup sidebar text area
        self.sidebar_text = QTextEdit()
        self.sidebar_text.setReadOnly(True)
        self.sidebar_text.setFont(QFont("Pyidaungsu", 9))
        self.scrollArea_2.setWidget(self.sidebar_text)
        self.scrollArea_2.setWidgetResizable(True)
        
        # Setup simple division combobox (replacing checkable combobox)
        self.setup_simple_division_combobox()

    def setup_three_chart_layout(self):
        """Setup layout with three main charts (Rasi, Bhava, Navamsa)"""
        # Clear existing layout
        layout = self.center_widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        charts_layout = QHBoxLayout()
        
        # Add three charts
        rasi_container = QVBoxLayout()
        rasi_label = QLabel("ရာသီ (D1)")
        rasi_label.setAlignment(Qt.AlignCenter)
        rasi_label.setFont(QFont("Pyidaungsu", 10, QFont.Bold))
        rasi_container.addWidget(rasi_label)
        rasi_container.addWidget(self.rasi_chart_widget)
        
        bhava_container = QVBoxLayout()
        bhava_label = QLabel("ဘာဝ")
        bhava_label.setAlignment(Qt.AlignCenter)
        bhava_label.setFont(QFont("Pyidaungsu", 10, QFont.Bold))
        bhava_container.addWidget(bhava_label)
        bhava_container.addWidget(self.bhava_chart_widget)
        
        navamsa_container = QVBoxLayout()
        navamsa_label = QLabel("နဝင်း (D9)")
        navamsa_label.setAlignment(Qt.AlignCenter)
        navamsa_label.setFont(QFont("Pyidaungsu", 10, QFont.Bold))
        navamsa_container.addWidget(navamsa_label)
        navamsa_container.addWidget(self.navamsa_chart_widget)
        
        charts_layout.addLayout(rasi_container)
        charts_layout.addLayout(bhava_container)
        charts_layout.addLayout(navamsa_container)
        
        layout = self.center_widget.layout()
        if layout:
            layout.addLayout(charts_layout)
        else:
            layout = QVBoxLayout(self.center_widget)
            layout.addLayout(charts_layout)

    def setup_simple_division_combobox(self):
        """Setup a simple QComboBox for division selection"""
        # Remove old combobox if exists
        if hasattr(self, 'cboDivision') and self.cboDivision is not None:
            self.cboDivision.setParent(None)
        
        # Create simple combobox
        self.cboDivision = QComboBox()
        self.cboDivision.setObjectName("cboDivision")
        
        # Add division options
        division_options = [
            ("ရာသီဇာတာ (D1)", "D1"),
            ("ငွေဇာတာ (D2)", "D2"),
            ("အိုးအိမ်ဇာတာ (D4)", "D4"),
            ("သားသမီးဇာတာ (D7)", "D7"),
            ("နဝင်းဇာတာ (D9)", "D9"),
            ("အလုပ်အကိုင်ဇာတာ (D10)", "D10"),
            ("ဒုက္ခဇာတာ (D30)", "D30"),
            ("အတိတ်ဘဝကံဇာတာ (D60)", "D60"),
            ("ဘာဝဇာတာ", "BHAVA")
        ]
        
        for display_text, value in division_options:
            self.cboDivision.addItem(display_text, value)
        
        # Set default to D1
        self.cboDivision.setCurrentIndex(0)
        
        # Connect signal
        self.cboDivision.currentIndexChanged.connect(self.on_division_changed)
        
        # Add to layout (replace cboCheckable)
        layout = self.horizontalLayout_2
        layout.addWidget(self.cboDivision)

    def setup_connections(self):
        self.cboState.currentTextChanged.connect(self.on_state_changed)
        self.cboCity.currentTextChanged.connect(self.on_town_changed)
        self.btnCalculate.clicked.connect(self.calculate_chart)
        self.btnEditPlace.clicked.connect(self.toggle_place_edit)
        self.actionNew.triggered.connect(self.new_chart)
        self.actionOpen.triggered.connect(self.open_chart)
        self.actionSave.triggered.connect(self.save_chart)
        self.actionExit.triggered.connect(self.close)

    def on_division_changed(self, index):
        """Handle division combobox selection change"""
        if index >= 0:
            selected_value = self.cboDivision.itemData(index)
            self.selected_division = selected_value
            
            # Update display if we have calculation results
            if self.current_calculation_results:
                self.display_single_chart(selected_value)

    def load_location_data(self):
        csv_path = os.path.join(os.path.dirname(__file__), "dataCSV.csv")
        try:
            if os.path.exists(csv_path):
                with open(csv_path, encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sr = row.get("SRName", "").strip()
                        town = row.get("TownName", "").strip()
                        lat = row.get("Latitude", "").strip()
                        lon = row.get("Longitude", "").strip()
                        if sr and town and lat and lon:
                            self.location_data[sr].append((town, lat, lon))
                
                states = sorted(self.location_data.keys())
                self.cboState.clear()
                self.cboState.addItems(states)
                if states:
                    self.cboState.setCurrentText(states[0])
                    self.on_state_changed(states[0])
            else:
                QMessageBox.warning(self, "ဖိုင်မတွေ့", "dataCSV.csv ဖိုင်မတွေ့ပါ။")
                self.create_sample_location_data()
                    
        except Exception as e:
            QMessageBox.warning(self, "ဖိုင်ဖတ်ရာတွင်အမှား", f"CSV ဖိုင်ဖတ်ရာတွင် အမှားဖြစ်နေပါသည်: {str(e)}")
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
        if not state or not town: 
            return
            
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
            self.btnEditPlace.setText("သိမ်းမည်")
        else:
            self.btnEditPlace.setText("ပြင်မည်")

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

            # Get date and time
            birth_date = self.cboDate.date()
            birth_time = self.cboTime.time()
            
            year = birth_date.year()
            month = birth_date.month()
            day = birth_date.day()
            hour = birth_time.hour()
            minute = birth_time.minute()
            second = birth_time.second()
            
            # Get timezone offset
            tz_offset = self.cboTimezone.currentData()
            if tz_offset is None: 
                tz_offset = 6.5
            
            # Convert to UTC
            local_hour = hour + minute/60.0 + second/3600.0
            utc_hour = local_hour - tz_offset
            
            # Adjust date if needed
            if utc_hour < 0:
                utc_hour += 24
                dt = datetime(year, month, day) - timedelta(days=1)
                year, month, day = dt.year, dt.month, dt.day
            elif utc_hour >= 24:
                utc_hour -= 24
                dt = datetime(year, month, day) + timedelta(days=1)
                year, month, day = dt.year, dt.month, dt.day
            
            # Calculate Julian day
            jd = swe.julday(year, month, day, utc_hour)
            
            # Get location
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

            # Set ayanamsa and house system
            ayanamsa_flag = self.get_ayanamsa_flag()
            swe.set_sid_mode(ayanamsa_flag)
            house_system_code = self.get_house_system_code()
            
            ayanamsa_val = swe.get_ayanamsa(jd)

            results = []
            
            # 1. Calculate Planets
            for pid in PLANET_IDS:
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
                        'longitude': planet_long
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
                    'longitude': asc_long_sidereal
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
                    'longitude': rahu_long
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
                    'longitude': ketu_long
                }
                results.append(ketu_data)
            except Exception as e:
                print(f"Node error: {e}")

            # Calculate houses for all planets
            asc_sign = results[0]['sign']  # Lagna's sign
            for planet in results:
                if planet['id'] != 'Lagna':
                    planet_sign = planet['sign']
                    house_number = (planet_sign + 12 - asc_sign) % 12 + 1
                    planet['house'] = house_number

            # Calculate the three different chart types
            rasi_results = results
            
            if self.current_houses_cusps is not None:
                bhava_results = self.calculate_bhava_chalit(results, asc_sign, self.current_houses_cusps)
            else:
                bhava_results = results.copy()
                print("Warning: Houses cusps not available, using Rasi chart for Bhava")
            
            navamsa_results = self.calculate_navamsa(results)
            
            # Store calculation results for later use
            self.current_calculation_results = (rasi_results, bhava_results, navamsa_results)
            
            # Display the selected division chart
            selected_division = self.selected_division
            self.display_single_chart(selected_division)

            # Update sidebar
            chart_name = self.get_chart_name(selected_division)
            self.update_sidebar_text(results, name, birth_date, birth_time, latitude, longitude, chart_name)
            
            self.statusbar.showMessage(f"{name} ၏ {chart_name} ဇာတာ တွက်ချက်ပြီးပါပြီ")
            
        except Exception as e:
            QMessageBox.critical(self, "တွက်ချက်မှု အမှား", f"တွက်ချက်မှု မအောင်မြင်ပါ:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def display_single_chart(self, division_code):
        """Display a single chart based on division code"""
        if not self.current_calculation_results:
            return
            
        rasi_results, bhava_results, navamsa_results = self.current_calculation_results
        
        # Clear existing layout
        layout = self.center_widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # Get chart data based on division
        if division_code == "D1":
            chart_data = rasi_results
            chart_title = "ရာသီဇာတာ (D1)"
            show_degrees = True
        elif division_code == "D2":
            chart_data = self.calculate_division_chart(rasi_results, 2)
            chart_title = "ငွေဇာတာ (D2)"
            show_degrees = True
        elif division_code == "D4":
            chart_data = self.calculate_division_chart(rasi_results, 4)
            chart_title = "အိုးအိမ်ဇာတာ (D4)"
            show_degrees = True
        elif division_code == "D7":
            chart_data = self.calculate_division_chart(rasi_results, 7)
            chart_title = "သားသမီးဇာတာ (D7)"
            show_degrees = True
        elif division_code == "D9":
            chart_data = navamsa_results
            chart_title = "နဝင်းဇာတာ (D9)"
            show_degrees = True
        elif division_code == "D10":
            chart_data = self.calculate_division_chart(rasi_results, 10)
            chart_title = "အလုပ်အကိုင်ဇာတာ (D10)"
            show_degrees = True
        elif division_code == "D30":
            chart_data = self.calculate_division_chart(rasi_results, 30)
            chart_title = "ဒုက္ခဇာတာ (D30)"
            show_degrees = True
        elif division_code == "D60":
            chart_data = self.calculate_division_chart(rasi_results, 60)
            chart_title = "အတိတ်ဘဝကံဇာတာ (D60)"
            show_degrees = True
        elif division_code == "BHAVA":
            chart_data = bhava_results
            chart_title = "ဘာဝဇာတာ"
            show_degrees = False
        else:
            # Default to Rasi
            chart_data = rasi_results
            chart_title = "ရာသီဇာတာ (D1)"
            show_degrees = True
        
        # Create layout for single chart
        chart_layout = QVBoxLayout()
        chart_label = QLabel(chart_title)
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
        chart_layout.addWidget(chart_label)
        
        # Create and configure chart widget
        chart_widget = BurmeseChartWidget()
        chart_widget.setFixedSize(500, 500)
        chart_widget.set_planet_data(chart_data, show_degrees, chart_title)
        chart_layout.addWidget(chart_widget, 0, Qt.AlignCenter)
        
        # Add to main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(chart_layout)
        main_layout.addStretch(1)
        
        self.center_widget.setLayout(main_layout)

    def calculate_division_chart(self, rasi_results, division_factor):
        """
        Calculate division chart positions based on division factor
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
            new_p.update({
                'longitude': div_long,
                'sign': div_sign,
                'deg': div_deg,
                'min': div_min,
                'house': 0  # Reset house for division chart
            })
            
            division_results.append(new_p)
        
        return division_results

    def calculate_navamsa(self, rasi_results):
        """
        Rasi Data များကို Navamsa (D9) အဖြစ် ပြောင်းလဲခြင်း
        Formula: Navamsa Long = (Planet Long * 9) % 360
        """
        navamsa_results = []
        for p in rasi_results:
            p_long = p.get('longitude', 0)
            
            # Navamsa တွက်ချက်ခြင်း
            d9_long = (p_long * 9) % 360
            
            # D9 Sign နှင့် Degree/Min တို့ ပြန်ခွဲထုတ်ခြင်း
            d9_sign = int(d9_long / 30)
            d9_deg = int(d9_long % 30)
            d9_min = int((d9_long * 60) % 60)
            
            # Create new dict
            new_p = p.copy()
            new_p.update({
                'longitude': d9_long,
                'sign': d9_sign,
                'deg': d9_deg,
                'min': d9_min,
                'house': 0
            })
            
            navamsa_results.append(new_p)
                
        return navamsa_results

    def calculate_bhava_chalit(self, rasi_results, lagna_sign, houses_cusps):
        """
        Bhava Chalit အတွက် Data တွက်ချက်ခြင်း (Cusps အခြေခံ)
        """
        if houses_cusps is None or len(houses_cusps) < 12:
            print("Warning: Invalid houses cusps, using rasi chart as fallback")
            return rasi_results.copy()
            
        bhava_results = []
        
        for p in rasi_results:
            p_long = p.get('longitude', 0)
            
            # Determine House based on Cusps
            planet_house = 0
            
            # Find which house the longitude falls into
            for i in range(12):
                cusp_start = houses_cusps[i]
                cusp_end = houses_cusps[(i + 1) % 12]
                
                # Handle the wrap-around case
                if cusp_end < cusp_start:
                    cusp_end += 360
                    p_long_adj = p_long if p_long >= cusp_start else p_long + 360
                else:
                    p_long_adj = p_long
                
                if cusp_start <= p_long_adj < cusp_end:
                    planet_house = i + 1
                    break
            
            if planet_house == 0:
                planet_house = 1
            
            # Calculate virtual sign for Bhava Chalit
            if p['id'] == 'Lagna':
                virtual_sign = lagna_sign
                bhava_house = 1
            else:
                bhava_house = planet_house
                virtual_sign = (lagna_sign + bhava_house - 1) % 12
            
            new_p = p.copy()
            new_p['sign'] = int(virtual_sign)
            new_p['house'] = bhava_house
            bhava_results.append(new_p)
            
        return bhava_results

    def get_chart_name(self, division_code):
        """Get display name for chart based on division code"""
        chart_names = {
            "D1": "ရာသီဇာတာ (D1)",
            "D2": "ငွေဇာတာ (D2)",
            "D4": "အိုးအိမ်ဇာတာ (D4)",
            "D7": "သားသမီးဇာတာ (D7)",
            "D9": "နဝင်းဇာတာ (D9)",
            "D10": "အလုပ်အကိုင်ဇာတာ (D10)",
            "D30": "ဒုက္ခဇာတာ (D30)",
            "D60": "အတိတ်ဘဝကံဇာတာ (D60)",
            "BHAVA": "ဘာဝဇာတာ"
        }
        return chart_names.get(division_code, "ရာသီဇာတာ (D1)")

    def update_sidebar_text(self, results, name, date, time, lat, lon, chart_type="ရာသီဇာတာ (D1)"):
        date_str = date.toString("dd.MM.yyyy")
        time_str = time.toString("hh:mm AP")
        
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

    def new_chart(self):
        self.txtName.clear()
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        
        # Clear chart widgets
        self.rasi_chart_widget.set_planet_data([])
        self.bhava_chart_widget.set_planet_data([])
        self.navamsa_chart_widget.set_planet_data([])
        
        # Clear sidebar
        self.sidebar_text.clear()
        
        # Reset to default layout
        self.setup_three_chart_layout()
        
        self.statusbar.showMessage("ဇာတာအသစ်အတွက် အဆင်သင့်ဖြစ်ပါပြီ")

    def open_chart(self):
        # Implement open chart functionality
        pass

    def save_chart(self):
        # Implement save chart functionality
        pass

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
        
        # Set Myanmar time as default
        default_index = -1
        for i in range(self.cboTimezone.count()):
            if abs(self.cboTimezone.itemData(i) - 6.5) < 0.01:
                default_index = i
                break
        
        if default_index >= 0:
            self.cboTimezone.setCurrentIndex(default_index)
        else:
            for i in range(self.cboTimezone.count()):
                if abs(self.cboTimezone.itemData(i)) < 0.01:
                    self.cboTimezone.setCurrentIndex(i)
                    break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Pyidaungsu")
    app.setFont(font)

    window = BharaniApp()
    window.showMaximized()
    sys.exit(app.exec_())