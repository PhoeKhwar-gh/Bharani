
import sys
import os
import csv
import math
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List

from narayana_dasha import NarayanaDashaCalculator
from narayana_dasha_widget import NarayanaDashaWidget
from yuga_calculator import YugaCalculator
from myanmar_calendar import ceMmDateTime, ceMmTranslate


from ashtakavarga import AshtakavargaCalculator
from ashtakavarga_widget import AshtakavargaMatrixWidget



# PyQt5 imports



from PyQt5 import QtWidgets

from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QFrame,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QDateEdit, QTimeEdit, QCheckBox, QTextEdit,
    QScrollArea, QMessageBox, QInputDialog,
    QFileDialog, QDockWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy, QSpacerItem,
    QListWidget, QListWidgetItem,QDialog, QAction)

from PyQt5.QtPrintSupport import (QPrinter, QPrintDialog)

from PyQt5.QtCore import (Qt, QDate, QTime, QDateTime, pyqtSignal,
    QPointF, QRectF, QTimer, QCoreApplication)
from PyQt5.QtGui import (QFont, QColor, QPen, QBrush, QPainter,
    QPixmap, QIcon, QTextCursor)
import PyQt5.QtCore as QtCore

# Fortune Chart  import
# fortune_chart_widget import (Matplotlib မပါတော့)
try:
    from fortune_chart_widget import FortuneChartWidget
    FORTUNE_CHART_AVAILABLE = True
except ImportError:
    FortuneChartWidget = None
    FORTUNE_CHART_AVAILABLE = False
    
# Kawzar chart navigation imports
try:
    from kawzar_widget import KawzarWidget
    KAWZAR_MODULE_AVAILABLE = True
    print("✅ Kawzar module loaded successfully")
except ImportError as e:
    KawzarWidget = None
    KAWZAR_MODULE_AVAILABLE = False
    print(f"⚠️ Warning: kawzar_widget module not found: {e}")

# Import Strength Widgets
try:
    from strength_widget import (PlanetStrengthChartWidget, KarakaTableWidget,
        calculate_planet_strengths, get_planet_strengths_for_chart,
        calculate_karakas)
    STRENGTH_MODULE_AVAILABLE = True
    print("✅ Strength module loaded successfully")
except ImportError as e:
    PlanetStrengthChartWidget = None
    KarakaTableWidget = None
    calculate_planet_strengths = None
    get_planet_strengths_for_chart = None
    calculate_karakas = None
    STRENGTH_MODULE_AVAILABLE = False
    print(f"⚠️ Warning: strength_widget module not found: {e}")
    print(f"\n=== Debug Info ===")
    
    

# Import Shad Bala Widgets
try:
    from shad_bala_widget import ShadBalaCalculator, ShadBalaTableWidget, BhavaBalaCalculator, BhavaBalaWidget
    SHAD_BALA_AVAILABLE = True
except ImportError as e:
    ShadBalaCalculator = None
    ShadBalaTableWidget = None
    BhavaBalaCalculator = None
    BhavaBalaWidget = None
    SHAD_BALA_AVAILABLE = False
    print(f"⚠️ Warning: shad_bala_widget module not found: {e}")

from chart_widget import BurmeseChartWidget, ZODIAC_SIGNS_MM
from Ui_mainApp import Ui_MainWindow
from planet_info_widget import PlanetInfoTableWidget  # 👈 
import swisseph as swe

# file paths ပြုပြင်ခြင်း
import shutil


def resource_path(*relative_paths):
    if getattr(sys, 'frozen', False):
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *relative_paths)


def app_data_dir():
    if getattr(sys, 'frozen', False):
        base = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'BharaniApp'
        )
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(base, exist_ok=True)
    return base


def app_data_path(*relative_paths):
    return os.path.join(app_data_dir(), *relative_paths)


def writable_data_path(file_name):
    user_file = app_data_path(file_name)

    if not os.path.exists(user_file):
        default_file = resource_path(file_name)
        if os.path.exists(default_file):
            try:
                shutil.copy2(default_file, user_file)
            except Exception as e:
                print(f"Cannot copy default data file: {e}")

    return user_file

# === Constants ===
PLANET_IDS = [
    swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER,
    swe.VENUS, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO
]


planet_symbols_mm = {
    'Sun': '၁', 'Moon': '၂', 'Mars': '၃', 'Mercury': '၄',
    'Jupiter': '၅', 'Venus': '၆', 'Saturn': '၀',
    'Rahu': '၈', 'Ketu': '၉', 'Lagna': 'လ',
    'Uranus': 'U', 'Neptune': 'N', 'Pluto': 'P'
}

PLANET_SYMBOLS = {
        swe.SUN: '၁', 
        swe.MOON: '၂', 
        swe.MARS: '၃', 
        swe.MERCURY: '၄',
        swe.JUPITER: '၅', 
        swe.VENUS: '၆', 
        swe.SATURN: '၀',
        swe.URANUS: 'U', 
        swe.NEPTUNE: 'N', 
        swe.PLUTO: 'P',
        'Lagna': 'လ', 
        'Rahu': '၈', 
        'Ketu': '၉'
}

ZODIAC_SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

MOVABLE_SIGNS = [1, 4, 7, 10]
FIXED_SIGNS = [2, 5, 8, 11]
DUAL_SIGNS = [3, 6, 9, 12]
ODD_SIGNS = [1, 3, 5, 7, 9, 11]
EVEN_SIGNS = [2, 4, 6, 8, 10, 12]




class BharaniApp(QMainWindow, Ui_MainWindow):
    
    # File path for storing all charts
    CHARTS_FILE = app_data_path("ZartarData.brn")
    
    
    def __init__(self):
        super().__init__()
        # === Set up the UI ===
        self.setupUi(self)
        
        # Narayana - dasa widget ကို Tab_3 တွင် ထည့်သွင်းခြင်း
        self.init_narayana_dasha()
        
        
        # Tabify the right side docks
        self.planet_info_widget = PlanetInfoTableWidget()
        self.docPlanetsInfo.setWidget(self.planet_info_widget)  # Dock Widget အတွင်း အစားထိုးထည့်သွင်း
        
        self.init_ui()
        
        # === Dock Widget Tabify & Stability Settings ===============================
        self.setDockOptions(self.AllowTabbedDocks | self.AllowNestedDocks)
        
        
        
        self.tabifyDockWidget(self.docPlanetsInfo, self.docStrength)
        self.tabifyDockWidget(self.docStrength, self.docRemark)
        
        # Set Default Visibility
        self.docPlanetsInfo.show()
        self.docStrength.hide()
        self.docRemark.hide()
        
        # === Initialize UI ===================================================================
        
        # === Set Swisseph Path ===
        ephe_path = resource_path ('ephe')
        swe.set_ephe_path(ephe_path)

        # Initialize variables
        self.location_data = defaultdict(lambda: defaultdict(list))
        self.custom_locations = []
        self.current_houses_cusps = None
        self.chart_widgets = {}
        self.karaka_table = None
        self.strength_chart = None
        self.current_planet_data = None
        self.current_ascendant = None
        
        # Set default date and time
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        
        # Latitude/Longitude fields - initially read-only
        self.txtLat.setReadOnly(True)
        self.txtLon.setReadOnly(True)
        
        # === Load CSV Data ===
        self.load_location_data()
        
        # === Populate Timezone ===
        self.populate_timezone_combo()
        
        # === Populate Step Combo ===
        self.populate_kawzar_step_combo()
        
        # === Setup Chart Display ===
        self.setup_display_widgets()
        
        # === Ashtakavarga Tab Setup ===
        self.init_ashtakavarga_tab()
        
        # === Initialize Dasa Table ===
        self.init_dasa_table()

        # === Connect Signals ===
        self.setup_connections()
        
        
        
        # === Kawzar Widget Setup ===
        self.setup_kawzar_widget()
        
        # ===== Fortune chart ======
        # === Fortune Chart Setup in Remark Dock ===
        if FORTUNE_CHART_AVAILABLE:
            # Create the Fortune Chart Widget
            self.fortune_chart_widget = FortuneChartWidget(self)
            
            # Set it as the content of docRemark Dock Widget
            self.docRemark.setWidget(self.fortune_chart_widget)
            
            # Optionally set a title for the Dock
            self.docRemark.setWindowTitle("📊 ကံကြမ္မာ အနိမ့်အမြင့် ဇယား")

        # Initialize division charts visibility based on checkbox
        self.chkDivision.setChecked(False)
        
        # Dock Widget များကို ညာဖက်ခြမ်းတွင်သာ ရှိစေရန် သတ်မှတ်ခြင်း
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.docPlanetsInfo)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.docStrength)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.docRemark)
        # Kawzar ကိုမူ Floating ထားလိုပါက သီးသန့်ထားနိုင်သည်
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.docKawzar)
        
        # ✅ အောက်ပါ Code ကို ထည့်ပေးလိုက်ပါ
        if hasattr(self, 'tabWidget'):
            self.tabWidget.setCurrentIndex(0)  # 0 သည် ပထမဆုံး Tab (Tab_1) ဖြစ်သည်
        
        #pdf export munu create
        self._export_pdf_menu()
    # ==================== INITIALIZATION METHODS ====================

    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("ဘရဏီ")
        
        # Style Sheet (keep existing)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f3f4;
            }
            QFrame#frame {
                background-color: #ebf5fa;
                border-right: 1px solid #dee2e6;
            }
            QLabel {
                color: #2c3e50;
                font-size: 11pt;
                padding: 2px;
            }
            QLineEdit, QComboBox, QDateEdit, QTimeEdit {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 10pt;
                min-height: 22px;
                selection-background-color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        
        self.frame.setMinimumWidth(400)
        self.frame.setMaximumWidth(400)
        
        # Set margins and spacing for the left frame layout
        self.verticalLayout_6.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_6.setSpacing(8)
        
        # Set minimum widths for labels (using existing labels)
        for lbl in [self.lblName, self.lblDate, self.lblTime, self.lblTimeZone]:
            lbl.setMinimumWidth(180)
        
        # Header fonts
        font = QFont("Pyidaungsu", 15, QFont.Bold)
        self.label_4.setFont(font)   # "ဇာတာ အသစ်"
        self.label_4.setMaximumWidth(16777215)
        self.label_4.setMinimumWidth(100)  # အနည်းဆုံး 100
        
        font = QFont("Pyidaungsu", 13, QFont.Bold)
        self.label_8.setFont(font)   # "မွေး ဒေသ"
        self.label_15.setFont(font)  # "အောက်ပါ စနစ်များ အသုံးပြုပါမည်"
        
        # Calculate button
        self.btnCalculate.setMinimumHeight(40)
        font = QFont("Pyidaungsu", 14, QFont.Bold)
        self.btnCalculate.setFont(font)
        
        # Combo box heights
        for combo in [self.cboDate, self.cboTime, self.cboTimezone, self.cboState,
                    self.cboCity, self.cboAyana, self.cboHouseSys, self.cboCountry]:
            combo.setMinimumHeight(28)
        
        # Text input heights
        self.txtName.setMinimumHeight(28)
        self.txtLat.setMinimumHeight(28)
        self.txtLon.setMinimumHeight(28)
        
        # Edit place button
        self.btnEditPlace.setMinimumHeight(28)
        self.btnEditPlace.setMinimumWidth(60)
        
        # Ayanamsa list (if empty)
        if self.cboAyana.count() == 0:
            ayanamsa_list = [
                "Lahiri", "Krishnamurti", "Raman", "Fagan/Bradley",
                "Yukteshwar", "J2000", "Suryasiddhanta",
                "True Citra / True Revati", "Galactic Center / Dhruva"
            ]
            self.cboAyana.clear()
            self.cboAyana.addItems(ayanamsa_list)
        
        # House systems (if empty)
        if self.cboHouseSys.count() == 0:
            house_systems = ["Whole Sign", "Vehlow Equal", "Equal", "Placidus", "Sripati", "Porphyry"]
            self.cboHouseSys.clear()
            self.cboHouseSys.addItems(house_systems)
            self.cboHouseSys.setCurrentText("Vehlow Equal")
        
        # Use the existing cboKawzarPlace (labeled "ကောဇာဒေသ") as the main city combo
        self.cboAllCities = self.cboKawzarPlace
        self.cboAllCities.setEditable(False)
        self.cboAllCities.setMinimumHeight(28)
        
        self.cboAllCities.setMinimumWidth(150)
        self.cboAllCities.setMaximumWidth(200)
        
        # cboKawzarStep (step combo for Kawzar navigation)
        self.cboKawzarStep = QComboBox(self.dockWidgetContents_6)
        self.cboKawzarStep.setMinimumHeight(28)
        # We'll add it to the Kawzar dock layout
        # The dock has a horizontal layout with pushButton_5, cboTimeSwitch_2, pushButton_6
        # We'll replace cboTimeSwitch_2 with cboKawzarStep or add a new combo?
        # The UI has cboTimeSwitch_2, we can rename it or use it.
        # Let's simply rename cboTimeSwitch_2 to cboKawzarStep and use it.
        # But it's already created by UI. So we can just assign:
        self.cboKawzarStep = self.cboTimeSwitch_2
        self.cboKawzarStep.clear()
        
        # Kawzar buttons: use existing pushButton_5 and pushButton_6
        self.btnKawzarPrev = self.pushButton_5
        self.btnKawzarNext = self.pushButton_6
        
    #Widget ပေါ်မယ် ပျောက်မယ်
    def closeEvent(self, event):
        # App ပိတ်တဲ့အခါ Layout အခြေအနေကို သိမ်းဆည်းခြင်း
        settings = QtCore.QSettings("MyCompany", "BharaniApp")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())
        event.accept()
        
        
    def open_place_editor(self):
        """Open place editor as child dialog"""

        # ✅ Dialog ဖွင့်ပြီးသားဆိုရင် ထပ်မဖွင့်ဘဲ ပြန်နေမယ်
        if getattr(self, "_place_editor_open", False):
            return

        self._place_editor_open = True

        try:
            from place_edit import AstroLocatorApp

            self._pending_saved_town = ""

            dlg = AstroLocatorApp(self)
            dlg.location_saved.connect(self.on_place_saved)

            result = dlg.exec_()

            if result == QtWidgets.QDialog.Accepted:
                self.load_location_data()

                if getattr(self, "_pending_saved_town", ""):
                    index = self.cboAllCities.findText(
                        self._pending_saved_town,
                        QtCore.Qt.MatchFixedString
                    )
                    if index >= 0:
                        self.cboAllCities.setCurrentIndex(index)
                        self.on_all_cities_changed(index)

                self.statusbar.showMessage("✅ နေရာအသစ် သိမ်းဆည်းပြီးပါပြီ")

        except ImportError as e:
            QtWidgets.QMessageBox.critical(
                self, "အမှား",
                f"place_edit.py ကို မတွေ့ရှိပါ:\n{str(e)}"
            )

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "အမှား",
                f"နေရာအယ်ဒီတာ ဖွင့်ရာတွင် အမှား:\n{str(e)}"
            )
            import traceback
            traceback.print_exc()

        finally:
            self._place_editor_open = False


    def restore_settings(self):
        # App ဖွင့်တဲ့အခါ Layout အခြေအနေကို ပြန်ယူခြင်း
        settings = QtCore.QSettings("MyCompany", "BharaniApp")
        if settings.value("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        if settings.value("state"):
            self.restoreState(settings.value("state"))
        
    def get_charts_dir(self):
        """Get or create the charts directory"""
        charts_dir = os.path.join(os.path.dirname(__file__), "charts")
        os.makedirs(charts_dir, exist_ok=True)
        return charts_dir


    #Ashtakavarga calculate parts
    def init_ashtakavarga_tab(self):
        """အဋ္ဌဝဂ္ဂ (Ashtakavarga) Tab ကို စတင်ထည့်သွင်းခြင်း"""
        try:
            # tabWidget ရှိမရှိ စစ်ဆေးပါ
            if not hasattr(self, 'tabWidget'):
                print("⚠️ tabWidget not found")
                return
                
            # အဋ္ဌဝဂ္ဂ Tab အသစ်ဖန်တီးခြင်း
            self.tab_ashtakavarga = QWidget()
            self.tab_ashtakavarga.setObjectName("tab_ashtakavarga")
            
            # Layout setup
            from PyQt5.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self.tab_ashtakavarga)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)
            
            # Header Label
            header = QLabel("🔮 အဋ္ဌဝဂ္ဂ (Ashtakavarga) ဇယားများ")
            header.setFont(QFont("Pyidaungsu", 14, QFont.Bold))
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("color: #2c3e50; padding: 10px;")
            layout.addWidget(header)
            
            # Info Label
            info = QLabel("ဂြိုဟ် ၇ လုံး၏ ဗိန္ဒုအမှတ်များနှင့် စုစုပေါင်း (SAV) ကို ပြသထားသည်။(ပရာသရ, ဝရဟာမိဟိရ ဆရာတို့အလို Whole Sign ဘာဝစနစ် သုံးသည်)")
            info.setFont(QFont("Pyidaungsu", 10))
            info.setAlignment(Qt.AlignCenter)
            info.setStyleSheet("color: #7f8c8d;")
            layout.addWidget(info)
            
            # Ashtakavarga Matrix Widget ထည့်သွင်းခြင်း
            self.ashta_matrix = AshtakavargaMatrixWidget()
            self.ashta_matrix.setMinimumSize(600, 600)
            layout.addWidget(self.ashta_matrix)
            
            # Tab ကို tabWidget သို့ ထည့်ခြင်း (ဇာတာပုံ tab ပြီးနောက်)
            # Tab_1 = Chart, Tab_2 = Dasa, Tab_3 = Narayana
            # We insert at index 3 (after existing tabs)
            self.tabWidget.addTab(self.tab_ashtakavarga, "အဋ္ဌဝဂ္ဂ")
            
            print("✅ Ashtakavarga tab initialized successfully")
            
        except Exception as e:
            print(f"⚠️ Error initializing Ashtakavarga tab: {e}")
            import traceback
            traceback.print_exc()
    
    # နာရာယဏ ဒသာကို ဖော်ပြတွက်ချက်ပါမည်
    
    def init_narayana_dasha(self):
        """tab_3 တွင် Narayana Dasha Widget ကို စတင်ထည့်သွင်းခြင်း"""
        try:
            from narayana_dasha_widget import NarayanaDashaWidget
            
            # tab_3 ၏ Layout ရှင်းလင်းခြင်း
            if self.tab_3.layout():
                old_layout = self.tab_3.layout()
                while old_layout.count():
                    child = old_layout.takeAt(0)
                    if child and child.widget():
                        child.widget().deleteLater()
            else:
                from PyQt5.QtWidgets import QVBoxLayout
                QVBoxLayout(self.tab_3)

            # Widget ဖန်တီးပြီး tab_3 ထဲသို့ ထည့်ခြင်း
            self.narayana_widget = NarayanaDashaWidget()
            self.tab_3.layout().addWidget(self.narayana_widget)
            print("✅ Narayana Dasha widget initialized in tab_3")
            
        except Exception as e:
            print(f"⚠️ Error initializing Narayana Dasha: {e}")
            import traceback
            traceback.print_exc()

    
        

    def setup_kawzar_widget(self):  # sourcery skip: extract-method
        """Kawzar Widget ကို စတင်ထည့်သွင်းခြင်း"""
        try:
            if not KAWZAR_MODULE_AVAILABLE:
                print("⚠️ Kawzar module not available")
                return
            
            if hasattr(self, 'frmkawzar'):
                old_layout = self.frmkawzar.layout()
                if old_layout:
                    while old_layout.count():
                        child = old_layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()
                else:
                    old_layout = QVBoxLayout(self.frmkawzar)
    #-----------------------------------------------------------------------
                old_layout.setContentsMargins(0,0,0,0)
                old_layout.setSpacing(0)
    #-----------------------------------------------------------------------            
                self.kawzar_widget = KawzarWidget(self)
                
                self.frmkawzar.setStyleSheet(""" 
                QFrame{
                    background-color: transparent;
                    border:none
                }
            """)
                
                self.kawzar_widget.now_clicked.connect(self.update_kawzar_to_now)
                
                self.frmkawzar.setMinimumSize(QtCore.QSize(420, 520))
                self.frmkawzar.setMaximumSize(QtCore.QSize(420, 520))
                
                
                
                self.kawzar_widget.now_clicked.connect(self.update_kawzar_to_now)
                
                #self.kawzar_widget.setFixedSize(500, 500)
                
                
                old_layout.addWidget(self.kawzar_widget)
                old_layout.addStretch()
                
                self.update_kawzar_location()
                print("✅ Kawzar widget initialized")
            else:
                print("⚠️ frmkawzar not found in UI")
        except Exception as e:
            print(f"Error setting up Kawzar widget: {e}")
            import traceback
            traceback.print_exc()

    def update_kawzar_location(self):
        """ကောဇာအတွက် နေရာအချက်အလက် အပ်ဒိတ်လုပ်ခြင်း"""
        if not hasattr(self, 'kawzar_widget') or not KAWZAR_MODULE_AVAILABLE:
            return
        
        city_index = self.cboAllCities.currentIndex()
        if city_index >= 0:
            city_name = self.cboAllCities.currentText()
            location_data = self.cboAllCities.itemData(city_index)
            
            if location_data and len(location_data) >= 2:
                lat, lon = location_data[0], location_data[1]
                self.kawzar_widget.set_location(city_name, lat, lon)
                print(f"📍 Kawzar location updated: {city_name}")
                
     

    def update_kawzar_time(self):
        """ကောဇာအတွက် အချိန်အချက်အလက် အပ်ဒိတ်လုပ်ခြင်း"""
        if not hasattr(self, 'kawzar_widget') or not KAWZAR_MODULE_AVAILABLE:
            return
        
        birth_date = self.cboDate.date()
        birth_time = self.cboTime.time()
        qdatetime = QDateTime(birth_date, birth_time)
        self.kawzar_widget.set_datetime(qdatetime)
        print(f"🕐 Kawzar time updated: {birth_date.toString()} {birth_time.toString()}")
        

    # ယုဂ်တွက်ပုံ chrt %%%%%%%%%%%%%%%%%%%%%%%%%+_+_+_+_+__

    @staticmethod
    def format_myanmar_date(gregorian_date):
        """Format a Gregorian date as a Myanmar calendar date."""
        mm_date = ceMmDateTime.from_gregorian(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day,
            tz=6.5,
        )
        translator = ceMmTranslate()
        my_year = translator.T(str(mm_date.my), 1, 0)
        month_names = [
            "တန်ခူး", "ကဆုန်", "နယုန်", "ဝါဆို", "ဝါခေါင်", "တော်သလင်း",
            "သီတင်းကျွတ်", "တန်ဆောင်မုန်း", "နတ်တော်", "ပြာသို", "တပို့တွဲ", "တပေါင်း",
        ]
        if mm_date.mm == 4 and mm_date.myt > 0:
            month_name = "ဒုတိယ ဝါဆို"
        elif mm_date.mm == 13:
            month_name = "နှောင်းတန်ခူး"
        else:
            month_name = month_names[mm_date.mm - 1]

        moon_names = ["လဆန်း", "လပြည့်", "လဆုတ်", "လကွယ်"]
        moon_phase = moon_names[mm_date.mp]
        if mm_date.mp in (1, 3):
            moon_day = ""
        else:
            moon_day = f" {translator.T(str(mm_date.mf), 1, 0)} ရက်"
        weekdays = ["စနေ", "တနင်္ဂနွေ", "တနင်္လာ", "အင်္ဂါ", "ဗုဒ္ဓဟူး", "ကြာသပတေး", "သောကြာ"]
        return f"{my_year} ခုနှစ်၊ {month_name}{moon_phase}{moon_day}၊ {weekdays[mm_date.w]}နေ့"
    
    def update_sidebar_text(self, planet_data, name, birth_dt, lat, lon, jd): 
        """Update sidebar text with chart details + Yuga Info"""
        
        # 1. အခြေခံ အချက်အလက်များ
        text = f"<h3>{name}</h3>"
        text += f"<p>📅 မွေးနေ့: {birth_dt.strftime('%Y-%m-%d %H:%M')}</p>"
        text += f"<p>မြန်မာရက်စွဲ: {self.format_myanmar_date(birth_dt)}</p>"
        text += f"<p>📍 နေရာ: {self.cboAllCities.currentText()} ({lat:.4f}, {lon:.4f})</p>"
        
        # 2. ယုဂ် (Yuga) အချက်အလက် ထည့်သွင်းခြင်း 🌟
        yuga_html = YugaCalculator.get_yuga_html(jd)
        text += yuga_html
        
        # 3. ဂြိုဟ်တည်ရာများ
        text += "<h4>ဂြိုဟ်တည်ရာများ:</h4>"
        text += "<ul style='margin-top:5px; padding-left:20px;'>"
        for p in planet_data:
            sign_short = p['sign_name'][:3] 
            text += f"<li><b>{p['symbol']} {p['name']}:</b> {sign_short} {p['deg']}° {p['min']}'</li>"
        text += "</ul>"
        
        self.sidebar_text.setHtml(text)
#_+_+_+_+_+_+_+_+__+_+_+_+_+_+_+_+__+_+_+_+_+_+_+_+__+_+_+_+_+_+_+_+__+_+_+_+_+_+_+_+__+_+_+_+_+_+_+_+_

    def init_dasa_table(self):
        """Initialize Dasa table in the Dasa tab """
        try:
            from dasa_table import DasaTableWidget
            
            print("=" * 50)
            print("Initializing Dasa Table... ")

            # ✅ tab_2 တွင် Layout ရှိ/မရှိ စစ်ဆေးပြီး မရှိလျှင် အသစ်ဖန်တီး
            if self.tab_2.layout() is None:
                self.dasa_layout = QVBoxLayout(self.tab_2)
                self.dasa_layout.setAlignment(QtCore.Qt.AlignTop)
            else:
                self.dasa_layout = self.tab_2.layout()
                self.dasa_layout.setAlignment(QtCore.Qt.AlignTop)
                

            # Layout အဟောင်းထဲရှိ Widget များကို လုံခြုံစွာ ရှင်းလင်း
            while self.dasa_layout.count():
                child = self.dasa_layout.takeAt(0)
                if child and child.widget():
                    child.widget().deleteLater()

            self.dasa_layout.setContentsMargins(0, 0, 0, 0)
            self.dasa_layout.setSpacing(5)

            print("Creating DasaTableWidget... ")
            self.dasa_table = DasaTableWidget()
           
            self.dasa_table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.dasa_layout.addWidget(self.dasa_table)

            # ✅ Signal များ ထပ်နေခြင်းကို ကာကွယ်ရန် Disconnect လုပ်ခြင်း
            try:
                self.dasa_table.level_changed.disconnect(self.on_dasa_level_changed)
                self.dasa_table.period_selected.disconnect(self.on_dasa_period_selected)
            except:
                pass

            self.dasa_table.level_changed.connect(self.on_dasa_level_changed)
            self.dasa_table.period_selected.connect(self.on_dasa_period_selected)

            # ✅ Widget ကို ပေါ်လာစေရန် အတင်းဖွင့်ခြင်း & Layout Refresh
            self.dasa_table.setVisible(True)
            self.dasa_layout.update()
            self.tab_2.update()

            print("✅ Dasa table initialized successfully ")
            print("=" * 50)
            
        except ImportError as e:
            print(f"⚠️ Dasa table module not found: {e} ")
            self.dasa_table = None
        except Exception as e:
            print(f"❌ Error in init_dasa_table: {e} ")
            import traceback
            traceback.print_exc()
            self.dasa_table = None

    def calculate_and_show_strengths(self):
        """Calculate and display planetary strengths with embedded Chart"""
        try:
            if not STRENGTH_MODULE_AVAILABLE:
                QtWidgets.QMessageBox.warning(self, "Warning", "Strength module not available.")
                return
            
            if not hasattr(self, 'current_planet_data') or self.current_planet_data is None:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please calculate a chart first.")
                return
            
            shad_bala_data = []
            error_msg = ""
            
            try:
                from shad_bala_widget import ShadBalaCalculator
                calc = ShadBalaCalculator()
                birth_date = self.cboDate.date()
                birth_time = self.cboTime.time()
                birth_dt = datetime(birth_date.year(), birth_date.month(), birth_date.day(),
                                    birth_time.hour(), birth_time.minute(), birth_time.second())
                lat = float(self.txtLat.text()) if self.txtLat.text() else 0
                lon = float(self.txtLon.text()) if self.txtLon.text() else 0
                shad_bala_data = calc.calculate_shad_bala(self.current_planet_data, birth_dt, lat, lon)
                if not shad_bala_data: error_msg = "No Shad Bala data calculated."
            except Exception as e:
                error_msg = f"Calculation Error: {str(e)}"
                import traceback; traceback.print_exc()
            
            # Layout ရှင်းလင်းခြင်း
            layout = self.frm_strength_table.layout()
            if layout:
                while layout.count():
                    child = layout.takeAt(0)
                    if child and child.widget(): child.widget().deleteLater()
            else:
                layout = QtWidgets.QVBoxLayout(self.frm_strength_table)
                layout.setContentsMargins(5, 5, 5, 5)
                layout.setSpacing(10)
            
            # Tab Widget ဖန်တီးခြင်း
            tab_widget = QtWidgets.QTabWidget()
            tab_widget.setStyleSheet("""
                QTabWidget::pane { border: 1px solid #bdc3c7; border-radius: 5px; background-color: white; }
                QTabBar::tab { background-color: #ecf0f1; color: #2c3e50; padding: 10px 20px; margin-right: 2px; font-weight: bold; }
                QTabBar::tab:selected { background-color: #3498db; color: white; }
            """)
            
            # 1️⃣ Shad Bala Tab
            shad_tab = QtWidgets.QWidget()
            shad_layout = QtWidgets.QVBoxLayout(shad_tab)
            shad_layout.setContentsMargins(0,0,0,0)
            if error_msg:
                shad_layout.addWidget(QtWidgets.QLabel(f"❌ {error_msg}"))
            else:
                try:
                    from shad_bala_widget import ShadBalaTableWidget
                    table_widget = ShadBalaTableWidget()
                    scroll = QtWidgets.QScrollArea()
                    scroll.setWidgetResizable(True)
                    scroll.setWidget(table_widget)
                    table_widget.update_shad_bala(shad_bala_data)
                    shad_layout.addWidget(scroll)
                except Exception as e:
                    shad_layout.addWidget(QtWidgets.QLabel(f"Table Display Error: {str(e)}"))
            tab_widget.addTab(shad_tab, "📊 ဂြိုဟ်အားဗလ ၆ မျိုး & Chart")
            
            # 2️⃣ Bhava Bala Tab
            bhava_tab = QtWidgets.QWidget()
            bhava_layout = QtWidgets.QVBoxLayout(bhava_tab)
            bhava_layout.setContentsMargins(5,5,5,5)
            try:
                from shad_bala_widget import BhavaBalaCalculator, BhavaBalaWidget
                b_calc = BhavaBalaCalculator()
                asc_long = next((p.get('longitude', 0) for p in self.current_planet_data if p.get('id') == 'Lagna'), 0)
                b_data = b_calc.calculate_bhava_bala(self.current_planet_data, asc_long, self.current_houses_cusps)
                b_widget = BhavaBalaWidget()
                b_widget.update_bhava_bala(b_data)
                bhava_layout.addWidget(b_widget)
            except Exception as e:
                bhava_layout.addWidget(QtWidgets.QLabel(f"Bhava Bala Error: {str(e)}"))
            tab_widget.addTab(bhava_tab, "🏠 ဘာဝဗလ")
            
            # 3️⃣ Karaka Tab
            karaka_tab = QtWidgets.QWidget()
            karaka_layout = QtWidgets.QVBoxLayout(karaka_tab)
            karaka_layout.setContentsMargins(5,5,5,5)
            try:
                from strength_widget import calculate_karakas, KarakaTableWidget
                karakas = calculate_karakas(self.current_planet_data)
                self.karaka_table = KarakaTableWidget()
                self.karaka_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                self.karaka_table.setMinimumHeight(350)
                self.karaka_table.update_karakas(karakas)
                karaka_layout.addWidget(self.karaka_table)
            except Exception as e:
                karaka_layout.addWidget(QtWidgets.QLabel(f"Karaka Error: {str(e)}"))
            tab_widget.addTab(karaka_tab, "🌟 ကာရက ၇ ပါး")
            
            # 4️⃣ Combined Relations Tab
            try:
                from planet_relations_combined import CombinedRelationWidget
                combined_widget = CombinedRelationWidget()
                combined_widget.update_analysis(self.current_planet_data, self.current_houses_cusps)
                tab_widget.addTab(combined_widget, "🔗 ပေါင်းစပ်ခွဲခြမ်း")
                print("✅ Combined Relation Analysis loaded")
            except Exception as e:
                print(f"⚠️ Combined Relation Error: {e}")
                
            # 5️⃣ Naisargika Relations Tab
            rel_tab = QtWidgets.QWidget()
            rel_layout = QtWidgets.QVBoxLayout(rel_tab)
            rel_layout.setContentsMargins(5,5,5,5)
            rel_table = QtWidgets.QTableWidget()
            rel_table.setColumnCount(4)
            rel_table.setHorizontalHeaderLabels(["ဂြိုဟ်", "မိတ်ဖက် (Mitra)", "သင့်တင့် (Neutral)", "ရန်ဘက် (Shatru)"])
            rel_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            rel_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
            rel_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
            rel_table.setAlternatingRowColors(True)
            rel_table.setStyleSheet("""
                QTableWidget { font-size: 10pt; background-color: #ffffff; alternate-background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; }
                QHeaderView::section { background-color: #2c3e50; color: white; padding: 8px; border: 1px solid #bdc3c7; font-weight: bold; font-size: 10pt; }
            """)
            planet_relations = {
                'Sun': (['Moon','Mars','Jupiter'], ['Mercury'], ['Venus','Saturn']),
                'Moon': (['Sun','Mercury'], ['Mars','Jupiter','Venus','Saturn'], []),
                'Mars': (['Sun','Moon','Jupiter'], ['Saturn'], ['Mercury']),
                'Mercury':(['Sun','Venus'], ['Mars','Jupiter','Saturn'], ['Moon']),
                'Jupiter':(['Sun','Moon','Mars'], ['Saturn'], ['Mercury','Venus']),
                'Venus': (['Mercury','Saturn'], ['Mars','Jupiter'], ['Sun','Moon']),
                'Saturn': (['Mercury','Venus'], ['Jupiter'], ['Sun','Moon','Mars']),
                'Rahu': (['Mercury','Venus','Saturn'], ['Jupiter'], ['Sun','Moon','Mars']),
                'Ketu': (['Mars','Jupiter','Saturn'], ['Mercury'], ['Sun','Moon','Venus'])
            }
            rel_table.setRowCount(len(planet_relations))
            for row, (planet, (friends, neutrals, enemies)) in enumerate(planet_relations.items()):
                rel_table.setItem(row, 0, QtWidgets.QTableWidgetItem(planet))
                rel_table.setItem(row, 1, QtWidgets.QTableWidgetItem(', '.join(friends) if friends else '-'))
                rel_table.setItem(row, 2, QtWidgets.QTableWidgetItem(', '.join(neutrals) if neutrals else '-'))
                rel_table.setItem(row, 3, QtWidgets.QTableWidgetItem(', '.join(enemies) if enemies else '-'))
                for col in range(4): rel_table.item(row, col).setTextAlignment(Qt.AlignCenter)
            rel_layout.addWidget(rel_table)
            tab_widget.addTab(rel_tab, "🤝 ဂြိုဟ်ဆက်နွယ်မှု")
            
            # ✅ Tab အားလုံးပြီးမှ Layout သို့ ထည့်ခြင်း
            layout.addWidget(tab_widget)
            self.docStrength.show()
            self.statusbar.showMessage("ဂြိုဟ်အားဗလ, ဘာဝဗလ, ကာရကနှင့် ဆက်နွယ်မှုများ တွက်ချက်ပြီးပါပြီ")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            import traceback; traceback.print_exc()

    # ==================== HELPER METHODS ====================
    
    #Column line chart ရေးဆွဲခြင်းပါ
    
    def show_fortune_chart(self):
        """ ကံကြမ္မာ အနိမ့်အမြင့် ဇယား ဖွင့်ခြင်း """
        try:
            # Widget အသစ်ဖွင့်မည်
            self.fortune_window = FortuneChartWidget(self)
            
            # ွင့်လိုက်သော Widget ကို ပြင်ဆင်ခြင်း (Optional)
            self.fortune_window.setWindowTitle("ကံကြမ္မာ အနိမ့်အမြင့် ဇယား")
            self.fortune_window.resize(900, 600)
            
            # မွေးသက္ကရာ် ရှိ/မရှိ စစ်ဆေးခြင်း
            if self.current_planet_data is None:
                QMessageBox.warning(self, "သတိပေးချက်", "းစွာ ဇာတာကို တွက်ချက်ပေးပါ။")
                return
                
            self.fortune_window.show()
            
        except Exception as e:
            QMessageBox.critical(self, "အမှား", f"ယားဖွင့်ရာတွင် အမှား-\n{str(e)}")

    # ==================== DOCK WIDGET TOGGLE HELPERS ====================
    def toggle_dock_visibility(self, dock_widget, action):
        """Menu Action နှိပ်လိုက်သည့်အခါ Dock Widget ကို ပေါ်/ပျောက် လုပ်ပေးမည့် Function"""
        if action.isChecked():
            dock_widget.show()
            dock_widget.raise_()  # Bring to front
        else:
            dock_widget.hide()

    def sync_action_state(self, dock_widget, action):
        """Dock Widget ကို X နှိပ်ပိတ်လိုက်သည့်အခါ Menu Action မှ အမှန်ခြစ် ပျက်စေရန် Function"""
        # Visibility ပြောင်းလဲမှုကို Action သို့ ပြန်လည် အပ်ဒိတ်လုပ်ခြင်း
        # blockSignals ကို သုံးပြီး Loop မဖြစ်အောင် ကာကွယ်ခြင်း
        action.blockSignals(True)
        action.setChecked(dock_widget.isVisible())
        action.blockSignals(False)
        
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
        
        for i in range(self.cboTimezone.count()):
            if self.cboTimezone.itemData(i) == 6.5:
                self.cboTimezone.setCurrentIndex(i)
                break

    def populate_kawzar_step_combo(self):
        """Populate step combo for Kawzar chart navigation"""
        steps = ["Sec", "Min", "Hour", "Day", "Month", "Year"]
        tooltips = ["စက္ကန့်", "မိနစ်", "နာရီ", "ရက်", "လ", "နှစ်"]
        
        self.cboKawzarStep.clear()
        for i, step in enumerate(steps):
            self.cboKawzarStep.addItem(step)
            if i < len(tooltips):
                self.cboKawzarStep.setItemData(i, tooltips[i], Qt.ToolTipRole)
        
        self.cboKawzarStep.setCurrentText("Sec")

    def load_location_data(self):
        """Load location data from CSV file using column indices."""
        csv_path = writable_data_path("dataCSV.csv")
        
        try:
            self.location_data = defaultdict(lambda: defaultdict(list))
            
            with open(csv_path, encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                # Skip header (we'll use fixed column indices)
                header = next(reader)
                # Column indices based on your CSV structure
                # 0: Country, 1: SRName, 2: TownName, 3: Latitude, 4: Longitude, 5: timezone
                idx_country = 0
                idx_sr = 1
                idx_town = 2
                idx_lat = 3
                idx_lon = 4
                
                for row in reader:
                    if len(row) < 5:
                        continue
                    country = row[idx_country].strip()
                    sr = row[idx_sr].strip()
                    town = row[idx_town].strip()
                    lat = row[idx_lat].strip()
                    lon = row[idx_lon].strip()
                    
                    if not town or not lat or not lon:
                        continue
                    
                    self.location_data[country][sr].append((town, lat, lon))
            
            # Sort towns within each state
            for country in self.location_data:
                for state in self.location_data[country]:
                    self.location_data[country][state].sort(key=lambda x: x[0])
            
            # Populate Country ComboBox
            countries = sorted(self.location_data.keys())
            self.cboCountry.clear()
            self.cboCountry.addItem("-- ရွေးပါ --")
            self.cboCountry.addItems(countries)
            
            if countries:
                if "မြန်မာ" in countries:
                    self.cboCountry.setCurrentText("မြန်မာ")
                else:
                    self.cboCountry.setCurrentIndex(1)
                self.on_country_changed(self.cboCountry.currentText())
            
            # Build the list of all cities (town, lat, lon, country, state)
            all_cities = []
            for country, states in self.location_data.items():
                for state, towns in states.items():
                    for town, lat, lon in towns:
                        all_cities.append((town, lat, lon, country, state))
            
            all_cities.sort(key=lambda x: x[0])
            
            # Ensure self.cboAllCities points to the existing Kawzar place combo
            if not hasattr(self, 'cboAllCities') or self.cboAllCities is None:
                self.cboAllCities = self.cboKawzarPlace
            
            self.cboAllCities.clear()
            for town, lat, lon, country, state in all_cities:
                self.cboAllCities.addItem(town)
                self.cboAllCities.setItemData(
                    self.cboAllCities.count() - 1,
                    (lat, lon, country, state)
                )
            
            self.cboAllCities.setEditable(False)
            
            # Connect the signal (disconnect first to avoid duplicates)
            try:
                self.cboAllCities.currentIndexChanged.disconnect(self.on_all_cities_changed)
            except:
                pass
            self.cboAllCities.currentIndexChanged.connect(self.on_all_cities_changed)
            
            # Set default city (Taunggyi)
            default_city = "တောင်ကြီး"
            index = self.cboAllCities.findText(default_city, QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.cboAllCities.setCurrentIndex(index)
                self.on_all_cities_changed(index)
            else:
                if self.cboAllCities.count() > 0:
                    self.cboAllCities.setCurrentIndex(0)
                    self.on_all_cities_changed(0)
            
            self.populate_chart_selection()
            print(f"✅ Loaded {len(all_cities)} locations from {len(countries)} countries")
            
        except FileNotFoundError:
            QMessageBox.warning(self, "ဖိုင်မတွေ့", "dataCSV.csv ဖိုင်မတွေ့ပါ။")
            self.create_sample_location_data()
        except Exception as e:
            QMessageBox.critical(self, "အမှား", f"ဒေတာဖိုင်ဖတ်ရာတွင် အမှားရှိနေသည်:\n{str(e)}")
            import traceback
            traceback.print_exc()
            self.populate_chart_selection()

    def populate_chart_selection(self):
        """Populate chart selection combo box"""
        chart_list = [
            "Rasi (D1)", "Bhava", "Navamsa (D9)",
            "Hora (D2)", "Drekkana (D3)", "Chaturthamsa (D4)",
            "Panchamsa (D5)", "Saptamsa (D7)", "Dasamsa (D10)",
            "Vimsamsa (D20)", "Trimsamsa (D30)", "Shashtiamsa (D60)"
        ]
        self.cboCheckable.clear()
        self.cboCheckable.addItems(chart_list)

    def create_sample_location_data(self):
        """Create sample location data if CSV file not found"""
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

    # ==================== UI SETUP METHODS ====================

    def setup_display_widgets(self):
        """Setup chart display widgets inside the first tab with ScrollArea"""
        # Clear any existing layout in the first tab
        if self.tab.layout():
            old_layout = self.tab.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            layout = QVBoxLayout(self.tab)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
        
        main_layout = self.tab.layout()
        
        # === Create Scroll Area for the entire chart area ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("border: none; background-color: transparent;")
        
        # Create a container widget for all charts
        self.charts_container = QWidget()
        self.charts_layout = QVBoxLayout(self.charts_container)
        self.charts_layout.setContentsMargins(10, 10, 10, 10)
        self.charts_layout.setSpacing(20)
        self.charts_layout.setAlignment(Qt.AlignTop)
        
        self.chart_widgets = {}
        
        # First row (D1, Bhava, D9)
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(15)
        first_row_layout.setContentsMargins(0, 0, 0, 0)
        
        self.rasi_chart_widget = BurmeseChartWidget()
        self.rasi_chart_widget.setFixedSize(400, 400)
        self.rasi_chart_widget.set_planet_data([], True, "D1 - ရာသီ")
        first_row_layout.addWidget(self.rasi_chart_widget)
        self.chart_widgets['D1'] = self.rasi_chart_widget
        
        self.bhava_chart_widget = BurmeseChartWidget()
        self.bhava_chart_widget.setFixedSize(400, 400)
        self.bhava_chart_widget.set_planet_data([], False, "Bhava - ဘာဝ")
        first_row_layout.addWidget(self.bhava_chart_widget)
        self.chart_widgets['Bhava'] = self.bhava_chart_widget
        
        self.navamsa_chart_widget = BurmeseChartWidget()
        self.navamsa_chart_widget.setFixedSize(400, 400)
        self.navamsa_chart_widget.set_planet_data([], False, "D9 - နဝင်း")
        first_row_layout.addWidget(self.navamsa_chart_widget)
        self.chart_widgets['D9'] = self.navamsa_chart_widget
        
        self.charts_layout.addLayout(first_row_layout)
        
        # Division charts container
        self.division_container = QFrame()
        self.division_container.setVisible(False)
        div_layout = QVBoxLayout(self.division_container)
        div_layout.setSpacing(20)
        div_layout.setContentsMargins(0, 0, 0, 0)
        
        # Separator
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("background-color: #999; height: 2px; margin: 10px 0;")
        div_layout.addWidget(line1)
        
        # Second Row (D2, D3, D4)
        second_row_layout = QHBoxLayout()
        second_row_layout.setSpacing(15)
        
        self.d2_chart_widget = BurmeseChartWidget()
        self.d2_chart_widget.setFixedSize(400, 400)
        self.d2_chart_widget.set_planet_data([], True, "D2 - ဟောရာ")
        second_row_layout.addWidget(self.d2_chart_widget)
        self.chart_widgets['D2'] = self.d2_chart_widget
        
        self.d3_chart_widget = BurmeseChartWidget()
        self.d3_chart_widget.setFixedSize(400, 400)
        self.d3_chart_widget.set_planet_data([], True, "D3 - တြိကန")
        second_row_layout.addWidget(self.d3_chart_widget)
        self.chart_widgets['D3'] = self.d3_chart_widget
        
        self.d4_chart_widget = BurmeseChartWidget()
        self.d4_chart_widget.setFixedSize(400, 400)
        self.d4_chart_widget.set_planet_data([], True, "D4 - စတုသံသ")
        second_row_layout.addWidget(self.d4_chart_widget)
        self.chart_widgets['D4'] = self.d4_chart_widget
        
        div_layout.addLayout(second_row_layout)

        # Third Row (D5, D7, D10)
        third_row_layout = QHBoxLayout()
        third_row_layout.setSpacing(15)

        self.d5_chart_widget = BurmeseChartWidget()
        self.d5_chart_widget.setFixedSize(400, 400)
        self.d5_chart_widget.set_planet_data([], True, "D5 - ပဉ္စမ")
        third_row_layout.addWidget(self.d5_chart_widget)
        self.chart_widgets['D5'] = self.d5_chart_widget

        self.d7_chart_widget = BurmeseChartWidget()
        self.d7_chart_widget.setFixedSize(400, 400)
        self.d7_chart_widget.set_planet_data([], True, "D7 - သတ္တမ")
        third_row_layout.addWidget(self.d7_chart_widget)
        self.chart_widgets['D7'] = self.d7_chart_widget

        self.d10_chart_widget = BurmeseChartWidget()
        self.d10_chart_widget.setFixedSize(400, 400)
        self.d10_chart_widget.set_planet_data([], True, "D10 - ဒသမ")
        third_row_layout.addWidget(self.d10_chart_widget)
        self.chart_widgets['D10'] = self.d10_chart_widget

        div_layout.addLayout(third_row_layout)

        # Fourth Row (D20, D30, D60)
        fourth_row_layout = QHBoxLayout()
        fourth_row_layout.setSpacing(15)

        self.d20_chart_widget = BurmeseChartWidget()
        self.d20_chart_widget.setFixedSize(400, 400)
        self.d20_chart_widget.set_planet_data([], True, "D20 - ဝိမသမ")
        fourth_row_layout.addWidget(self.d20_chart_widget)
        self.chart_widgets['D20'] = self.d20_chart_widget

        self.d30_chart_widget = BurmeseChartWidget()
        self.d30_chart_widget.setFixedSize(400, 400)
        self.d30_chart_widget.set_planet_data([], True, "D30 - တြိမသမ")
        fourth_row_layout.addWidget(self.d30_chart_widget)
        self.chart_widgets['D30'] = self.d30_chart_widget

        self.d60_chart_widget = BurmeseChartWidget()
        self.d60_chart_widget.setFixedSize(400, 400)
        self.d60_chart_widget.set_planet_data([], True, "D60 - သဠာမ")
        fourth_row_layout.addWidget(self.d60_chart_widget)
        self.chart_widgets['D60'] = self.d60_chart_widget

        div_layout.addLayout(fourth_row_layout)
        self.charts_layout.addWidget(self.division_container)
        
        # Add stretch at the bottom
        self.charts_layout.addStretch()
        
        # Set the container to the scroll area
        self.scroll_area.setWidget(self.charts_container)
        
        # Add scroll area to main layout
        main_layout.addWidget(self.scroll_area)
        
        self.setup_sidebar()

    def setup_sidebar(self):
        """Setup sidebar text widget"""
        container = self.scrollAreaWidgetContents_2
        
        old_layout = container.layout()
        if old_layout is not None:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            old_layout = QVBoxLayout(container)
        
        self.sidebar_text = QTextEdit()
        self.sidebar_text.setReadOnly(True)
        self.sidebar_text.setFont(QFont("Pyidaungsu", 10))
        self.sidebar_text.setMinimumHeight(600)
        old_layout.addWidget(self.sidebar_text)

    def on_all_cities_changed(self, index):
        """When a city is selected from the all-cities combo, update lat/lon fields."""
        if index >= 0:
            data = self.cboAllCities.itemData(index)
            if data and len(data) >= 3:
                lat, lon, country = data[0], data[1], data[2]
                self.txtLat.setText(str(lat))
                self.txtLon.setText(str(lon))
                
                # Set Country combo if exists
                if hasattr(self, 'cboCountry'):
                    country_index = self.cboCountry.findText(country)
                    if country_index >= 0:
                        self.cboCountry.setCurrentIndex(country_index)
                        self.on_country_changed(country)

    
        
        
    def setup_connections(self):
        """Setup signal connections"""
        # --- Location Combos ---
        if hasattr(self, 'cboCountry'):
            self.cboCountry.currentTextChanged.connect(self.on_country_changed)
        
        self.cboState.currentTextChanged.connect(self.on_state_changed)
        self.cboCity.currentTextChanged.connect(self.on_town_changed)
        
        # --- Buttons editPlaces---
        self.btnCalculate.clicked.connect(self.calculate_chart)
        self.btnEditPlace.clicked.connect(self.open_place_editor)
        
        # --- Kawzar Navigation ---
        self.btnKawzarPrev.clicked.connect(self.on_kawzar_previous)
        self.btnKawzarNext.clicked.connect(self.on_kawzar_next)
        self.cboKawzarStep.currentIndexChanged.connect(self.on_kawzar_step_changed)
        
       
        
        # --- File Menu ---
        self.actionNew.triggered.connect(self.new_chart)
        self.actionOpen.triggered.connect(self.open_chart)
        self.actionSave.triggered.connect(self.save_chart)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout_Me.triggered.connect(self.show_about)
        
        # --- Chart Display ---
        self.chkDivision.stateChanged.connect(self.toggle_division_charts)
        self.cboCheckable.currentIndexChanged.connect(self.on_chart_selected)
        
        # --- Kawzar Updates ---
        self.btnCalculate.clicked.connect(self.update_kawzar_after_calc)
        self.cboAllCities.currentIndexChanged.connect(self.update_kawzar_location)
        self.cboDate.dateChanged.connect(self.update_kawzar_time)
        self.cboTime.timeChanged.connect(self.update_kawzar_time)
        
        #self.actionStrength_Table.triggered.connect(self.toggle_strength_table)
        
        # --- View Menu Dock Toggles (အဓိက ပြင်ဆင်ရမည့် အပိုင်း) ---
        
        # Initialize Menu Check States
        self.actionPlanets_info.setChecked(self.docPlanetsInfo.isVisible())
        self.actionStrength_Table.setChecked(self.docStrength.isVisible())
        self.actionRemark_3.setChecked(self.docRemark.isVisible())
        self.actionRemark.setChecked(self.docKawzar.isVisible())
        
        
        
        # 1. Planets Info
        self.actionPlanets_info.toggled.connect(
            lambda checked: self.toggle_dock_visibility(self.docPlanetsInfo, self.actionPlanets_info)
        )
        self.docPlanetsInfo.visibilityChanged.connect(
            lambda visible: self.sync_action_state(self.docPlanetsInfo, self.actionPlanets_info)
        )
        
        # 2. Strength Table (Calculate Logic ကို ဖြုတ်ပြီး Toggle သာ လုပ်စေရန်)
        # အရင်က calculate_and_show_strengths ချိတ်ထားတာကို ဖြုတ်ပါ
        self.actionStrength_Table.toggled.connect(
            lambda checked: self.toggle_dock_visibility(self.docStrength, self.actionStrength_Table)
        )
        self.docStrength.visibilityChanged.connect(
            lambda visible: self.sync_action_state(self.docStrength, self.actionStrength_Table)
        )
        
        # 3. Remark (Ui မှာ actionRemark_3 က "Remark" ဟု ပါရှိသည်)
        self.actionRemark_3.toggled.connect(
            lambda checked: self.toggle_dock_visibility(self.docRemark, self.actionRemark_3)
        )
        self.docRemark.visibilityChanged.connect(
            lambda visible: self.sync_action_state(self.docRemark, self.actionRemark_3)
        )
        
        # 4. Current Planets Position / Kawzar (Ui မှာ actionRemark က "Current Planets Position" ဟု ပါရှိသည်)
        self.actionRemark.toggled.connect(
            lambda checked: self.toggle_dock_visibility(self.docKawzar, self.actionRemark)
        )
        self.docKawzar.visibilityChanged.connect(
            lambda visible: self.sync_action_state(self.docKawzar, self.actionRemark)
        )

    def on_place_saved(self, location_data):
        """Handle data saved from place editor"""
        print(f"📍 Location saved: {location_data}")
        self.load_location_data()
        
        if location_data.get('TownName'):
            index = self.cboAllCities.findText(location_data['TownName'])
            if index >= 0:
                self.cboAllCities.setCurrentIndex(index)

    #File Export to PDF, PNG, SVG, CSV, Excel, etc. (သို့မဟုတ်) Print
    def _export_pdf_menu(self):
        """File menu ထဲတွင် Export PDF action ကို Save အောက်၌ ထည့်သွင်းခြင်း"""

        # တစ်ကြိမ်ပဲ ထည့်စေရန်
        if getattr(self, "_export_pdf_menu_added", False):
            return

        self._export_pdf_menu_added = True

        # UI ထဲမှာ actionExportPDF မပါသေးရင် အသစ်ဖန်တီးမည်
        if not hasattr(self, "actionExportPDF") or self.actionExportPDF is None:
            self.actionExportPDF = QAction(self)
            self.actionExportPDF.setObjectName("actionExportPDF")

        # Text ဗလာဖြစ်နေရင် ထည့်ပေးမည်
        if not self.actionExportPDF.text():
            self.actionExportPDF.setText("Export PDF...")

        self.actionExportPDF.setToolTip("တွက်ချက်ပြီး ဇာတာပုံများကို PDF အဖြစ် သိမ်းဆည်းမည်")
        self.actionExportPDF.setShortcut("Ctrl+Shift+E")
        self.actionExportPDF.setEnabled(True)
        self.actionExportPDF.setVisible(True)

        # Signal ချိတ်ခြင်း
        try:
            self.actionExportPDF.triggered.disconnect()
        except Exception:
            pass

        self.actionExportPDF.triggered.connect(self.export_charts_to_pdf)

        menu_bar = self.menuBar()
        if menu_bar is None:
            return

        # Duplicate မဖြစ်အောင် menu တွေထဲကနေ အရင်ဖြုတ်မည်
        for menu in menu_bar.findChildren(QtWidgets.QMenu):
            if self.actionExportPDF in menu.actions():
                menu.removeAction(self.actionExportPDF)

        target_menu = None

        # Save action ပါဝင်သော menu ကို အရင်ရှာမည်
        if hasattr(self, "actionSave") and self.actionSave is not None:
            for menu in menu_bar.findChildren(QtWidgets.QMenu):
                if self.actionSave in menu.actions():
                    target_menu = menu
                    break

        # File menu ကို ရှာမည်
        if target_menu is None:
            for menu in menu_bar.findChildren(QtWidgets.QMenu):
                title = menu.title().replace("&", "").strip().lower()
                if title in ("file", "ဖိုင်"):
                    target_menu = menu
                    break

        # မတွေ့ရင် ပထမ menu သို့မဟုတ် File menu အသစ်
        if target_menu is None:
            menus = menu_bar.findChildren(QtWidgets.QMenu)
            if menus:
                target_menu = menus[0]
            else:
                target_menu = menu_bar.addMenu("File")

        # Save အောက်မှာ ထည့်မည်
        if hasattr(self, "actionSave") and self.actionSave in target_menu.actions():
            actions = target_menu.actions()
            save_index = actions.index(self.actionSave)

            if save_index + 1 < len(actions):
                target_menu.insertAction(actions[save_index + 1], self.actionExportPDF)
            else:
                target_menu.addAction(self.actionExportPDF)
        else:
            target_menu.addAction(self.actionExportPDF)
    
    def export_charts_to_pdf(self):
        """တွက်ချက်ပြီး ဇာတာပုံများကို PDF အဖြစ် သိမ်းဆည်းခြင်း
        A4, Full Page, Margin 0.35 inch around
        """

        if not getattr(self, "current_planet_data", None):
            QMessageBox.warning(self, "သတိပေးချက်", "ကျေးဇူးပြု၍ ဦးစွာ ဇာတာကို တွက်ချက်ပေးပါ။")
            return

        default_name = self.txtName.text().strip() or "Zarta"

        settings = QtCore.QSettings("MyCompany", "BharaniApp")
        last_dir = settings.value("lastPdfExportDir", QtCore.QDir.homePath())
        default_path = os.path.join(last_dir, f"{default_name}.pdf")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF ဖိုင် သိမ်းရန် နေရာ ရွေးပါ",
            default_path,
            "PDF Files (*.pdf)"
        )

        if not file_path:
            self.statusbar.showMessage("PDF သိမ်းဆည်းခြင်း မလုပ်ပါ")
            return

        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"

        settings.setValue("lastPdfExportDir", os.path.dirname(file_path))

        painter = QPainter()
        painter_started = False
        error_message = None

        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)

            # A4 size
            printer.setPageSize(QPrinter.A4)

            # Resolution
            printer.setResolution(150)

            # ✅ Full Page coordinate system
            printer.setFullPage(True)

            widget = self.charts_container
            widget.ensurePolished()
            widget.adjustSize()

            pixmap = widget.grab()

            if pixmap.isNull():
                raise Exception("ဇာတာပုံ widget ကို ဖမ်းယူ၍ မရပါ။")

            if not painter.begin(printer):
                raise Exception("PDF writer ကို စတင်၍ မရပါ။")

            painter_started = True

            # ✅ Margin 0.35 inch around
            dpi = printer.resolution()
            margin_inch = 0.35
            margin_px = int(margin_inch * dpi)

            paper_rect = printer.paperRect(QPrinter.DevicePixel)

            page_x = margin_px
            page_y = margin_px
            page_w = int(paper_rect.width()) - 2 * margin_px
            page_h = int(paper_rect.height()) - 2 * margin_px
            birth_date = self.cboDate.date()
            birth_time = self.cboTime.time()
            birth_dt = datetime(
                birth_date.year(), birth_date.month(), birth_date.day(),
                birth_time.hour(), birth_time.minute(), birth_time.second(),
            )
            myanmar_date = self.format_myanmar_date(birth_dt)
            header_height = int(0.45 * dpi)

            if page_w <= 0 or page_h <= 0:
                raise Exception("PDF စာမျက်နှာ အရွယ်အစား မမှန်ပါ။")

            # Chart container ကို PDF page width နဲ့ ကိုက်ညီအောင် scale လုပ်ခြင်း
            scaled = pixmap.scaledToWidth(page_w, Qt.SmoothTransformation)

            if scaled.isNull() or scaled.height() <= 0:
                raise Exception("PDF အတွက် ပုံဖမ်းယူမှု မအောင်မြင်ပါ။")

            y = 0
            first_page = True

            while y < scaled.height():
                if not first_page:
                    printer.newPage()

                first_page = False

                # စာမျက်နှာ နောက်ခံ အဖြူရောင်
                painter.fillRect(paper_rect, QColor(Qt.white))

                current_header_height = header_height if first_page is False and y == 0 else 0
                if y == 0:
                    current_header_height = header_height
                    painter.setPen(QColor(Qt.black))
                    painter.setFont(QFont("Pyidaungsu", 11, QFont.Bold))
                    painter.drawText(
                        page_x,
                        page_y + int(0.18 * dpi),
                        page_w,
                        int(0.2 * dpi),
                        Qt.AlignCenter,
                        myanmar_date,
                    )

                segment_h = int(min(page_h - current_header_height, scaled.height() - y))

                # ✅ Left margin 0.35 inch
                x = page_x + max(0, (page_w - scaled.width()) // 2)

                # ✅ Top margin 0.35 inch
                painter.drawPixmap(
                    x,
                    page_y + current_header_height,
                    scaled,
                    0,
                    y,
                    scaled.width(),
                    segment_h
                )

                y += segment_h

        except Exception as e:
            error_message = str(e)
            import traceback
            traceback.print_exc()

        finally:
            # ✅ PDF writer ကို လုံခြုံစွာ ပိတ်ခြင်း
            if painter_started:
                painter.end()

        if error_message:
            QMessageBox.critical(
                self,
                "အမှား",
                f"PDF သိမ်းဆည်းရာတွင် အမှားရှိနေပါသည်:\n{error_message}"
            )
        else:
            self.statusbar.showMessage(f"✅ PDF သိမ်းပြီး: {file_path}")
            QMessageBox.information(
                self,
                "အောင်မြင်ပါသည်",
                f"PDF ဖိုင်ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။\n{file_path}"
            )

    # ==================== KAWZAR HANDLERS ====================

    def update_kawzar_to_now(self):
        """Now ခလုတ်နှိပ်သည့်အခါ လက်ရှိအချိန်နှင့် နေရာသို့ ပြန်သွားခြင်း"""
        if not hasattr(self, 'kawzar_widget') or not KAWZAR_MODULE_AVAILABLE:
            return
        
        current_datetime = QDateTime.currentDateTime()
        self.kawzar_widget.set_datetime(current_datetime)
        
        city_index = self.cboAllCities.currentIndex()
        if city_index >= 0:
            city_name = self.cboAllCities.currentText()
            location_data = self.cboAllCities.itemData(city_index)
            
            if location_data and len(location_data) >= 2:
                lat, lon = location_data[0], location_data[1]
                self.kawzar_widget.set_location(city_name, lat, lon)
        
        for i in range(self.cboTimezone.count()):
            if self.cboTimezone.itemData(i) == 6.5:
                self.cboTimezone.setCurrentIndex(i)
                break
        
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        
        self.statusbar.showMessage("🕐 ကောဇာဂြိုဟ်များကို လက်ရှိအချိန်သို့ ပြန်လည်သတ်မှတ်ပြီးပါပြီ")
        print("✅ Kawzar reset to current time and default place")

    def on_kawzar_previous(self):
        """ကောဇာ ရှေ့သို့ သွားခြင်း"""
        if hasattr(self, 'kawzar_widget') and KAWZAR_MODULE_AVAILABLE:
            step_type = self.get_kawzar_step_type()
            self.kawzar_widget.navigate_time(-1, step_type)
            self.statusbar.showMessage(f"ကောဇာ: ရှေ့သို့ {step_type} ရွှေ့လိုက်သည်")

    def on_kawzar_next(self):
        """ကောဇာ နောက်သို့ သွားခြင်း"""
        if hasattr(self, 'kawzar_widget') and KAWZAR_MODULE_AVAILABLE:
            step_type = self.get_kawzar_step_type()
            self.kawzar_widget.navigate_time(1, step_type)
            self.statusbar.showMessage(f"ကောဇာ: နောက်သို့ {step_type} ရွှေ့လိုက်သည်")

    def on_kawzar_step_changed(self, index):
        """ကောဇာ အဆင့် ပြောင်းလဲခြင်း"""
        if hasattr(self, 'kawzar_widget') and KAWZAR_MODULE_AVAILABLE:
            step_text = self.cboKawzarStep.currentText()
            step_type = self.get_kawzar_step_type()
            self.kawzar_widget.set_step_display(step_text)
            self.statusbar.showMessage(f"ကောဇာ အဆင့်: {step_text}")

    def get_kawzar_step_type(self):
        """ကောဇာ အဆင့်အမျိုးအစား ရယူခြင်း"""
        step_map = {
            'Sec': 'sec', 'Min': 'min', 'Hour': 'hour',
            'Day': 'day', 'Month': 'month', 'Year': 'year'
        }
        step_text = self.cboKawzarStep.currentText()
        return step_map.get(step_text, 'min')

    def update_kawzar_after_calc(self):
        """ဇာတာတွက်ပြီးနောက် ကောဇာကို အပ်ဒိတ်လုပ်ခြင်း"""
        self.update_kawzar_location()
        self.update_kawzar_time()

    # ==================== LOCATION HANDLERS ====================

    def on_country_changed(self, country):
        """Handle country change in location combo"""
        print(f"on_country_changed: country = '{country}'")
        print(f"location_data keys: {list(self.location_data.keys())}")
        
        if country == "-- ရွေးပါ --" or not country:
            return
        
        if country not in self.location_data:
            return
        
        self.cboState.clear()
        self.cboCity.clear()
        self.txtLat.clear()
        self.txtLon.clear()
        
        states = sorted(self.location_data[country].keys())
        self.cboState.addItem("-- ရွေးပါ --")
        self.cboState.addItems(states)
        
        if states:
            self.cboState.setCurrentIndex(1)
            self.on_state_changed(states[0])

    def on_state_changed(self, state):
        """Handle state change in location combo"""
        country = self.cboCountry.currentText() if hasattr(self, 'cboCountry') else "မြန်မာ"
       
        print(f"on_state_changed: country = '{country}', state = '{state}'")
        print(f"states for {country}: {list(self.location_data.get(country, {}).keys())}")
       
       
        if country == "-- ရွေးပါ --" or not country:
            return
        
        if country not in self.location_data:
            return
        
        self.cboCity.clear()
        self.txtLat.clear()
        self.txtLon.clear()
        
        if state in self.location_data[country]:
            towns = [item[0] for item in self.location_data[country][state]]
            self.cboCity.addItem("-- ရွေးပါ --")
            self.cboCity.addItems(towns)
            
            if towns:
                self.cboCity.setCurrentIndex(1)
                self.on_town_changed(towns[0])

    def on_town_changed(self, town):
        """Handle town change in location combo"""
        country = self.cboCountry.currentText() if hasattr(self, 'cboCountry') else "မြန်မာ"
        state = self.cboState.currentText()
        
        if country == "-- ရွေးပါ --" or not country:
            return
        if not state or not town:
            return
        
        if country in self.location_data and state in self.location_data[country]:
            for t, lat, lon in self.location_data[country][state]:
                if t == town:
                    self.txtLat.setText(lat)
                    self.txtLon.setText(lon)
                    break

    # ==================== CALCULATION METHODS ====================
    
    def sign_to_number(self, sign_name):
        return ZODIAC_SIGNS_EN.index(sign_name) + 1

    def number_to_sign(self, num):
        return ZODIAC_SIGNS_EN[num - 1]

    def compute_nth_sign(self, from_sign_num, n):
        return ((from_sign_num - 1 + (n - 1)) % 12) + 1

    def get_ayanamsa_flag(self):
        ayanamsa_name = self.cboAyana.currentText().strip()
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
        house_system_name = self.cboHouseSys.currentText()
        mapping = {"Whole Sign": b'W', "Vehlow Equal": b'E', "Equal": b'A',
                   "Placidus": b'P', "Sripati": b'S', "Porphyry": b'O'}
        return mapping.get(house_system_name, b'E')

    def validate_coordinates(self, lat, lon):
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

    def calculate_vimshottari_dasa(self, moon_longitude, birth_dt):
        """Calculate Vimshottari Mahadasha periods"""
        nakshatra_degree = 360/27
        nakshatra_index = int(moon_longitude / nakshatra_degree)
        passed_fraction = (moon_longitude % nakshatra_degree) / nakshatra_degree

        nakshatra_lords = [
            'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
            'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
            'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
        ]

        first_lord = nakshatra_lords[nakshatra_index]
        dasa_order = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        dasa_years = {'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17}

        mahadashas = {}
        start_date = birth_dt
        first_index = dasa_order.index(first_lord)
        ordered_lords = dasa_order[first_index:] + dasa_order[:first_index]

        for i in range(9):
            lord = ordered_lords[i]
            years = dasa_years[lord]
            if i == 0:
                years = years * (1 - passed_fraction)
            end_date = start_date + timedelta(days=round(years * 365.25))
            mahadashas[lord] = {
                'start': start_date,
                'end': end_date,
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'is_current': (start_date <= datetime.now() <= end_date)
            }
            start_date = end_date

        return mahadashas

    def calculate_motion_info(self, jd, planet_data):
        """ဂြိုဟ်များ၏ အသွားနှုန်း (ဝကြ/တိုက်/သီဟဇာ) နှင့် သိင်္ဃ အခြေအနေ တွက်ချက်ခြင်း"""
        sun_lon = next((p['longitude'] for p in planet_data if p['name'] == 'Sun'), 0)

        for p in planet_data:
            name = p['name']
            # လဂ် နှင့် နေ သည် အမြဲ တိုက်ရိုက် ဖြစ်သည်
            if name in ('Lagna', 'Sun'):
                p['motion_info'] = "တိုက်ရိုက် ➡"
                continue
            
            # ရာဟု/ကေတု သည် ဂန္ထဝင်အရ အမြဲ ဝကြသွား ဖြစ်သည်
            if name in ('Rahu', 'Ketu'):
                p['motion_info'] = "ဝကြသွား ↺"
                continue

            pid = p.get('id')
            
            try:
                if isinstance(pid, int):
                    # Swiss Ephemeris မှ အသွားနှုန်း တိုက်ရိုက်ယူခြင်း (°/day)
                    xx, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
                    speed = xx[3]  

                    # အသွားအမျိုးအစား ဆုံးဖြတ်ခြင်း
                    if abs(speed) < 0.02:
                        state = "သီဟဇာ ⏸"
                    elif speed < 0:
                        state = "ဝကြသွား ↺"
                    else:
                        state = "တိုက်ရိုက် ➡"

                    # သိင်္ဃ (Combust) စစ်ဆေးခြင်း (နေနှင့် ၈° အတွင်း ရောက်နေပါက)
                    diff = abs(p['longitude'] - sun_lon)
                    if diff > 180: diff = 360 - diff
                    combust_limit = 8.0  # ဂြိုဟ်အလိုက် ပြင်ဆင်နိုင်
                    if diff < combust_limit:
                        state = f"သိင်္ဃ 🔥 {state}"

                    p['motion_info'] = state
                else:
                    p['motion_info'] = "-"
            except Exception:
                p['motion_infot'] = "-"
                
#တွက်ချက် မှု စတင်ပါ============================                
    def calculate_chart(self):
        """Main chart calculation"""
        try:
            name = self.txtName.text().strip()
            if not name:
                name = "အမည်မသိ"
            
            birth_date = self.cboDate.date()
            birth_time = self.cboTime.time()
            tz_offset = self.cboTimezone.currentData()
            if tz_offset is None:
                tz_offset = 6.5  # default Myanmar timezone
            
            lat_text = self.txtLat.text().strip()
            lon_text = self.txtLon.text().strip()
            valid, lat, lon = self.validate_coordinates(lat_text, lon_text)
            if not valid:
                QMessageBox.warning(self, "Coordinate Error", f"Invalid coordinates: {lat_text}, {lon_text}")
                return
            
            # Convert to datetime
            birth_dt = datetime(birth_date.year(), birth_date.month(), birth_date.day(),
                                birth_time.hour(), birth_time.minute(), birth_time.second())
            
            # Adjust for timezone offset (hours to days)
            tz_hours = tz_offset
            jd = swe.julday(birth_dt.year, birth_dt.month, birth_dt.day,
                           birth_dt.hour + birth_dt.minute/60.0 + birth_dt.second/3600.0 - tz_hours)
            
            ayanamsa_flag = self.get_ayanamsa_flag()
            
            
            swe.set_sid_mode(ayanamsa_flag)  #Sidereal Mode သတ်မှတ်ခြင်း
            
            #=======================================================================
            # Compute ascendant and houses
            
            house_sys = self.get_house_system_code()

            cusps_tropical, ascmc_tropical = swe.houses(jd, lat, lon, house_sys)
            ayanamsa = swe.get_ayanamsa(jd)
            
            ascendant = (ascmc_tropical[0]-ayanamsa ) %360

            houses = [(c-ayanamsa) % 360 for c in cusps_tropical[:12]]
            # Store house cusps for later use
            self.current_houses_cusps = houses
            
            # Compute planets
            planet_data = []
            for planet_id in PLANET_IDS:
                try:
                    xx, flags = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
                    #xx, flags = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
                    lon_deg = xx[0]
                    # Convert to 0-360 range
                    lon_deg = lon_deg % 360
                    sign = int(lon_deg / 30)
                    deg = lon_deg % 30
                    minutes = (deg * 60) % 60
                    seconds = (minutes * 60) % 60
                    
                    
                    planet_data.append({
                    'id': planet_id,
                    'name': swe.get_planet_name(planet_id),
                    'symbol': PLANET_SYMBOLS.get(planet_id, '?'),
                    'longitude': lon_deg,
                    'sign': sign,
                    'deg': int(deg),
                    'min': int(minutes),
                    'sec': int(seconds),
                    'sign_name': ZODIAC_SIGNS_EN[sign],
                    'retro': xx[3] < 0
                })
                except Exception as e:
                    print(f"Error calculating planet {planet_id}: {e}")
            
            # Compute Rahu and Ketu (mean nodes)
            rahu_lon = 0.0 #Initialize to prevet UnboundLocalError
            try:
                #xx, flags = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
                
                #flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_TRUE_NODE  # True Node ကို အတည်ပြုခြင်း
                flags_nodes = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
                xx, _ = swe.calc_ut(jd, swe.TRUE_NODE, flags_nodes)
                
                rahu_lon = xx[0] % 360
                ketu_lon = (rahu_lon + 180) % 360
                
                # Add Rahu and Ketu as pseudo-planets
                for node, name, lon in [(swe.TRUE_NODE, 'Rahu', rahu_lon), (swe.TRUE_NODE+1, 'Ketu', ketu_lon)]:
                    sign = int(lon / 30)
                    deg = lon % 30
                    minutes = (deg * 60) % 60
                    seconds = (minutes * 60) % 60
                    planet_data.append({
                        'id': node,
                        'name': name,
                        'symbol': PLANET_SYMBOLS.get(name, '?'),
                        'longitude': lon,
                        'sign': sign,
                        'deg': int(deg),
                        'min': int(minutes),
                        'sec': int(seconds),
                        'sign_name': ZODIAC_SIGNS_EN[sign]
                    })
            except Exception as e:
                print(f"⚠️ Error calculating nodes: {e}")
            
            # Add Lagna (Ascendant)
            asc_sign = int(ascendant / 30)
            asc_deg = ascendant % 30
            asc_min = (asc_deg * 60) % 60
            asc_sec = (asc_min * 60) % 60
            planet_data.append({
                'id': 'Lagna',
                'name': 'Lagna',
                'symbol': 'Asc',
                'longitude': ascendant,
                'sign': asc_sign,
                'deg': int(asc_deg),
                'min': int(asc_min),
                'sec': int(asc_sec),
                'sign_name': ZODIAC_SIGNS_EN[asc_sign]
            })
            
            self.current_planet_data = planet_data
            self.current_ascendant = ascendant
            
            #ဂြိုဟ် သွားနှုန်း တွက်ခြင်း
            try:
                self.calculate_motion_info(jd, planet_data)
            except Exception as e:
                print(f"Motion info calculation skipped: {e}")
                
                
            #Planet ifo  table တည်ဆောက်ခြင်း
            if hasattr(self, 'planet_info_widget'):
                self.planet_info_widget.update_data(planet_data)
            
            # Update Rasi chart (Whole sign)
            rasi_data = self.prepare_chart_data(planet_data, use_whole_sign=True)
            self.rasi_chart_widget.set_planet_data(rasi_data, True, "D1 - ရာသီ")
            
            # Update Bhava chart (using house cusps)
            bhava_data = self.prepare_chart_data(planet_data, use_whole_sign=False, houses=houses)
        
            # 🔧 FIX: Pass calculated house cusps to the Bhava chart widget
            # The widget needs these cusps to redraw house boundaries according to the selected system.
            try:
                # ဘာဝစနစ်အလိုက် အိမ်အစွန်းများကို Widget ထံ တိုက်ရိုက်ပို့ပေးသည်
                self.bhava_chart_widget.set_planet_data(bhava_data, False, "Bhava - ဘာဝ", houses=houses)
            except TypeError:
                # အကယ်၍ widget ၏ signature မတူညီပါက အောက်ပါ fallback ကို သုံးပါ
                self.bhava_chart_widget.set_planet_data(bhava_data, False, "Bhava - ဘာဝ")
                if hasattr(self.bhava_chart_widget, 'set_house_cusps'):
                    self.bhava_chart_widget.set_house_cusps(houses)
                elif hasattr(self.bhava_chart_widget, 'cusps'):
                    self.bhava_chart_widget.cusps = houses
                    self.bhava_chart_widget.update()
                    
            # Navamsa (D9) - for now using simple rule (3°20' per amsa)
            navamsa_data = self.calculate_division_chart(planet_data, "D9")
            self.navamsa_chart_widget.set_planet_data(navamsa_data, True, "D9 - နဝင်း")
            
            # Update division charts if needed
            if self.chkDivision.isChecked():
                self.update_division_charts(planet_data)
            
            # Update sidebar
            self.update_sidebar_text(planet_data, name, birth_dt, lat, lon, jd)
            

            # Update Dasa table if available
            if self.dasa_table:
                moon = next((p for p in planet_data if p.get('id') == swe.MOON), None)
                if moon:
                    moon_long = moon['longitude']
                    try:
                        mahadashas, antardashas, prayantardashas = self.calculate_full_vimshottari_dasa(moon_long, birth_dt)
                        self.dasa_table.set_dasa_data(mahadashas, antardashas, prayantardashas)
                    except Exception as e:
                        print(f"Error calculating dasa: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("Warning: Moon position not found, Dasa table not updated.")
            
            #calculate strengths and update strength table if available
            self.calculate_and_show_strengths()
            

                    
            #နာရာယဏ ဒဿာ ပြဆိုပါသည်
                    # === Narayana Dasha Calculation ===
            if hasattr(self, 'narayana_widget') and self.current_planet_data:
                try:
                    # လဂ်နာ Sign Index (0-11) ရယူခြင်း
                    asc_sign = int(self.current_ascendant / 30)
                    
                    # ဂြိုဟ်များ၏ Sign Position Dict ဖန်တီးခြင်း
                    planet_positions = {p['name']: p['sign'] for p in self.current_planet_data}
                    
                    # တွက်ချက်ခြင်း
                    calc = NarayanaDashaCalculator(asc_sign, birth_dt)
                    narayana_periods = calc.calculate(planet_positions, levels=3)
                    
                    # UI သို့ ပို့ဆောင်ခြင်း
                    self.narayana_widget.set_data(narayana_periods)
                except Exception as e:
                    print(f"Narayana Dasha calculation error: {e}")
                    
                
            # ======================================================================
            # === Ashtakavarga (BAV & SAV) Calculation (D1 Chart အပေါ်အခြေခံ) ===
            # ======================================================================
            if hasattr(self, 'ashta_matrix') and self.current_planet_data:
    
                try:
                    # ✅ ပထမ line - ဒါကိုထားပါ
                    house_sys_code = self.get_house_system_code()
                    
                    # ✅ ဒုတိယ line - ဒါကိုထားပါ
                    ashta_calc = AshtakavargaCalculator(
                        ayanamsa_flag=self.get_ayanamsa_flag(),
                        house_sys=house_sys_code.decode() if isinstance(house_sys_code, bytes) else house_sys_code
                    )
                    
                    
                    
                    # ✅ တတိယ line - ဒါကိုထားပါ
                    widget_data = ashta_calc.calculate_all_for_widget(jd, lat, lon)
                    self.ashta_matrix.update_all_matrix_data(widget_data)
                    
                    print("✅ Ashtakavarga (D1) calculation complete.")

                except Exception as e:
                    print(f"⚠️ Ashtakavarga Calculation Error: {e}")
                    import traceback
                    traceback.print_exc()
            
            self.statusbar.showMessage("ဇာတာတွက်ချက်မှု ပြီးစီးပါပြီ")
            
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Error during calculation:\n{str(e)}")
            import traceback
            traceback.print_exc()
            
    
    
 
    def prepare_chart_data(self, planet_data, use_whole_sign=True, houses=None):
        """Convert planet_data to format expected by chart widget"""
        
        chart_data = []
        
        for p in planet_data:
            lon = p['longitude']

            if use_whole_sign:
                # D1 (ရာသီ) Chart: ရာသီအလိုက် # The above code is written in the Python programming
                # language. However, the code itself is commented out
                # using the "#" symbol, so it is not actually executing
                # any instructions. It appears to be a placeholder or a
                # reminder for someone to write code to perform a
                # specific task.
                #ဒီဂရီပြတ်သားစွာ ယူမည်
                sign = p['sign']
                deg = p['deg']
                min_ = p['min']
                house = sign + 1
            else:
                # Bhava Chart: တကယ့်ရာသီနေရာကို မပြောင်းဘဲ ထားမည်
                house = self.get_house_number(lon, houses) if houses else p['sign'] + 1
                 
                
                # ဒီဂရီနှင့် မိနစ်ကို တိကျစွာ ခွဲထုတ်ခြင်း (Math Fix)
                deg_in_sign = lon % 30.0
                deg = int(deg_in_sign)
                min_ = int(round((deg_in_sign - deg) * 60)) 
                sign = p['sign']
                #  မှတ်ချက်: အိမ်နံပါတ်ကို သီးသန့်သိထားလိုပါက 
                # p['house_num'] = self.get_house_number(lon, houses) လို့ သီးသန့်ထည့်နိုင်ပါတယ်။
                # ဒါပေမယ့် Chart Widget ဆွဲဖို့အတွက် sign ကို ပြောင်းစရာမလိုပါ။
                
            chart_data.append({
                'name': p['name'],
                'symbol': p['symbol'],
                'sign': sign,      # ✅ တကယ့်ရာသီအညွှန်း (0-11)
                'deg': deg,        # ✅ ကိန်းပြည့် ဒီဂရီ
                'min': min_,       # ✅ ကိန်းပြည့် မိနစ်
                
                'retro': p.get('retro', False)
            })
        return chart_data
    def get_house_number(self, longitude, cusps):
        """ဂြိုဟ်၏ longitude အရ ဘာဝအိမ်နံပါတ် (1-12) တွက်ချက်ပေးမည့် function"""
        if not cusps or len(cusps) < 2:
            return 1
        
        # cusps 12 ခုသာယူပါ (swe.houses မှ 13 ခုပြန်ပေးတတ်သည်)
        c_list = cusps[:12]
        
        for i in range(12):
            c1 = c_list[i]
            c2 = c_list[(i + 1) % 12]
            
            # 360° ကျော်ဖြတ်သွားသော အိမ်များအတွက် စစ်ဆေးခြင်း
            if c1 <= c2:
                if c1 <= longitude < c2:
                    return i + 1
            else:
                if longitude >= c1 or longitude < c2:
                    return i + 1
                    
        return 12  # နယ်စပ်ကျနေပါက ၁၂ လဂ်ဟု သတ်မှတ်မည်

    def calculate_division_chart(self, rasi_results, chart_name):
        """စံနှုန်းမီ Varga (Divisional Chart) တွက်ချက်ခြင်း (D2 မှ D60 အထိ)"""
        division_results = []
        
        # Chart name မှ Division Number ထုတ်ယူခြင်း (ဥပမာ "D9" -> 9)
        try:
            div_num = int(chart_name.replace("D", "").strip())
        except ValueError:
            div_num = 1  # Fallback to D1

        for p in rasi_results:
            p_long = p.get('longitude', 0.0)
            
            # ✅ Vedic Astrology ၏ တရားဝင် စံနှုန်း ပုံသေနည်း
            div_total_lon = (p_long * div_num) % 360.0
            
            div_sign_0based = int(div_total_lon / 30)
            div_deg = div_total_lon % 30
            div_min = int((div_deg * 60) % 60)
            
            new_p = p.copy()
            new_p['longitude'] = div_total_lon
            new_p['sign'] = div_sign_0based
            new_p['deg'] = int(div_deg)
            new_p['min'] = div_min
            new_p['sign_name'] = ZODIAC_SIGNS_EN[div_sign_0based]
            division_results.append(new_p)
            
        return division_results

    def calculate_hora_d2(self, sign_num, degrees):
        """Calculate D2 chart"""
        is_odd = sign_num in ODD_SIGNS
        if degrees < 15:
            div_sign_num = 5 if is_odd else 4
        else:
            div_sign_num = 4 if is_odd else 5
        div_deg = degrees if degrees < 15 else (degrees - 15)
        return div_sign_num, div_deg

    def calculate_drekkana_d3(self, sign_num, degrees):
        """Calculate D3 chart"""
        amsa = 10.0
        part = int(degrees / amsa)
        if sign_num in MOVABLE_SIGNS:
            div_sign_num = self.compute_nth_sign(sign_num, part + 1)
        elif sign_num in FIXED_SIGNS:
            div_sign_num = self.compute_nth_sign(sign_num, part + 5)
        else:
            div_sign_num = self.compute_nth_sign(sign_num, part + 9)
        div_deg = degrees % amsa
        return div_sign_num, div_deg

    def update_division_charts(self, rasi_results):
        """D2 မှ D60 အထိ ဝဂ္ဂဇာတာများကို ပြန်လည်တွက်ချက်ပြီး အပ်ဒိတ်လုပ်ခြင်း"""
        division_specs = {
            "D2": ("D2 - ဟောရာ", self.d2_chart_widget),
            "D3": ("D3 - တြိင်း", self.d3_chart_widget),
            "D4": ("D4 - စတုသံသ", self.d4_chart_widget),
            "D5": ("D5 - ပဉ္စမ", self.d5_chart_widget),
            "D7": ("D7 - သတ္တံသင်း", self.d7_chart_widget),
            "D10": ("D10 - ဒသံသင်း", self.d10_chart_widget),
            "D20": ("D20 - ဝိမသမ", self.d20_chart_widget),
            "D30": ("D30 - တြိမသမ", self.d30_chart_widget),
            "D60": ("D60 - သဠာမ", self.d60_chart_widget),
        }

        for division_name, (label, widget) in division_specs.items():
            if widget is None:
                continue
            division_data = self.calculate_division_chart(rasi_results, division_name)
            widget.set_planet_data(division_data, False, label)

    def toggle_division_charts(self, state):
        print("toggle_division_charts called, state = ", state)
        if hasattr(self, 'division_container'):
            print("division_container exists")
            self.division_container.setVisible(state == Qt.Checked)
            if state == Qt.Checked and self.current_planet_data is not None:
                self.update_division_charts(self.current_planet_data)
        else:
            print("division_container does NOT exist")

    def new_chart(self):
        """New chart: reset all fields"""
        self.txtName.clear()
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        self.cboTimezone.setCurrentIndex(self.cboTimezone.findData(6.5))
        # Reset location to default (Taunggyi)
        index = self.cboAllCities.findText("တောင်ကြီး")
        if index >= 0:
            self.cboAllCities.setCurrentIndex(index)
        else:
            self.on_all_cities_changed(0)
        # Clear chart widgets
        self.rasi_chart_widget.set_planet_data([], True, "D1 - ရာသီ")
        self.bhava_chart_widget.set_planet_data([], False, "Bhava - ဘာဝ")
        self.navamsa_chart_widget.set_planet_data([], False, "D9 - နဝင်း")
        self.sidebar_text.clear()
        self.current_planet_data = None
        self.statusbar.showMessage("ဇာတာအသစ်အတွက် ပြင်ဆင်ပြီးပါပြီ")

    def load_charts_data(self):
        """Load all charts from ZartarData.brn"""
        if os.path.exists(self.CHARTS_FILE):
            try:
                with open(self.CHARTS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading charts: {e}")
        return {}

    def save_charts_data(self, data):
        """Save all charts to ZartarData.brn"""
        with open(self.CHARTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
            
    def save_chart(self):
        """Save current chart to ZartarData.brn with duplicate checking"""
        if self.current_planet_data is None:
            QMessageBox.warning(self, "Warning", "No chart data to save. Please calculate first.")
            return

        # Gather current data
        current_data = {
            "name": self.txtName.text().strip(),
            "date": self.cboDate.date().toString("yyyy-MM-dd"),
            "time": self.cboTime.time().toString("HH:mm:ss"),
            "timezone": self.cboTimezone.currentText(),
            "country": self.cboCountry.currentText(),
            "state": self.cboState.currentText(),
            "city": self.cboCity.currentText(),
            "lat": self.txtLat.text(),
            "lon": self.txtLon.text(),
            "ayanamsa": self.cboAyana.currentText(),
            "house_system": self.cboHouseSys.currentText(),
        }

        name = current_data["name"]
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a name before saving.")
            return

        charts = self.load_charts_data()

        # Check for existing entry with same name
        existing = charts.get(name)

        if existing:
            # Compare data (date, time, location, etc.)
            same_data = True
            for key in ["date", "time", "timezone", "country", "state", "city", "lat", "lon", "ayanamsa", "house_system"]:
                if existing.get(key) != current_data.get(key):
                    same_data = False
                    break
            if same_data:
                QMessageBox.information(self, "Info", f"Chart '{name}' already saved with identical data. No save needed.")
                return
            else:
                # Ask user what to do
                msg = f"A chart with the name '{name}' already exists but with different data.\n\n"
                msg += "Do you want to:\n"
                msg += "• Overwrite the existing chart\n"
                msg += "• Save as a new chart (with a modified name)"
                reply = QMessageBox.question(self, "Duplicate Name", msg,
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                            QMessageBox.No)
                if reply == QMessageBox.Cancel:
                    return
                elif reply == QMessageBox.Yes:
                    # Overwrite: update existing entry
                    charts[name] = current_data
                else:
                    # Save as new: ask for new name
                    new_name, ok = QInputDialog.getText(self, "New Name", "Enter a new name for this chart:",
                                                        text=name + " (1)")
                    if not ok or not new_name.strip():
                        return
                    name = new_name.strip()
                    current_data["name"] = name
                    if name in charts:
                        QMessageBox.warning(self, "Warning", f"A chart with name '{name}' already exists. Please choose another name.")
                        return
                    charts[name] = current_data
        else:
            charts[name] = current_data

        # Save all charts
        self.save_charts_data(charts)

        self.statusbar.showMessage(f"Chart saved as '{name}'")

    def open_chart(self):
        """Open a saved chart from ZartarData.brn"""
        charts = self.load_charts_data()
        
        if not isinstance(charts, dict):
            QMessageBox.warning(self, "Error", "Chart data is corrupted. Please re-save your charts.")
            return
        
        if not charts:
            QMessageBox.information(self, "Info", "No saved charts found.")
            return

        # Create a dialog to select a chart
        dialog = QDialog(self)
        dialog.setWindowTitle("Open Chart")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)

        # List widget to display charts
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.SingleSelection)

        # Populate list with name, date, location
        for name, data in charts.items():
            if not isinstance(data, dict):
                continue  # skip invalid entries
            date = data.get("date", "?")
            loc = data.get("city", "")
            if not loc:
                loc = f"{data.get('lat', '')}, {data.get('lon', '')}"
            display_text = f"{name}  ({date})  {loc}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, name)  # store name for retrieval
            list_widget.addItem(item)

        layout.addWidget(QLabel("Select a chart to open:"))
        layout.addWidget(list_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_open = QPushButton("Open")
        btn_cancel = QPushButton("Cancel")
        btn_layout.addStretch()
        btn_layout.addWidget(btn_open)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        def on_open():
            current = list_widget.currentItem()
            if current:
                name = current.data(Qt.UserRole)
                data = charts.get(name)
                if data and isinstance(data, dict):
                    # Restore UI fields
                    # Use the key name if the stored name is empty, otherwise use stored name
                    stored_name = data.get("name", "")
                    if stored_name:
                        self.txtName.setText(stored_name)
                    else:
                        self.txtName.setText(name)
                    
                    date_str = data.get("date", "")
                    if date_str:
                        qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                        if qdate.isValid():
                            self.cboDate.setDate(qdate)
                    
                    time_str = data.get("time", "")
                    if time_str:
                        qtime = QTime.fromString(time_str, "HH:mm:ss")
                        if qtime.isValid():
                            self.cboTime.setTime(qtime)
                    
                    tz_text = data.get("timezone", "")
                    if tz_text:
                        idx = self.cboTimezone.findText(tz_text)
                        if idx >= 0:
                            self.cboTimezone.setCurrentIndex(idx)
                    
                    # Restore location combos if possible
                    country = data.get("country", "")
                    if country:
                        idx = self.cboCountry.findText(country)
                        if idx >= 0:
                            self.cboCountry.setCurrentIndex(idx)
                            self.on_country_changed(country)
                    
                    state = data.get("state", "")
                    if state and self.cboState.count() > 0:
                        idx = self.cboState.findText(state)
                        if idx >= 0:
                            self.cboState.setCurrentIndex(idx)
                            self.on_state_changed(state)
                    
                    city = data.get("city", "")
                    if city and self.cboCity.count() > 0:
                        idx = self.cboCity.findText(city)
                        if idx >= 0:
                            self.cboCity.setCurrentIndex(idx)
                    
                    # Latitude/Longitude
                    lat = data.get("lat", "")
                    lon = data.get("lon", "")
                    if lat:
                        self.txtLat.setText(lat)
                    if lon:
                        self.txtLon.setText(lon)
                    
                    # Ayanamsa
                    aya = data.get("ayanamsa", "")
                    if aya:
                        idx = self.cboAyana.findText(aya)
                        if idx >= 0:
                            self.cboAyana.setCurrentIndex(idx)
                    
                    # House system
                    house = data.get("house_system", "")
                    if house:
                        idx = self.cboHouseSys.findText(house)
                        if idx >= 0:
                            self.cboHouseSys.setCurrentIndex(idx)
                    
                    # Set all-cities combo if city found
                    if city:
                        idx_all = self.cboAllCities.findText(city)
                        if idx_all >= 0:
                            self.cboAllCities.setCurrentIndex(idx_all)

                    dialog.accept()
                    # Recalculate chart
                    self.calculate_chart()
                    self.statusbar.showMessage(f"Loaded chart: {name}")
                else:
                    QMessageBox.warning(dialog, "Error", "Chart data not found.")
            else:
                QMessageBox.warning(dialog, "Warning", "Please select a chart.")

        btn_open.clicked.connect(on_open)
        btn_cancel.clicked.connect(dialog.reject)

        dialog.exec_()

    def load_chart_from_line(self, lines):
        """Load chart data from file lines (simple implementation)"""
        # This is a placeholder - implement full parsing as needed
        for line in lines:
            if line.startswith("Name:"):
                name = line.split(":",1)[1].strip()
                self.txtName.setText(name)
            elif line.startswith("Date:"):
                date_str = line.split(":",1)[1].strip()
                # Parse date
                pass
            # etc.
        # After loading, trigger calculation
        self.calculate_chart()

    # ==================== DASA METHODS ====================

    def on_dasa_level_changed(self, level, data):
        level_names = {1: "မဟာဒဿာ", 2: "အန္တရဒဿာ", 3: "ပြတန္တရဒဿာ"}
        if level == 1:
            name = data.get('name', '')
            self.statusbar.showMessage(f"{level_names[level]}: {name}")
        elif level == 2:
            antar = data.get('antar', '')
            self.statusbar.showMessage(f"{level_names[level]}: {antar}")
        elif level == 3:
            praya = data.get('praya', '')
            self.statusbar.showMessage(f"{level_names[level]}: {praya}")

    def on_dasa_period_selected(self, period_data):
        period_type = period_data.get('type', '')
        if period_type == 'maha':
            name = period_data.get('name', '')
            data = period_data.get('data', {})
            start = data.get('startDate', '')[:10]
            end = data.get('endDate', '')[:10]
            duration = data.get('duration', '')
            msg = f"{name} မဟာဒဿာ: {start} မှ {end} အထိ ({duration})"
            self.statusbar.showMessage(msg)
        elif period_type == 'antar':
            maha = period_data.get('maha', '')
            antar = period_data.get('antar', '')
            msg = f"{maha}-{antar} အန္တရဒဿာ"
            self.statusbar.showMessage(msg)
        elif period_type == 'praya':
            maha = period_data.get('maha', '')
            antar = period_data.get('antar', '')
            praya = period_data.get('praya', '')
            msg = f"{maha}-{antar}-{praya} ပြတန္တရဒဿာ"
            self.statusbar.showMessage(msg)

    def calculate_full_vimshottari_dasa(self, moon_longitude, birth_dt):
        """
        Calculate Vimshottari Dasha with all three levels.
        Returns (mahadashas, antardashas, prayantardashas)
        """
        # Constants
        dasa_years = {
            'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10,
            'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
        }
        dasa_order = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars',
                    'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        total_cycle = 120.0

        # Nakshatra info
        nakshatra_deg = 360.0 / 27.0
        nakshatra_idx = int(moon_longitude // nakshatra_deg) % 27
        passed_frac = (moon_longitude % nakshatra_deg) / nakshatra_deg

        # First Mahadasha lord
        first_lord = dasa_order[nakshatra_idx % 9]
        first_index = dasa_order.index(first_lord)

        # Build Mahadasha list (circular order starting from first_lord)
        maha_lords = dasa_order[first_index:] + dasa_order[:first_index]

        mahadashas = {}
        antardashas = {}
        prayantardashas = {}

        # Helper to compute duration in days from years
        def years_to_days(y):
            return y * 365.25

        current_start = birth_dt
        now = datetime.now()

        # ----- Mahadasha Level -----
        for i, m_lord in enumerate(maha_lords):
            full_years = dasa_years[m_lord]
            # First Mahadasha may be partial
            if i == 0:
                years = full_years * (1 - passed_frac)
            else:
                years = full_years

            duration_days = years_to_days(years)
            current_end = current_start + timedelta(days=duration_days)

            mahadashas[m_lord] = {
                'start': current_start,
                'end': current_end,
                'startDate': current_start.strftime('%Y-%m-%d'),
                'endDate': current_end.strftime('%Y-%m-%d'),
                'duration': years,
                'is_current': current_start <= now <= current_end
            }

            # ----- Antardasha Level inside this Mahadasha -----
            # Antardashas are in the same order starting from the Mahadasha lord
            antar_lords = dasa_order[dasa_order.index(m_lord):] + dasa_order[:dasa_order.index(m_lord)]
            antar_start = current_start

            for j, a_lord in enumerate(antar_lords):
                # Full Antardasha duration in years
                antar_full_years = (full_years * dasa_years[a_lord]) / total_cycle
                if i == 0 and j == 0:
                    # First Antardasha of the first Mahadasha is also partial
                    antar_years = antar_full_years * (1 - passed_frac)
                else:
                    antar_years = antar_full_years

                antar_duration_days = years_to_days(antar_years)
                antar_end = antar_start + timedelta(days=antar_duration_days)

                key = f"{m_lord}-{a_lord}"
                antardashas[key] = {
                    'lord': a_lord,
                    'start': antar_start,
                    'end': antar_end,
                    'startDate': antar_start.strftime('%Y-%m-%d'),
                    'endDate': antar_end.strftime('%Y-%m-%d'),
                    'duration': antar_years,
                    'is_current': antar_start <= now <= antar_end
                }

                # ----- Prayantardasha Level inside this Antardasha -----
                praya_lords = dasa_order[dasa_order.index(a_lord):] + dasa_order[:dasa_order.index(a_lord)]
                praya_start = antar_start

                for k, p_lord in enumerate(praya_lords):
                    # Full Prayantardasha duration in years
                    praya_full_years = (full_years * dasa_years[a_lord] * dasa_years[p_lord]) / (total_cycle * total_cycle)
                    if i == 0 and j == 0 and k == 0:
                        praya_years = praya_full_years * (1 - passed_frac)
                    else:
                        praya_years = praya_full_years

                    praya_duration_days = years_to_days(praya_years)
                    praya_end = praya_start + timedelta(days=praya_duration_days)

                    p_key = f"{m_lord}-{a_lord}-{p_lord}"
                    prayantardashas[p_key] = {
                        'lord': p_lord,
                        'start': praya_start,
                        'end': praya_end,
                        'startDate': praya_start.strftime('%Y-%m-%d'),
                        'endDate': praya_end.strftime('%Y-%m-%d'),
                        'duration': praya_years,
                        'is_current': praya_start <= now <= praya_end
                    }

                    praya_start = praya_end

                antar_start = antar_end

            current_start = current_end

        return mahadashas, antardashas, prayantardashas

    def previous_chart(self):
        """Go to previous chart"""
        current_index = self.cboCheckable.currentIndex()
        if current_index > 0:
            self.cboCheckable.setCurrentIndex(current_index - 1)
        else:
            self.statusbar.showMessage("ပထမဆုံးဇာတာဖြစ်ပါသည်")

    def next_chart(self):
        """Go to next chart"""
        current_index = self.cboCheckable.currentIndex()
        if current_index < self.cboCheckable.count() - 1:
            self.cboCheckable.setCurrentIndex(current_index + 1)
        else:
            self.statusbar.showMessage("နောက်ဆုံးဇာတာဖြစ်ပါသည်")

    def on_chart_selected(self, index):
        """Handle chart selection"""
        if index >= 0:
            chart_name = self.cboCheckable.currentText()
            self.statusbar.showMessage(f"{chart_name} ဇာတာကို ရွေးချယ်ပြီးပါပြီ")

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>ဘရဏီ - ဗေဒင်ဇာတာတွက်စနစ်</h2>
        <p>ဗားရှင်း 1.10.0</p>
        <p>ဇာတာကို Swiss Ephemerisဖြင့် အကောင်းဆုံး တွက်ချက်သည်။</p>
        <p>အင်္ဂါရပ်များ:</p>
        <ul>
            <li>D1 မှ D60 အထိ ဝဂ္ဂဇာတာများ</li>
            <li>အာယနအမျိုးမျိုး ရွေးချယ်နိုင်</li>
            <li>ဘာဝခွဲစနစ်အမျိုးမျိုး</li>
            <li>မြန်မာလို ဇာတာဖော်ပြချက်</li>
        </ul>
        <p>© 2025 မူပိုင်ခွင့်လက်ဝယ်ရှိသည်။</p>
        """
        QMessageBox.about(self, "အကြောင်း", about_text)


if __name__ == "__main__":
    # Windows Taskbar Icon Fix
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('bharani.astrology.app')
    except Exception:
        pass

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    
    # App-level icon (for Taskbar)
    icon_path = resource_path("VediIcon.ico")
    
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    font = QFont("Pyidaungsu")
    font.setPointSize(10)
    app.setFont(font)
    
    window = BharaniApp()
    window.show()
    sys.exit(app.exec_())
