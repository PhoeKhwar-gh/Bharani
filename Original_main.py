# main.py
import sys
import os
import csv
import math
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QPushButton, QStyledItemDelegate, 
                             QCheckBox, QVBoxLayout, QListView, QFileDialog, QTextEdit, QWidget,
                             QHBoxLayout, QLabel, QComboBox, QTableView, QAbstractItemView, QFrame)
from PyQt5.QtCore import QDate, QTime, Qt, QItemSelectionModel
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem

from widgets.chart_widget import BurmeseChartWidget, ZODIAC_SIGNS_MM
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

# English sign names for calculations
ZODIAC_SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Sign nature classifications
MOVABLE_SIGNS = [1, 4, 7, 10]  # Aries, Cancer, Libra, Capricorn
FIXED_SIGNS = [2, 5, 8, 11]     # Taurus, Leo, Scorpio, Aquarius
DUAL_SIGNS = [3, 6, 9, 12]       # Gemini, Virgo, Sagittarius, Pisces

# Odd/Even signs (1-based)
ODD_SIGNS = [1, 3, 5, 7, 9, 11]
EVEN_SIGNS = [2, 4, 6, 8, 10, 12]


class BharaniApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup UI from designer file
        self.setupUi(self)
        
        # Initialize UI components
        self.init_ui()
        
        # === Set Swisseph Path ===
        ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
        swe.set_ephe_path(ephe_path)

        # Initialize variables
        self.location_data = defaultdict(list)
        self.custom_locations = []
        self.current_houses_cusps = None
        self.chart_widgets = {}  # Store references to chart widgets
        
        # Set default date and time
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        
        # Latitude/Longitude fields - initially read-only
        self.txtLat.setReadOnly(True)
        self.txtLon.setReadOnly(True)
        
        # === Load CSV Data ===
        self.load_location_data()  # ဒီ method ရှိရမယ်
        
        # === Populate Timezone ===
        self.populate_timezone_combo()
        
        # === Populate Step Combo ===
        self.populate_step_combo()
        
        # === Setup Chart Display ===
        self.setup_display_widgets()

        # === Connect Signals ===
        self.setup_connections()
        
        # Initialize division charts visibility based on checkbox
        self.toggle_division_charts(self.chkDivision.checkState())

    # ==================================================== #
    # ============= INITIALIZATION FUNCTIONS ============= #
    # ==================================================== #
    
    def init_ui(self):
        """Initialize UI components and settings"""
        # Set window title
        self.setWindowTitle("ဘရဏီ - ဗေဒင်ဇာတာတွက်စနစ်")
        
        # Populate Ayanamsa combo if not already populated
        if self.cboAyana.count() == 0:
            ayanamsa_list = [
                "Lahiri", "Krishnamurti", "Raman", "Fagan/Bradley",
                "Yukteshwar", "J2000", "Suryasiddhanta", 
                "True Citra / True Revati", "Galactic Center / Dhruva"
            ]
            self.cboAyana.addItems(ayanamsa_list)
        
        # Populate House System combo if not already populated
        if self.cboHouseSys.count() == 0:
            house_systems = ["Whole Sign", "Vehlow Equal", "Equal", "Placidus", "Sripati", "Porphyry"]
            self.cboHouseSys.addItems(house_systems)
            self.cboHouseSys.setCurrentText("Vehlow Equal")  # Default
        
        # Set default for step combo
        self.cboStep.setCurrentText("Day")
        
    def populate_step_combo(self):
        """Populate step combo with time units"""
        # Already populated in UI, just set tooltips
        self.cboStep.setItemData(0, "စက္ကန့်", Qt.ToolTipRole)
        self.cboStep.setItemData(1, "မိနစ်", Qt.ToolTipRole)
        self.cboStep.setItemData(2, "နာရီ", Qt.ToolTipRole)
        self.cboStep.setItemData(3, "ရက်", Qt.ToolTipRole)
        self.cboStep.setItemData(4, "လ", Qt.ToolTipRole)
        self.cboStep.setItemData(5, "နှစ်", Qt.ToolTipRole)

    # ==================================================== #
    # ============= HELPER FUNCTIONS ===================== #
    # ==================================================== #
    
    def sign_to_number(self, sign_name):
        """Convert English sign name to 1-based number (Aries=1)"""
        return ZODIAC_SIGNS_EN.index(sign_name) + 1

    def number_to_sign(self, num):
        """Convert 1-based number to English sign name"""
        return ZODIAC_SIGNS_EN[num - 1]

    def compute_nth_sign(self, from_sign_num, n):
        """Compute nth sign from given sign (1-based, cyclic)"""
        return ((from_sign_num - 1 + (n - 1)) % 12) + 1

    # ==================================================== #
    # ============= DIVISIONAL CHART CALCULATIONS ======== #
    # ==================================================== #

    def calculate_hora_d2(self, sign_num, degrees):
        """
        D2 - Hora calculation
        Odd signs: 0-15° -> Leo, 15-30° -> Cancer
        Even signs: 0-15° -> Cancer, 15-30° -> Leo
        """
        is_odd = sign_num in ODD_SIGNS
        
        if degrees < 15:
            if is_odd:
                div_sign_num = 5  # Leo
            else:
                div_sign_num = 4  # Cancer
        else:
            if is_odd:
                div_sign_num = 4  # Cancer
            else:
                div_sign_num = 5  # Leo
        
        div_deg = degrees if degrees < 15 else (degrees - 15)
        return div_sign_num, div_deg

    def calculate_saptamsa_d7(self, sign_num, degrees):
        """D7 - Saptamsa calculation"""
        amsa = 30.0 / 7  # 4.2857°
        compartment = int(degrees / amsa)  # 0-6
        
        if sign_num % 2 == 1:  # Odd signs
            div_sign_num = self.compute_nth_sign(sign_num, compartment + 1)
        else:  # Even signs
            div_sign_num = self.compute_nth_sign(sign_num, compartment + 7)
        
        div_deg = degrees % amsa
        return div_sign_num, div_deg

    def calculate_navamsa_d9(self, sign_num, degrees):
        """D9 - Navamsa calculation"""
        amsa = (3 + 20/60.0)  # 3.3333°
        compartment = int(degrees / amsa)  # 0-8
        
        if sign_num in MOVABLE_SIGNS:  # Movable
            base_start = sign_num
        elif sign_num in FIXED_SIGNS:  # Fixed
            base_start = self.compute_nth_sign(sign_num, 9)
        else:  # Dual
            base_start = self.compute_nth_sign(sign_num, 5)
        
        div_sign_num = self.compute_nth_sign(base_start, compartment + 1)
        div_deg = degrees % amsa
        return div_sign_num, div_deg

    def calculate_dasamsa_d10(self, sign_num, degrees):
        """D10 - Dasamsa calculation"""
        amsa = 3.0
        part = int(degrees / amsa)  # 0-9
        
        dasamsa_table = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],   # 1: Aries
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # 2: Taurus
            [3, 4, 5, 6, 7, 8, 9, 10, 11, 12], # 3: Gemini
            [4, 5, 6, 7, 8, 9, 10, 11, 12, 1], # 4: Cancer
            [5, 6, 7, 8, 9, 10, 11, 12, 1, 2], # 5: Leo
            [6, 7, 8, 9, 10, 11, 12, 1, 2, 3], # 6: Virgo
            [7, 8, 9, 10, 11, 12, 1, 2, 3, 4], # 7: Libra
            [8, 9, 10, 11, 12, 1, 2, 3, 4, 5], # 8: Scorpio
            [9, 10, 11, 12, 1, 2, 3, 4, 5, 6], # 9: Sagittarius
            [10, 11, 12, 1, 2, 3, 4, 5, 6, 7], # 10: Capricorn
            [11, 12, 1, 2, 3, 4, 5, 6, 7, 8],  # 11: Aquarius
            [12, 1, 2, 3, 4, 5, 6, 7, 8, 9],   # 12: Pisces
        ]
        
        div_sign_num = dasamsa_table[sign_num - 1][part]
        div_deg = degrees % amsa
        return div_sign_num, div_deg

    def calculate_dwadasamsa_d12(self, sign_num, degrees):
        """D12 - Dwadasamsa calculation"""
        amsa = 2.5
        compartment = int(degrees / amsa)  # 0-11
        
        div_sign_num = self.compute_nth_sign(sign_num, compartment + 1)
        div_deg = degrees % amsa
        return div_sign_num, div_deg

    def calculate_vimsamsa_d20(self, sign_num, degrees):
        """D20 - Vimsamsa calculation"""
        amsa = 1.5
        compartment = int(degrees / amsa)  # 0-19
        
        if sign_num in MOVABLE_SIGNS:  # Movable
            base = 1
        elif sign_num in FIXED_SIGNS:  # Fixed
            base = 9
        else:  # Dual
            base = 5
        
        div_sign_num = self.compute_nth_sign(base, compartment + 1)
        div_deg = degrees % amsa
        return div_sign_num, div_deg

    def calculate_trimsamsa_d30(self, sign_num, degrees):
        """D30 - Trimsamsa calculation"""
        if sign_num % 2 == 0:  # Even signs
            if degrees < 5:
                div_sign_num = 2  # Taurus
            elif degrees < 12:
                div_sign_num = 6  # Virgo
            elif degrees < 19:
                div_sign_num = 10  # Capricorn
            elif degrees < 24:
                div_sign_num = 12  # Pisces
            else:
                div_sign_num = 8  # Scorpio
        else:  # Odd signs
            if degrees < 5:
                div_sign_num = 1  # Aries
            elif degrees < 10:
                div_sign_num = 11  # Aquarius
            elif degrees < 18:
                div_sign_num = 9  # Sagittarius
            elif degrees < 25:
                div_sign_num = 3  # Gemini
            else:
                div_sign_num = 7  # Libra
        
        return div_sign_num, 0.0

    def calculate_shashtiamsa_d60(self, sign_num, degrees):
        """D60 - Shashtiamsa calculation"""
        amsa = 0.5  # 0.5 degrees per part
        part_1based = int(degrees / amsa) + 1  # 1-60
        compartment = ((part_1based - 1) % 12) + 1
        
        div_sign_num = self.compute_nth_sign(sign_num, compartment)
        div_deg = degrees % amsa
        return div_sign_num, div_deg

    def calculate_division_chart(self, rasi_results, chart_name):
        """Calculate division chart positions using proper Vedic formulas"""
        division_results = []
        
        chart_functions = {
            "D2": self.calculate_hora_d2,
            "D7": self.calculate_saptamsa_d7,
            "D9": self.calculate_navamsa_d9,
            "D10": self.calculate_dasamsa_d10,
            "D12": self.calculate_dwadasamsa_d12,
            "D20": self.calculate_vimsamsa_d20,
            "D30": self.calculate_trimsamsa_d30,
            "D60": self.calculate_shashtiamsa_d60
        }
        
        if chart_name not in chart_functions:
            print(f"Warning: Unknown chart type {chart_name}")
            return rasi_results
        
        calc_func = chart_functions[chart_name]
        
        for p in rasi_results:
            p_long = p.get('longitude', 0)
            sign_num_0based = int(p_long / 30)
            deg_in_sign = p_long % 30
            sign_num = sign_num_0based + 1
            
            div_sign_num, div_deg = calc_func(sign_num, deg_in_sign)
            
            div_sign_0based = div_sign_num - 1
            div_long = div_sign_0based * 30 + div_deg
            
            new_p = p.copy()
            new_p['longitude'] = div_long
            new_p['sign'] = div_sign_0based
            new_p['deg'] = int(div_deg)
            new_p['min'] = int((div_deg * 60) % 60)
            division_results.append(new_p)
        
        return division_results

    # ==================================================== #
    # ============= UI SETUP FUNCTIONS =================== #
    # ==================================================== #

    def populate_timezone_combo(self):
        """Populate cboTimezone with world time zones"""
        timezones = [
            ("UTC-12:00", -12.0), ("UTC-11:00", -11.0), ("UTC-10:00", -10.0),
            ("UTC-09:30", -9.5), ("UTC-09:00", -9.0), ("UTC-08:00", -8.0),
            ("UTC-07:00", -7.0), ("UTC-06:00", -6.0), ("UTC-05:00", -5.0),
            ("UTC-04:30", -4.5), ("UTC-04:00", -4.0), ("UTC-03:30", -3.5),
            ("UTC-03:00", -3.0), ("UTC-02:00", -2.0), ("UTC-01:00", -1.0),
            ("UTC±00:00", 0.0), ("UTC+01:00", 1.0), ("UTC+02:00", 2.0),
            ("UTC+03:00", 3.0), ("UTC+03:30", 3.5), ("UTC+04:00", 4.0),
            ("UTC+04:30", 4.5), ("UTC+05:00", 5.0), ("UTC+05:30", 5.5),
            ("UTC+05:45", 5.75), ("UTC+06:00", 6.0), ("UTC+06:30", 6.5),
            ("UTC+07:00", 7.0), ("UTC+08:00", 8.0), ("UTC+08:45", 8.75),
            ("UTC+09:00", 9.0), ("UTC+09:30", 9.5), ("UTC+10:00", 10.0),
            ("UTC+10:30", 10.5), ("UTC+11:00", 11.0), ("UTC+12:00", 12.0),
            ("UTC+12:45", 12.75), ("UTC+13:00", 13.0), ("UTC+14:00", 14.0),
        ]
        
        self.cboTimezone.clear()
        for tz_name, tz_offset in timezones:
            self.cboTimezone.addItem(tz_name, tz_offset)
        
        # Set default to Myanmar Time (UTC+6:30)
        for i in range(self.cboTimezone.count()):
            if self.cboTimezone.itemData(i) == 6.5:
                self.cboTimezone.setCurrentIndex(i)
                break

# တနည်း
    # def setup_display_widgets(self):
        """Setup the chart display grid - ခင်ဗျားရဲ့ ပုံစံအတိုင်း"""
        # Get the scroll area contents
        container = self.scrollAreaWidgetContents
        
        # Clear existing layout if any
        old_layout = container.layout()
        if old_layout is not None:
            # Delete all widgets in the old layout
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # Create main layout for scroll area
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # === ပထမအတန်း - အမြဲပြမယ့် ဇာတာသုံးခု (Rasi, Bhava, Navamsa) ===
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(10)
        
        # Rasi chart (D1) - ရာသီစက်
        self.rasi_chart_widget = BurmeseChartWidget()
        self.rasi_chart_widget.setFixedSize(400, 400)
        self.rasi_chart_widget.set_planet_data([], True, "D1 - Rāśi")
        first_row_layout.addWidget(self.rasi_chart_widget)
        
        # Bhava chart - ဘာဝစက်
        self.bhava_chart_widget = BurmeseChartWidget()
        self.bhava_chart_widget.setFixedSize(400, 400)
        self.bhava_chart_widget.set_planet_data([], False, "Bhava - ဘာဝ")
        first_row_layout.addWidget(self.bhava_chart_widget)
        
        # Navamsa chart (D9) - နဝင်းစက်
        self.navamsa_chart_widget = BurmeseChartWidget()
        self.navamsa_chart_widget.setFixedSize(400, 400)
        self.navamsa_chart_widget.set_planet_data([], False, "D9 - Navāṁśa")
        first_row_layout.addWidget(self.navamsa_chart_widget)
        
        main_layout.addLayout(first_row_layout)
        
        # Divider Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #999; height: 2px; margin: 10px 0;")
        main_layout.addWidget(line)
        
        # === Division Charts Container (checkbox နဲ့ hide/show) ===
        self.division_charts_container = QWidget()
        self.division_charts_container.setVisible(self.chkDivision.isChecked())
        
        division_layout = QVBoxLayout(self.division_charts_container)
        division_layout.setSpacing(15)
        
        # ဒုတိယအတန်း - D2, D7, D10
        second_row_layout = QHBoxLayout()
        second_row_layout.setSpacing(10)
        
        self.d2_chart_widget = BurmeseChartWidget()
        self.d2_chart_widget.setFixedSize(400, 400)
        self.d2_chart_widget.set_planet_data([], True, "D2 - Hora")
        second_row_layout.addWidget(self.d2_chart_widget)
        
        self.d7_chart_widget = BurmeseChartWidget()
        self.d7_chart_widget.setFixedSize(400, 400)
        self.d7_chart_widget.set_planet_data([], True, "D7 - Saptāṁśa")
        second_row_layout.addWidget(self.d7_chart_widget)
        
        self.d10_chart_widget = BurmeseChartWidget()
        self.d10_chart_widget.setFixedSize(400, 400)
        self.d10_chart_widget.set_planet_data([], True, "D10 - Daśāṁśa")
        second_row_layout.addWidget(self.d10_chart_widget)
        
        division_layout.addLayout(second_row_layout)
        
        # တတိယအတန်း - D12, D20, D30
        third_row_layout = QHBoxLayout()
        third_row_layout.setSpacing(10)
        
        self.d12_chart_widget = BurmeseChartWidget()
        self.d12_chart_widget.setFixedSize(400, 400)
        self.d12_chart_widget.set_planet_data([], True, "D12 - Dvādashāṁśa")
        third_row_layout.addWidget(self.d12_chart_widget)
        
        self.d20_chart_widget = BurmeseChartWidget()
        self.d20_chart_widget.setFixedSize(400, 400)
        self.d20_chart_widget.set_planet_data([], True, "D20 - Vimshāṁśa")
        third_row_layout.addWidget(self.d20_chart_widget)
        
        self.d30_chart_widget = BurmeseChartWidget()
        self.d30_chart_widget.setFixedSize(400, 400)
        self.d30_chart_widget.set_planet_data([], True, "D30 - Trimshāṁśa")
        third_row_layout.addWidget(self.d30_chart_widget)
        
        division_layout.addLayout(third_row_layout)
        
        # စတုတ္ထအတန်း - D60 (တစ်ခုတည်း - အလယ်မှာ)
        fourth_row_layout = QHBoxLayout()
        fourth_row_layout.setSpacing(10)
        
        # Left spacer
        fourth_row_layout.addStretch(1)
        
        self.d60_chart_widget = BurmeseChartWidget()
        self.d60_chart_widget.setFixedSize(400, 400)
        self.d60_chart_widget.set_planet_data([], True, "D60 - Shashtyāṁśa")
        fourth_row_layout.addWidget(self.d60_chart_widget)
        
        # Right spacer
        fourth_row_layout.addStretch(1)
        
        division_layout.addLayout(fourth_row_layout)
        
        # Store all chart widgets in dictionary for easy access
        self.chart_widgets = {
            'D1': self.rasi_chart_widget,
            'Bhava': self.bhava_chart_widget,
            'D2': self.d2_chart_widget,
            'D7': self.d7_chart_widget,
            'D9': self.navamsa_chart_widget,
            'D10': self.d10_chart_widget,
            'D12': self.d12_chart_widget,
            'D20': self.d20_chart_widget,
            'D30': self.d30_chart_widget,
            'D60': self.d60_chart_widget
        }
        
        main_layout.addWidget(self.division_charts_container)
        main_layout.addStretch(1)
        
        # Setup sidebar
        self.setup_sidebar()

# တနည်း အကွက်တစ်ကွက်ချင်းစီ အရောင်ဖြည့်ခြင်း...
    # def setup_display_widgets(self):
    #     """Setup the chart display grid - ခင်ဗျားရဲ့ ပုံစံအတိုင်း"""
    #     # Get the scroll area contents
    #     container = self.scrollAreaWidgetContents
        
    #     # Clear existing layout if any
    #     old_layout = container.layout()
    #     if old_layout is not None:
    #         # Delete all widgets in the old layout
    #         while old_layout.count():
    #             item = old_layout.takeAt(0)
    #             if item.widget():
    #                 item.widget().deleteLater()
        
    #     # Create main layout for scroll area
    #     main_layout = QVBoxLayout(container)
    #     main_layout.setSpacing(15)
    #     main_layout.setContentsMargins(10, 10, 10, 10)
        
    #     # === ပထမအတန်း - အမြဲပြမယ့် ဇာတာသုံးခု (Rasi, Bhava, Navamsa) ===
    #     first_row_layout = QHBoxLayout()
    #     first_row_layout.setSpacing(10)
        
    #     # Rasi chart (D1) - ရာသီစက်
    #     self.rasi_chart_widget = BurmeseChartWidget()
    #     self.rasi_chart_widget.setFixedSize(400, 400)
    #     self.rasi_chart_widget.set_planet_data([], True, "D1 - Rāśi")
    #     first_row_layout.addWidget(self.rasi_chart_widget)
        
    #     # Bhava chart - ဘာဝစက်
    #     self.bhava_chart_widget = BurmeseChartWidget()
    #     self.bhava_chart_widget.setFixedSize(400, 400)
    #     self.bhava_chart_widget.set_planet_data([], False, "Bhava - ဘာဝ")
    #     first_row_layout.addWidget(self.bhava_chart_widget)
        
    #     # Navamsa chart (D9) - နဝင်းစက်
    #     self.navamsa_chart_widget = BurmeseChartWidget()
    #     self.navamsa_chart_widget.setFixedSize(400, 400)
    #     self.navamsa_chart_widget.set_planet_data([], False, "D9 - Navāṁśa")
    #     first_row_layout.addWidget(self.navamsa_chart_widget)
        
    #     main_layout.addLayout(first_row_layout)
        
    #     # Divider Line
    #     line = QFrame()
    #     line.setFrameShape(QFrame.HLine)
    #     line.setFrameShadow(QFrame.Sunken)
    #     line.setStyleSheet("background-color: #999; height: 2px; margin: 10px 0;")
    #     main_layout.addWidget(line)
        
    #     # === Division Charts Container (checkbox နဲ့ hide/show) ===
    #     self.division_charts_container = QWidget()
    #     self.division_charts_container.setVisible(self.chkDivision.isChecked())
        
    #     division_layout = QVBoxLayout(self.division_charts_container)
    #     division_layout.setSpacing(15)
    #     division_layout.setContentsMargins(0, 0, 0, 0)
        
    #     # ဒုတိယအတန်း - D2, D7, D10
    #     second_row_layout = QHBoxLayout()
    #     second_row_layout.setSpacing(10)
        
    #     # D2 Chart
    #     d2_frame = QFrame()
    #     d2_frame.setFrameShape(QFrame.StyledPanel)
    #     d2_frame.setStyleSheet("QFrame { background-color: #ffe6e6; border: 1px solid #ff9999; border-radius: 5px; }")
    #     d2_layout = QVBoxLayout(d2_frame)
    #     self.d2_chart_widget = BurmeseChartWidget()
    #     self.d2_chart_widget.setFixedSize(380, 380)
    #     self.d2_chart_widget.set_planet_data([], True, "D2 - Hora")
    #     d2_layout.addWidget(self.d2_chart_widget)
    #     second_row_layout.addWidget(d2_frame)
        
    #     # D7 Chart
    #     d7_frame = QFrame()
    #     d7_frame.setFrameShape(QFrame.StyledPanel)
    #     d7_frame.setStyleSheet("QFrame { background-color: #e6f0ff; border: 1px solid #99b3ff; border-radius: 5px; }")
    #     d7_layout = QVBoxLayout(d7_frame)
    #     self.d7_chart_widget = BurmeseChartWidget()
    #     self.d7_chart_widget.setFixedSize(380, 380)
    #     self.d7_chart_widget.set_planet_data([], True, "D7 - Saptāṁśa")
    #     d7_layout.addWidget(self.d7_chart_widget)
    #     second_row_layout.addWidget(d7_frame)
        
    #     # D10 Chart
    #     d10_frame = QFrame()
    #     d10_frame.setFrameShape(QFrame.StyledPanel)
    #     d10_frame.setStyleSheet("QFrame { background-color: #e6ffe6; border: 1px solid #99cc99; border-radius: 5px; }")
    #     d10_layout = QVBoxLayout(d10_frame)
    #     self.d10_chart_widget = BurmeseChartWidget()
    #     self.d10_chart_widget.setFixedSize(380, 380)
    #     self.d10_chart_widget.set_planet_data([], True, "D10 - Daśāṁśa")
    #     d10_layout.addWidget(self.d10_chart_widget)
    #     second_row_layout.addWidget(d10_frame)
        
    #     division_layout.addLayout(second_row_layout)
        
    #     # တတိယအတန်း - D12, D20, D30
    #     third_row_layout = QHBoxLayout()
    #     third_row_layout.setSpacing(10)
        
    #     # D12 Chart
    #     d12_frame = QFrame()
    #     d12_frame.setFrameShape(QFrame.StyledPanel)
    #     d12_frame.setStyleSheet("QFrame { background-color: #fff0e6; border: 1px solid #ffcc99; border-radius: 5px; }")
    #     d12_layout = QVBoxLayout(d12_frame)
    #     self.d12_chart_widget = BurmeseChartWidget()
    #     self.d12_chart_widget.setFixedSize(380, 380)
    #     self.d12_chart_widget.set_planet_data([], True, "D12 - Dvādashāṁśa")
    #     d12_layout.addWidget(self.d12_chart_widget)
    #     third_row_layout.addWidget(d12_frame)
        
    #     # D20 Chart
    #     d20_frame = QFrame()
    #     d20_frame.setFrameShape(QFrame.StyledPanel)
    #     d20_frame.setStyleSheet("QFrame { background-color: #f0e6ff; border: 1px solid #cc99ff; border-radius: 5px; }")
    #     d20_layout = QVBoxLayout(d20_frame)
    #     self.d20_chart_widget = BurmeseChartWidget()
    #     self.d20_chart_widget.setFixedSize(380, 380)
    #     self.d20_chart_widget.set_planet_data([], True, "D20 - Vimshāṁśa")
    #     d20_layout.addWidget(self.d20_chart_widget)
    #     third_row_layout.addWidget(d20_frame)
        
    #     # D30 Chart
    #     d30_frame = QFrame()
    #     d30_frame.setFrameShape(QFrame.StyledPanel)
    #     d30_frame.setStyleSheet("QFrame { background-color: #e6ffff; border: 1px solid #99ffff; border-radius: 5px; }")
    #     d30_layout = QVBoxLayout(d30_frame)
    #     self.d30_chart_widget = BurmeseChartWidget()
    #     self.d30_chart_widget.setFixedSize(380, 380)
    #     self.d30_chart_widget.set_planet_data([], True, "D30 - Trimshāṁśa")
    #     d30_layout.addWidget(self.d30_chart_widget)
    #     third_row_layout.addWidget(d30_frame)
        
    #     division_layout.addLayout(third_row_layout)
        
    #     # စတုတ္ထအတန်း - D60 (ဘယ်ဘက်ကပ်)
    #     fourth_row_layout = QHBoxLayout()
    #     fourth_row_layout.setSpacing(10)
        
    #     # D60 Chart (ဘယ်ဘက်ကပ်)
    #     d60_frame = QFrame()
    #     d60_frame.setFrameShape(QFrame.StyledPanel)
    #     d60_frame.setStyleSheet("QFrame { background-color: #ffe6f0; border: 1px solid #ff99cc; border-radius: 5px; }")
    #     d60_layout = QVBoxLayout(d60_frame)
    #     self.d60_chart_widget = BurmeseChartWidget()
    #     self.d60_chart_widget.setFixedSize(380, 380)
    #     self.d60_chart_widget.set_planet_data([], True, "D60 - Shashtyāṁśa")
    #     d60_layout.addWidget(self.d60_chart_widget)
    #     fourth_row_layout.addWidget(d60_frame)
        
    #     # ညာဘက်မှာ spacer ထည့်မယ် (ဘယ်ဘက်ကပ်ဖို့)
    #     fourth_row_layout.addStretch(1)
        
    #     division_layout.addLayout(fourth_row_layout)
        
    #     # Store all chart widgets in dictionary for easy access
    #     self.chart_widgets = {
    #         'D1': self.rasi_chart_widget,
    #         'Bhava': self.bhava_chart_widget,
    #         'D2': self.d2_chart_widget,
    #         'D7': self.d7_chart_widget,
    #         'D9': self.navamsa_chart_widget,
    #         'D10': self.d10_chart_widget,
    #         'D12': self.d12_chart_widget,
    #         'D20': self.d20_chart_widget,
    #         'D30': self.d30_chart_widget,
    #         'D60': self.d60_chart_widget
    #     }
        
    #     # Store frames for later use (optional)
    #     self.chart_frames = {
    #         'D2': d2_frame,
    #         'D7': d7_frame,
    #         'D10': d10_frame,
    #         'D12': d12_frame,
    #         'D20': d20_frame,
    #         'D30': d30_frame,
    #         'D60': d60_frame
    #     }
        
    #     main_layout.addWidget(self.division_charts_container)
    #     main_layout.addStretch(1)
        
    #     # Setup sidebar
    #     self.setup_sidebar()

# တတိယနည်း လမ်း
    def setup_display_widgets(self):
        """Setup the chart display grid - ခေါင်းစီးမပါပဲ ဇာတာများသာပြမည်"""
        # Get the scroll area contents
        container = self.scrollAreaWidgetContents
        
        # Check if container already has a layout
        old_layout = container.layout()
        if old_layout is not None:
            # Delete all widgets in the old layout
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # Delete the old layout
            QWidget().setLayout(old_layout)
        
        # Create new layout for container
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Clear existing chart widgets references
        self.chart_widgets = {}
        
        # === ပထမအတန်း - အမြဲပြမယ့် ဇာတာသုံးခု (Rasi, Bhava, Navamsa) ===
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(10)
        
        # Rasi chart (D1) - ရာသီစက်
        self.rasi_chart_widget = BurmeseChartWidget()
        self.rasi_chart_widget.setFixedSize(400, 400)
        self.rasi_chart_widget.set_planet_data([], True, "D1 - Rāśi")
        first_row_layout.addWidget(self.rasi_chart_widget)
        self.chart_widgets['D1'] = self.rasi_chart_widget
        
        # Bhava chart - ဘာဝစက်
        self.bhava_chart_widget = BurmeseChartWidget()
        self.bhava_chart_widget.setFixedSize(400, 400)
        self.bhava_chart_widget.set_planet_data([], False, "Bhava - ဘာဝ")
        first_row_layout.addWidget(self.bhava_chart_widget)
        self.chart_widgets['Bhava'] = self.bhava_chart_widget
        
        # Navamsa chart (D9) - နဝင်းစက်
        self.navamsa_chart_widget = BurmeseChartWidget()
        self.navamsa_chart_widget.setFixedSize(400, 400)
        self.navamsa_chart_widget.set_planet_data([], False, "D9 - Navāṁśa")
        first_row_layout.addWidget(self.navamsa_chart_widget)
        self.chart_widgets['D9'] = self.navamsa_chart_widget
        
        main_layout.addLayout(first_row_layout)
        
        # Divider Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #999; height: 2px; margin: 10px 0;")
        main_layout.addWidget(line)
        
        # === Division Charts Container (checkbox နဲ့ hide/show) ===
        self.division_charts_container = QWidget()
        self.division_charts_container.setVisible(self.chkDivision.isChecked())
        
        division_layout = QVBoxLayout(self.division_charts_container)
        division_layout.setSpacing(15)
        division_layout.setContentsMargins(0, 0, 0, 0)
        
        # === ဒုတိယအတန်း - D2, D7, D10 ===
        second_row_layout = QHBoxLayout()
        second_row_layout.setSpacing(10)
        
        self.d2_chart_widget = BurmeseChartWidget()
        self.d2_chart_widget.setFixedSize(400, 400)
        self.d2_chart_widget.set_planet_data([], True, "D2 - Hora")
        second_row_layout.addWidget(self.d2_chart_widget)
        self.chart_widgets['D2'] = self.d2_chart_widget
        
        self.d7_chart_widget = BurmeseChartWidget()
        self.d7_chart_widget.setFixedSize(400, 400)
        self.d7_chart_widget.set_planet_data([], True, "D7 - Saptāṁśa")
        second_row_layout.addWidget(self.d7_chart_widget)
        self.chart_widgets['D7'] = self.d7_chart_widget
        
        self.d10_chart_widget = BurmeseChartWidget()
        self.d10_chart_widget.setFixedSize(400, 400)
        self.d10_chart_widget.set_planet_data([], True, "D10 - Daśāṁśa")
        second_row_layout.addWidget(self.d10_chart_widget)
        self.chart_widgets['D10'] = self.d10_chart_widget
        
        division_layout.addLayout(second_row_layout)
        
        # === တတိယအတန်း - D12, D20, D30 ===
        third_row_layout = QHBoxLayout()
        third_row_layout.setSpacing(10)
        
        self.d12_chart_widget = BurmeseChartWidget()
        self.d12_chart_widget.setFixedSize(400, 400)
        self.d12_chart_widget.set_planet_data([], True, "D12 - Dvādashāṁśa")
        third_row_layout.addWidget(self.d12_chart_widget)
        self.chart_widgets['D12'] = self.d12_chart_widget
        
        self.d20_chart_widget = BurmeseChartWidget()
        self.d20_chart_widget.setFixedSize(400, 400)
        self.d20_chart_widget.set_planet_data([], True, "D20 - Vimshāṁśa")
        third_row_layout.addWidget(self.d20_chart_widget)
        self.chart_widgets['D20'] = self.d20_chart_widget
        
        self.d30_chart_widget = BurmeseChartWidget()
        self.d30_chart_widget.setFixedSize(400, 400)
        self.d30_chart_widget.set_planet_data([], True, "D30 - Trimshāṁśa")
        third_row_layout.addWidget(self.d30_chart_widget)
        self.chart_widgets['D30'] = self.d30_chart_widget
        
        division_layout.addLayout(third_row_layout)
        
        # === စတုတ္ထအတန်း - D60 (ဘယ်ဘက်ကပ်) ===
        fourth_row_layout = QHBoxLayout()
        fourth_row_layout.setSpacing(10)
        
        self.d60_chart_widget = BurmeseChartWidget()
        self.d60_chart_widget.setFixedSize(400, 400)
        self.d60_chart_widget.set_planet_data([], True, "D60 - Shashtyāṁśa")
        fourth_row_layout.addWidget(self.d60_chart_widget)
        self.chart_widgets['D60'] = self.d60_chart_widget
        
        # ညာဘက်မှာ spacer ထည့်မယ် (ဘယ်ဘက်ကပ်ဖို့)
        fourth_row_layout.addStretch(1)
        
        division_layout.addLayout(fourth_row_layout)
        
        main_layout.addWidget(self.division_charts_container)
        main_layout.addStretch(1)
        
        # Setup sidebar
        self.setup_sidebar()

    def setup_sidebar(self):
        """Setup the sidebar text widget"""
        # Get the scroll area contents for sidebar
        container = self.scrollAreaWidgetContents_2
        
        # Clear existing layout
        old_layout = container.layout()
        if old_layout is not None:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            old_layout = QVBoxLayout(container)
        
        # Create sidebar text widget
        self.sidebar_text = QTextEdit()
        self.sidebar_text.setReadOnly(True)
        self.sidebar_text.setFont(QFont("Pyidaungsu", 10))
        self.sidebar_text.setMinimumHeight(600)
        
        # Add to layout
        old_layout.addWidget(self.sidebar_text)

    def setup_connections(self):
        """Setup signal connections"""
        # Location connections
        self.cboState.currentTextChanged.connect(self.on_state_changed)
        self.cboCity.currentTextChanged.connect(self.on_town_changed)
        
        # Button connections
        self.btnCalculate.clicked.connect(self.calculate_chart)
        self.btnEditPlace.clicked.connect(self.toggle_place_edit)
        self.btnPreVal.clicked.connect(self.previous_chart)
        self.btnNextVal.clicked.connect(self.next_chart)
        
        # Menu connections
        self.actionNew.triggered.connect(self.new_chart)
        self.actionOpen.triggered.connect(self.open_chart)
        self.actionSave.triggered.connect(self.save_chart)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout_Me.triggered.connect(self.show_about)
        
        # Checkbox connections
        self.chkDivision.stateChanged.connect(self.toggle_division_charts)
        
        # Chart selection combo
        self.cboCheckable.currentIndexChanged.connect(self.on_chart_selected)
        
        # Step combo
        self.cboStep.currentTextChanged.connect(self.on_step_changed)

    def toggle_division_charts(self, state):
        """Toggle visibility of division charts"""
        self.division_charts_container.setVisible(state == Qt.Checked)

    def previous_chart(self):
        """Navigate to previous chart"""
        current_index = self.cboCheckable.currentIndex()
        if current_index > 0:
            self.cboCheckable.setCurrentIndex(current_index - 1)
        else:
            self.statusbar.showMessage("ပထမဆုံးဇာတာဖြစ်ပါသည်")

    def next_chart(self):
        """Navigate to next chart"""
        current_index = self.cboCheckable.currentIndex()
        if current_index < self.cboCheckable.count() - 1:
            self.cboCheckable.setCurrentIndex(current_index + 1)
        else:
            self.statusbar.showMessage("နောက်ဆုံးဇာတာဖြစ်ပါသည်")

    def on_chart_selected(self, index):
        """Handle chart selection from combo box"""
        if index >= 0:
            chart_name = self.cboCheckable.currentText()
            self.statusbar.showMessage(f"{chart_name} ဇာတာကို ရွေးချယ်ပြီးပါပြီ")

    def on_step_changed(self, step_text):
        """Handle step combo change"""
        self.statusbar.showMessage(f"အဆင့်: {step_text} သို့ ပြောင်းလဲပြီးပါပြီ")

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>ဘရဏီ - ဗေဒင်ဇာတာတွက်စနစ်</h2>
        <p>ဗားရှင်း 1.0.0</p>
        <p>မြန်မာ့ရိုးရာ ဗေဒင်ဇာတာကို ကွန်ပျူတာဖြင့် တွက်ချက်ပေးသော ဆော့ဖ်ဝဲလ်</p>
        <p>အင်္ဂါရပ်များ:</p>
        <ul>
            <li>D1 မှ D60 အထိ ဝဂ္ဂဇာတာများ</li>
            <li>အာယနအမျိုးမျိုး ရွေးချယ်နိုင်</li>
            <li>ဘာဝခွဲစနစ်အမျိုးမျိုး</li>
            <li>မြန်မာလို ဇာတာဖော်ပြချက်</li>
        </ul>
        <p>© 2024 မူပိုင်ခွင့်လက်ဝယ်ရှိသည်။</p>
        """
        QMessageBox.about(self, "အကြောင်း", about_text)

    # ==================================================== #
    # ============= DATA LOADING FUNCTIONS =============== #
    # ==================================================== #

    def load_location_data(self):
        """Load location data from CSV file"""
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
                
            # Populate chart selection combo with available charts
            self.populate_chart_selection()
                    
        except FileNotFoundError:
            QMessageBox.warning(self, "ဖိုင်မတွေ့", "dataCSV.csv ဖိုင်မတွေ့ပါ။")
            self.create_sample_location_data()
        except Exception as e:
            QMessageBox.critical(self, "အမှား", f"ဒေတာဖိုင်ဖတ်ရာတွင် အမှားရှိနေသည်:\n{str(e)}")

    def populate_chart_selection(self):
        """Populate the chart selection combo box"""
        chart_list = [
            "Rasi (D1)", "Bhava", "Navamsa (D9)",
            "Hora (D2)", "Saptamsa (D7)", "Dasamsa (D10)",
            "Dwadasamsa (D12)", "Vimsamsa (D20)", "Trimsamsa (D30)",
            "Shashtiamsa (D60)"
        ]
        self.cboCheckable.clear()
        self.cboCheckable.addItems(chart_list)

    def create_sample_location_data(self):
        """Create sample location data if CSV not found"""
        sample_data = {
            "ရန်ကုန်တိုင်း": [("ရန်ကုန်", "16.8661", "96.1951")],
            "မန္တလေးတိုင်း": [("မန္တလေး", "21.9588", "96.0891")],
            "နေပြည်တော်": [("နေပြည်တော်", "19.7633", "96.0785")]
        }
        self.location_data.update(sample_data)
        states = sorted(self.location_data.keys())
        self.cboState.clear()
        self.cboState.addItems(states)
        if states:
            self.cboState.setCurrentText(states[0])
            self.on_state_changed(states[0])

    def on_state_changed(self, state):
        """Handle state selection change"""
        self.cboCity.clear()
        self.txtLat.clear()
        self.txtLon.clear()
        if state in self.location_data:
            towns = [item[0] for item in self.location_data[state]]
            self.cboCity.addItems(towns)
            if towns:
                self.cboCity.setCurrentIndex(0)

    def on_town_changed(self, town):
        """Handle town selection change"""
        state = self.cboState.currentText()
        if not state or not town:
            return
        for t, lat, lon in self.location_data[state]:
            if t == town:
                self.txtLat.setText(lat)
                self.txtLon.setText(lon)
                break

    def toggle_place_edit(self):
        """Toggle latitude/longitude edit mode"""
        is_readonly = self.txtLat.isReadOnly()
        self.txtLat.setReadOnly(not is_readonly)
        self.txtLon.setReadOnly(not is_readonly)
        if is_readonly:
            self.btnEditPlace.setText("သိမ်း")
            self.txtLat.setFocus()
        else:
            self.btnEditPlace.setText("+/-")
            # Save custom location if both fields are filled
            if self.txtLat.text() and self.txtLon.text():
                self.save_custom_location()

    def save_custom_location(self):
        """Save custom location data"""
        state = "ကိုယ်ပိုင်နေရာ"
        town = "ကိုယ်ပိုင်နေရာ"
        lat = self.txtLat.text()
        lon = self.txtLon.text()
        
        # Add to location data if not exists
        if state not in self.location_data:
            self.location_data[state] = []
            self.cboState.addItem(state)
        
        # Check if this location already exists
        exists = False
        for t, l, ln in self.location_data[state]:
            if t == town and l == lat and ln == lon:
                exists = True
                break
        
        if not exists:
            self.location_data[state].append((town, lat, lon))
            self.statusbar.showMessage("နေရာသစ် သိမ်းဆည်းပြီးပါပြီ")

    # ==================================================== #
    # ============= CHART CALCULATION ==================== #
    # ==================================================== #

    def get_ayanamsa_flag(self):
        """Get ayanamsa flag based on selection"""
        ayanamsa_name = self.cboAyana.currentText()
        ayanamsa_map = {
            "Lahiri": swe.SIDM_LAHIRI,
            "Krishnamurti": swe.SIDM_KRISHNAMURTI,
            "Raman": swe.SIDM_RAMAN,
            "Fagan/Bradley": swe.SIDM_FAGAN_BRADLEY,
            "Yukteshwar": swe.SIDM_YUKTESHWAR,
            "J2000": swe.SIDM_J2000,
            "Suryasiddhanta": swe.SIDM_SURYASIDDHANTA,
            "True Citra / True Revati": swe.SIDM_TRUE_CITRA,
            "Galactic Center / Dhruva": swe.SIDM_GALCENT_0SAG
        }
        return ayanamsa_map.get(ayanamsa_name, swe.SIDM_LAHIRI)

    def get_house_system_code(self):
        """Get house system code based on selection"""
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

    def validate_coordinates(self, lat, lon):
        """Validate latitude and longitude values"""
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            
            if not (-90 <= lat_float <= 90):
                raise ValueError("လတ္တီတွဒ်သည် -90 မှ 90 အတွင်းဖြစ်ရမည်")
            if not (-180 <= lon_float <= 180):
                raise ValueError("လောင်ဂျီတွဒ်သည် -180 မှ 180 အတွင်းဖြစ်ရမည်")
            
            return True, lat_float, lon_float
        except ValueError as e:
            return False, None, None

    def calculate_chart(self):
        """Main chart calculation function"""
        try:
            name = self.txtName.text().strip()
            if not name:
                QMessageBox.warning(self, "အမည်ထည့်ရန်", "ကျေးဇူးပြု၍ အမည်ထည့်သွင်းပါ")
                return

            # Get birth date and time
            birth_date = self.cboDate.date()
            birth_time = self.cboTime.time()
            
            year = birth_date.year()
            month = birth_date.month()
            day = birth_date.day()
            hour = birth_time.hour()
            minute = birth_time.minute()
            second = birth_time.second()
            
            # Timezone adjustment
            tz_offset = self.cboTimezone.currentData()
            if tz_offset is None:
                tz_offset = 6.5
            
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
            
            # Julian day
            jd = swe.julday(year, month, day, utc_hour)
            
            # Get location
            house_system_code = self.get_house_system_code()
            
            lat_str = self.txtLat.text().strip()
            lon_str = self.txtLon.text().strip()
            
            if not lat_str or not lon_str:
                QMessageBox.warning(self, "တည်နေရာ အမှား", "လတ္တီတွဒ်/လောင်ဂျီတွဒ် မရှိပါ။")
                return
                
            # Validate coordinates
            is_valid, latitude, longitude = self.validate_coordinates(lat_str, lon_str)
            if not is_valid:
                QMessageBox.warning(self, "တည်နေရာ အမှား", "လတ္တီတွဒ်/လောင်ဂျီတွဒ် မှားယွင်းနေပါသည်")
                return

            # Set ayanamsa
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

            # Calculate houses for all planets (for Rasi chart)
            asc_sign = results[0]['sign']
            for planet in results:
                if planet['id'] != 'Lagna':
                    planet_sign = planet['sign']
                    house_number = (planet_sign + 12 - asc_sign) % 12 + 1
                    planet['house'] = house_number

            # Calculate divisional charts
            d1_results = results
            d2_results = self.calculate_division_chart(results, "D2")
            d7_results = self.calculate_division_chart(results, "D7")
            d9_results = self.calculate_division_chart(results, "D9")
            d10_results = self.calculate_division_chart(results, "D10")
            d12_results = self.calculate_division_chart(results, "D12")
            d20_results = self.calculate_division_chart(results, "D20")
            d30_results = self.calculate_division_chart(results, "D30")
            d60_results = self.calculate_division_chart(results, "D60")

            # Update chart widgets
            self.rasi_chart_widget.set_planet_data(d1_results, True, "D1 - Rāśi")
            self.bhava_chart_widget.set_planet_data(d1_results, False, "Bhava - ဘာဝ")
            self.navamsa_chart_widget.set_planet_data(d9_results, False, "D9 - Navāṁśa")
            
            # Update division charts
            self.d2_chart_widget.set_planet_data(d2_results, True, "D2 - Hora")
            self.d7_chart_widget.set_planet_data(d7_results, True, "D7 - Saptāṁśa")
            self.d10_chart_widget.set_planet_data(d10_results, True, "D10 - Daśāṁśa")
            self.d12_chart_widget.set_planet_data(d12_results, True, "D12 - Dvādashāṁśa")
            self.d20_chart_widget.set_planet_data(d20_results, True, "D20 - Vimshāṁśa")
            self.d30_chart_widget.set_planet_data(d30_results, True, "D30 - Trimshāṁśa")
            self.d60_chart_widget.set_planet_data(d60_results, True, "D60 - Shashtyāṁśa")

            # Update sidebar with chart info
            self.update_sidebar_text(d1_results, name, birth_date, birth_time, latitude, longitude)

            self.statusbar.showMessage(f"{name} ၏ ဇာတာများ တွက်ချက်ပြီးပါပြီ")
            
        except Exception as e:
            QMessageBox.critical(self, "တွက်ချက်မှု အမှား", f"တွက်ချက်မှု မအောင်မြင်ပါ:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def update_sidebar_text(self, results, name, date, time, lat, lon):
        """Update sidebar text with chart information"""
        date_str = date.toString("dd.MM.yyyy")
        time_str = time.toString("hh:mm AP")
        
        # Get ayanamsa and house system info
        ayanamsa = self.cboAyana.currentText()
        house_sys = self.cboHouseSys.currentText()
        
        text = f"<h2>{name}</h2>"
        text += f"<p><b>မွေးနေ့:</b> {date_str}<br>"
        text += f"<b>မွေးချိန်:</b> {time_str}<br>"
        text += f"<b>တည်နေရာ:</b> {lat:.4f}°N, {lon:.4f}°E<br>"
        text += f"<b>အချိန်ဇုံ:</b> {self.cboTimezone.currentText()}<br>"
        text += f"<b>အာယန:</b> {ayanamsa}<br>"
        text += f"<b>ဘာဝစနစ်:</b> {house_sys}</p>"
        
        text += "<h3>ဂြိုဟ်တည်နေရာများ (Rasi D1)</h3>"
        text += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
        text += "<tr><th>ဂြိုဟ်</th><th>ရာသီ</th><th>ဒီဂရီ</th><th>အိမ်</th></tr>"
        
        # Sort planets by house for better display
        sorted_results = sorted(results, key=lambda x: x.get('house', 0))
        
        for r in sorted_results:
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
            house = r.get('house', '?')
            
            text += f"<tr><td>{display_name}</td><td>{sign_name}</td><td>{r['deg']}°{r['min']}'{retro_str}</td><td>{house}</td></tr>"
        
        text += "</table>"
        
        # Add current chart selection info
        text += f"<p><i>လက်ရှိပြသထားသော ဇာတာ: {self.cboCheckable.currentText()}</i></p>"
        
        self.sidebar_text.setHtml(text)

    # ==================================================== #
    # ============= FILE OPERATIONS ====================== #
    # ==================================================== #

    def new_chart(self):
        """Clear all data for new chart"""
        reply = QMessageBox.question(self, "ဇာတာအသစ်", 
                                    "လက်ရှိဒေတာများ ပျက်သွားပါမည်။ ဆက်လုပ်မည်မှာ သေချာပါသလား?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.txtName.clear()
            self.cboDate.setDate(QDate.currentDate())
            self.cboTime.setTime(QTime.currentTime())
            
            # Clear all chart widgets
            self.rasi_chart_widget.set_planet_data([], True, "D1 - Rāśi")
            self.bhava_chart_widget.set_planet_data([], False, "Bhava - ဘာဝ")
            self.navamsa_chart_widget.set_planet_data([], False, "D9 - Navāṁśa")
            self.d2_chart_widget.set_planet_data([], True, "D2 - Hora")
            self.d7_chart_widget.set_planet_data([], True, "D7 - Saptāṁśa")
            self.d10_chart_widget.set_planet_data([], True, "D10 - Daśāṁśa")
            self.d12_chart_widget.set_planet_data([], True, "D12 - Dvādashāṁśa")
            self.d20_chart_widget.set_planet_data([], True, "D20 - Vimshāṁśa")
            self.d30_chart_widget.set_planet_data([], True, "D30 - Trimshāṁśa")
            self.d60_chart_widget.set_planet_data([], True, "D60 - Shashtyāṁśa")
            
            self.sidebar_text.clear()
            self.statusbar.showMessage("ဇာတာအသစ်အတွက် အဆင်သင့်ဖြစ်ပါပြီ")

    def save_chart(self):
        """Save current chart data to zartardata.brn file"""
        if not self.txtName.text():
            QMessageBox.warning(self, "သတိပေးချက်", 
                            "ဇာတာမရှိပါ။ ဦးစွာ ဇာတာတွက်ချက်ပါ။")
            return
        
        # Get current chart data
        name = self.txtName.text().strip()
        birth_date = self.cboDate.date()
        birth_time = self.cboTime.time()
        timezone = self.cboTimezone.currentText()
        tz_offset = self.cboTimezone.currentData()
        state = self.cboState.currentText()
        city = self.cboCity.currentText()
        lat = self.txtLat.text().strip()
        lon = self.txtLon.text().strip()
        ayanamsa = self.cboAyana.currentText()
        house_sys = self.cboHouseSys.currentText()
        
        # Format date and time
        date_str = birth_date.toString("dd.MM.yyyy")
        time_str = birth_time.toString("hh:mm")
        
        # Create data line
        # ဥပမာ: အေးမင်းမင်းဗိုလ်, 16.6.1974, 21:56, UTC+6:30, ရှမ်း (မြောက်), ကျောက်မဲ, 22.54172, 97.03671, Lahiri, Vehlow Equal
        data_line = f"{name}, {date_str}, {time_str}, {timezone}, {state}, {city}, {lat}, {lon}, {ayanamsa}, {house_sys}\n"
        
        # Get program directory
        program_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(program_dir, "zartardata.brn")
        
        try:
            # Append to file (line by line)
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(data_line)
            
            self.statusbar.showMessage(f"'{name}' ၏ ဇာတာအချက်အလက်များကို သိမ်းဆည်းပြီးပါပြီ")
            
        except Exception as e:
            QMessageBox.critical(self, "သိမ်းဆည်းမှု အမှား", 
                            f"ဖိုင်သိမ်းဆည်းရာတွင် အမှားရှိနေပါသည်:\n{str(e)}")

    def save_calculated_data(self):
        """Save calculated chart data (planetary positions) to file"""
        if not hasattr(self, 'rasi_chart_widget') or not self.rasi_chart_widget.planet_data:
            QMessageBox.warning(self, "သတိပေးချက်", 
                            "တွက်ချက်ထားသော ဇာတာဒေတာမရှိပါ။")
            return
        
        name = self.txtName.text().strip()
        if not name:
            name = "Unknown"
        
        # Get program directory
        program_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(program_dir, "zartardata.brn")
        
        try:
            # First, check if file exists and read all lines
            existing_lines = []
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_lines = f.readlines()
            
            # Prepare calculated data line
            calc_line = f"\n# Calculated data for {name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Add planetary positions
            for planet in self.rasi_chart_widget.planet_data:
                if planet['id'] == 'Lagna':
                    p_name = "Lagna"
                elif planet['id'] == 'Rahu':
                    p_name = "Rahu"
                elif planet['id'] == 'Ketu':
                    p_name = "Ketu"
                else:
                    p_name = str(planet['id'])
                
                sign_name = ZODIAC_SIGNS_MM[planet['sign']]
                retro = " R" if planet.get('retro', False) else ""
                calc_line += f"{p_name}: {sign_name} {planet['deg']}°{planet['min']}'{retro}, House: {planet.get('house', '?')}\n"
            
            calc_line += "# End of calculated data\n\n"
            
            # Write back all lines plus new calculated data
            with open(file_path, "w", encoding="utf-8") as f:
                # Write existing lines
                for line in existing_lines:
                    f.write(line)
                # Write new calculated data
                f.write(calc_line)
            
            self.statusbar.showMessage(f"'{name}' ၏ တွက်ချက်ထားသောဒေတာကို သိမ်းဆည်းပြီးပါပြီ")
            
        except Exception as e:
            QMessageBox.critical(self, "သိမ်းဆည်းမှု အမှား", 
                            f"ဒေတာသိမ်းဆည်းရာတွင် အမှားရှိနေပါသည်:\n{str(e)}")

    def open_chart(self):
        """Open and load chart data from zartardata.brn file"""
        program_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(program_dir, "zartardata.brn")
        
        if not os.path.exists(file_path):
            QMessageBox.information(self, "သတင်းအချက်အလက်", 
                                "zartardata.brn ဖိုင်မတွေ့ပါ။ ဦးစွာ ဇာတာသိမ်းဆည်းပါ။")
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Filter out comment lines and empty lines
            data_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
            
            if not data_lines:
                QMessageBox.information(self, "သတင်းအချက်အလက်", 
                                    "ဇာတာဒေတာမရှိပါ။")
                return
            
            # Show list of available charts
            chart_list = []
            for i, line in enumerate(data_lines):
                parts = line.split(',')
                if len(parts) >= 1:
                    chart_list.append(f"{i+1}. {parts[0].strip()}")
            
            if not chart_list:
                return
            
            # Simple selection dialog (you can create a proper dialog later)
            from PyQt5.QtWidgets import QInputDialog
            
            item, ok = QInputDialog.getItem(self, "ဇာတာရွေးချယ်ရန်", 
                                        "ဖွင့်လိုသောဇာတာကိုရွေးပါ:", 
                                        chart_list, 0, False)
            
            if ok and item:
                # Get index from selected item
                index = int(item.split('.')[0]) - 1
                selected_line = data_lines[index]
                self.load_chart_from_line(selected_line)
                
        except Exception as e:
            QMessageBox.critical(self, "ဖိုင်ဖွင့်မှု အမှား", 
                            f"ဖိုင်ဖွင့်ရာတွင် အမှားရှိနေပါသည်:\n{str(e)}")

    def load_chart_from_line(self, line):
        """Load chart data from a line of text"""
        try:  # Added try block
            parts = [p.strip() for p in line.split(',')]
            
            if len(parts) >= 10:
                name = parts[0]
                date_str = parts[1]
                time_str = parts[2]
                timezone = parts[3]
                state = parts[4]
                city = parts[5]
                lat = parts[6]
                lon = parts[7]
                ayanamsa = parts[8]
                house_sys = parts[9]
                
                # Set values to UI
                self.txtName.setText(name)
                
                # Parse date
                try:
                    day, month, year = map(int, date_str.split('.'))
                    date = QDate(year, month, day)
                    self.cboDate.setDate(date)
                except:
                    pass
                
                # Parse time
                try:
                    hour, minute = map(int, time_str.split(':'))
                    time = QTime(hour, minute)
                    self.cboTime.setTime(time)
                except:
                    pass
                
                # Set timezone
                for i in range(self.cboTimezone.count()):
                    if self.cboTimezone.itemText(i) == timezone:
                        self.cboTimezone.setCurrentIndex(i)
                        break
                
                # Set state and city
                state_index = self.cboState.findText(state)
                if state_index >= 0:
                    self.cboState.setCurrentIndex(state_index)
                    # Wait for state changed signal to populate cities
                    QApplication.processEvents()
                    
                    city_index = self.cboCity.findText(city)
                    if city_index >= 0:
                        self.cboCity.setCurrentIndex(city_index)
                
                # Set lat/lon
                self.txtLat.setText(lat)
                self.txtLon.setText(lon)
                
                # Set ayanamsa
                aya_index = self.cboAyana.findText(ayanamsa)
                if aya_index >= 0:
                    self.cboAyana.setCurrentIndex(aya_index)
                
                # Set house system
                house_index = self.cboHouseSys.findText(house_sys)
                if house_index >= 0:
                    self.cboHouseSys.setCurrentIndex(house_index)
                
                self.statusbar.showMessage(f"'{name}' ၏ ဇာတာအချက်အလက်များကို ဖွင့်ပြီးပါပြီ")
                
                # Optional: Auto-calculate after loading
                reply = QMessageBox.question(self, "ဇာတာတွက်ချက်ရန်", 
                                            "ဇာတာကိုအလိုအလျောက် တွက်ချက်မည်လား?",
                                            QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.calculate_chart()
        except Exception as e:  # Added matching except block
            print(f"Error loading chart from line: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set default font
    font = QFont("Pyidaungsu")
    font.setPointSize(10)
    app.setFont(font)

    window = BharaniApp()
    window.showMaximized()
    sys.exit(app.exec_())