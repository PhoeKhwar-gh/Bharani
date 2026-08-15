import sys
from collections import OrderedDict
from datetime import datetime, timedelta
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

class DasaCalculator:
    """ဝိသောတ္တရီဒသာ တွက်ချက်ခြင်း (Standalone)"""
    PLANET_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

    PLANET_YEARS = {
        'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10,
        'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
    }

    PLANET_NAMES_MM = {
        'Ketu': 'ကိတ်', 'Venus': 'သောကြာ', 'Sun': 'နေ', 'Moon': 'လ',
        'Mars': 'အင်္ဂါ', 'Rahu': 'ရာဟု',  'Jupiter': 'ကြာသပတေး',
        'Saturn': 'စနေ', 'Mercury': 'ဗုဒ္ဓဟူး'
    }

    @staticmethod
    def calculate_all_dashas(start_date, current_date=None, start_planet='Saturn'):
        """ဝိသောတ္တရီဒသာ အပြည့်အစုံ တွက်ချက်ခြင်း"""
        if current_date is None:
            current_date = datetime.now()
        
        start_index = DasaCalculator.PLANET_ORDER.index(start_planet)
        ordered_planets = DasaCalculator.PLANET_ORDER[start_index:] + DasaCalculator.PLANET_ORDER[:start_index]
        
        mahadashas = {}
        antardashas = {}
        prayantardashas = {}
        
        current_maha = None
        current_date_obj = start_date
        
        # ========== ၁. ထူလဒသာ ==========
        for i, planet in enumerate(ordered_planets):
            years = DasaCalculator.PLANET_YEARS[planet]
            days_to_add = int(years * 365.2422)
            end_date = current_date_obj + timedelta(days=days_to_add)
            
            is_current = (current_date_obj <= current_date < end_date)
            if is_current:
                current_maha = planet
            
            mahadashas[planet] = {
                'lord': planet,
                'name_mm': DasaCalculator.PLANET_NAMES_MM[planet],
                'duration_years': years,
                'start': current_date_obj,
                'end': end_date,
                'startDate': current_date_obj.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'is_current': is_current
            }
            current_date_obj = end_date
        
        # ========== ၂. အန္တရဒသာ (key format: "maha-antar") ==========
        for maha_planet, maha_data in mahadashas.items():
            maha_start = maha_data['start']
            maha_years = maha_data['duration_years']
            
            maha_index = DasaCalculator.PLANET_ORDER.index(maha_planet)
            antar_order = DasaCalculator.PLANET_ORDER[maha_index:] + DasaCalculator.PLANET_ORDER[:maha_index]
            
            antar_start = maha_start
            
            for antar_planet in antar_order:
                antar_years = (DasaCalculator.PLANET_YEARS[antar_planet] / 120.0) * maha_years
                antar_days = int(antar_years * 365.2422)
                antar_end = antar_start + timedelta(days=antar_days)
                
                key = f"{maha_planet}-{antar_planet}"
                antardashas[key] = {
                    'lord': antar_planet,
                    'name_mm': DasaCalculator.PLANET_NAMES_MM[antar_planet],
                    'maha_lord': maha_planet,
                    'duration_years': antar_years,
                    'start': antar_start,
                    'end': antar_end,
                    'startDate': antar_start.strftime('%Y-%m-%d'),
                    'endDate': antar_end.strftime('%Y-%m-%d')
                }
                antar_start = antar_end
        
        # ========== ၃. ပြတန္တရဒသာ (key format: "maha-antar-praya") ==========
        for antar_key, antar_data in antardashas.items():
            maha_planet = antar_data['maha_lord']
            antar_planet = antar_data['lord']
            antar_years = antar_data['duration_years']
            
            praya_index = DasaCalculator.PLANET_ORDER.index(antar_planet)
            praya_order = DasaCalculator.PLANET_ORDER[praya_index:] + DasaCalculator.PLANET_ORDER[:praya_index]
            
            praya_start = antar_data['start']
            
            for praya_planet in praya_order:
                praya_years = (DasaCalculator.PLANET_YEARS[praya_planet] / 120.0) * antar_years
                praya_days = max(1, int(praya_years * 365.2422))
                praya_end = praya_start + timedelta(days=praya_days)
                
                key = f"{maha_planet}-{antar_planet}-{praya_planet}"
                prayantardashas[key] = {
                    'lord': praya_planet,
                    'name_mm': DasaCalculator.PLANET_NAMES_MM[praya_planet],
                    'maha_lord': maha_planet,
                    'antar_lord': antar_planet,
                    'duration_years': praya_years,
                    'start': praya_start,
                    'end': praya_end,
                    'startDate': praya_start.strftime('%Y-%m-%d'),
                    'endDate': praya_end.strftime('%Y-%m-%d')
                }
                praya_start = praya_end
        
        return mahadashas, antardashas, prayantardashas, current_maha


class DasaTableWidget(QtWidgets.QWidget):
    level_changed = pyqtSignal(int, dict)
    period_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setMinimumHeight(450)
        self.setMaximumHeight(600)
        
        self.mahadashas = {}
        self.antardashas = {}
        self.prayantardashas = {}
        self.current_maha = None
        self.current_antar = None
        
        self.planet_names_mm = DasaCalculator.PLANET_NAMES_MM
        self.planet_order = DasaCalculator.PLANET_ORDER
         
        self.selected_maha = None
        self.selected_antar = None
        self.current_path = []
        
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        title_label = QtWidgets.QLabel("ဝိသောတ္တရီဒသာ (Vimshottari Dasha)")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Pyidaungsu", 16, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #8B4513;
                padding: 5px;
                background-color: #FDF5E6;
                border-bottom: 2px solid #DEB887;
            }
        """)
        main_layout.addWidget(title_label)
        
        tables_layout = QtWidgets.QHBoxLayout()
        tables_layout.setSpacing(5)
        tables_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setup_mahadasha_table(tables_layout)
        self.setup_antardasha_table(tables_layout)
        self.setup_prayantardasha_table(tables_layout)
        
        main_layout.addLayout(tables_layout)
        self.setup_status_bar(main_layout)

    def setup_mahadasha_table(self, parent_layout):
        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("""
            QGroupBox { 
                background-color: #FFF8E7; 
                border: 2px solid #CD853F; 
                border-radius: 8px; 
                margin-top: 0px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group_box)
        layout.setContentsMargins(5, 5, 5, 5)
        
        table_title = QtWidgets.QLabel("ထူလဒသာ (Mahadasha)")
        table_title.setAlignment(Qt.AlignCenter)
        table_title.setFont(QFont("Pyidaungsu", 13, QFont.Bold))
        table_title.setStyleSheet("color: #8B4513; padding: 5px; background-color: #FFF8E7;")
        layout.addWidget(table_title)
        
        self.maha_table = QtWidgets.QTableWidget()
        self.maha_table.setColumnCount(3)
        self.maha_table.setHorizontalHeaderLabels(["ဂြိုဟ်", "စတင်ရက်", "ပြီးဆုံးရက်"])
        self.maha_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.maha_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.maha_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.maha_table.setAlternatingRowColors(True)
        self.maha_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.maha_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.maha_table.setFont(QFont("Pyidaungsu", 12))
        self.maha_table.setStyleSheet("""
            QTableWidget { gridline-color: #D2B48C; selection-background-color: #CD853F; font-size: 12pt; }
            QHeaderView::section { background-color: #8B4513; color: white; padding: 5px; font-size: 12pt; }
        """)
        
        # ✅ Widget ဖန်တီးပြီးမှ အရွယ်အစား သတ်မှတ်
        self.maha_table.verticalScrollBar().setEnabled(False)
        self.maha_table.setMinimumHeight(420)
        self.maha_table.setMaximumHeight(460)
            
        self.maha_table.itemClicked.connect(self.on_maha_clicked)
        layout.addWidget(self.maha_table)
        parent_layout.addWidget(group_box)

    def setup_antardasha_table(self, parent_layout):
        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("""
            QGroupBox { 
                background-color: #FFF8E7; 
                border: 2px solid #B8860B; 
                border-radius: 8px; 
                margin-top: 0px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group_box)
        layout.setContentsMargins(5, 5, 5, 5)
        
        table_title = QtWidgets.QLabel("အန္တရဒသာ (Antardasha)")
        table_title.setAlignment(Qt.AlignCenter)
        table_title.setFont(QFont("Pyidaungsu", 13, QFont.Bold))
        table_title.setStyleSheet("color: #8B4513; padding: 5px; background-color: #FFF8E7;")
        layout.addWidget(table_title)
        
        # ✅ Widget ကို ဦးစွာဖန်တီးပါ
        self.antar_table = QtWidgets.QTableWidget()
        self.antar_table.setColumnCount(3)
        self.antar_table.setHorizontalHeaderLabels(["ဂြိုဟ်", "စတင်ရက်", "ပြီးဆုံးရက်"])
        self.antar_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.antar_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.antar_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.antar_table.setAlternatingRowColors(True)
        self.antar_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.antar_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.antar_table.setFont(QFont("Pyidaungsu", 12))
        self.antar_table.setStyleSheet(self.maha_table.styleSheet())
        
        # ✅ ဖန်တီးပြီးမှ အရွယ်အစား သတ်မှတ်ခြင်း (AttributeError ဖြေရှင်းပြီး)
        self.antar_table.verticalScrollBar().setEnabled(False)
        self.antar_table.setMinimumHeight(420)
        self.antar_table.setMaximumHeight(460)
        
        self.antar_table.itemClicked.connect(self.on_antar_clicked)
        layout.addWidget(self.antar_table) 
        parent_layout.addWidget(group_box)

    def setup_prayantardasha_table(self, parent_layout):
        group_box = QtWidgets.QGroupBox()
        group_box.setStyleSheet("""
            QGroupBox { 
                background-color: #FFF8E7; 
                border: 2px solid #DAA520; 
                border-radius: 8px; 
                margin-top: 0px;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group_box)
        layout.setContentsMargins(5, 5, 5, 5)
        
        table_title = QtWidgets.QLabel("ပြတန္တရဒသာ (Prayantardasha)")
        table_title.setAlignment(Qt.AlignCenter)
        table_title.setFont(QFont("Pyidaungsu", 13, QFont.Bold))
        table_title.setStyleSheet("color: #8B4513; padding: 5px; background-color: #FFF8E7;")
        layout.addWidget(table_title)
        
        # ✅ Widget ကို ဦးစွာဖန်တီးပါ
        self.praya_table = QtWidgets.QTableWidget()
        self.praya_table.setColumnCount(3)
        self.praya_table.setHorizontalHeaderLabels(["ဂြိုဟ်", "စတင်ရက်", "ပြီးဆုံးရက်"])
        self.praya_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.praya_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.praya_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.praya_table.setAlternatingRowColors(True)
        self.praya_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.praya_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.praya_table.setFont(QFont("Pyidaungsu", 12))
        self.praya_table.setStyleSheet(self.maha_table.styleSheet())
        
        # ✅ ဖန်တီးပြီးမှ အရွယ်အစား သတ်မှတ်ခြင်း (AttributeError ဖြေရှင်းပြီး)
        self.praya_table.verticalScrollBar().setEnabled(False)
        self.praya_table.setMinimumHeight(420)
        self.praya_table.setMaximumHeight(460)
        
        self.praya_table.itemClicked.connect(self.on_praya_clicked)
        layout.addWidget(self.praya_table) 
        parent_layout.addWidget(group_box)

    def setup_status_bar(self, parent_layout):
        status_layout = QtWidgets.QHBoxLayout()
        status_layout.setContentsMargins(5, 5, 5, 5)
         
        self.status_label = QtWidgets.QLabel("✓ အဆင်သင့်")
        self.status_label.setFont(QFont("Pyidaungsu", 12))
        self.status_label.setStyleSheet("""
            QLabel { color: #27ae60; padding: 5px; background-color: #FDF5E6; border-radius: 3px; }
        """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        parent_layout.addLayout(status_layout)

    # ==================== ဒသာတွက်ချက်ခြင်း ====================
    def calculate_dasa(self, birth_date, start_planet='Saturn'):
        """မွေးနေ့မှစတင်ကာ ဝိသောတ္တရီဒသာ တွက်ချက်ခြင်း"""
        try:
            mahadashas, antardashas, prayantardashas, current_maha = \
                DasaCalculator.calculate_all_dashas(birth_date, None, start_planet)
            
            self.set_dasa_data(mahadashas, antardashas, prayantardashas, current_maha)
            
            print(f"DEBUG: Mahadashas = {list(mahadashas.keys())}")
            print(f"DEBUG: Antardashas count = {len(antardashas)}")
            print(f"DEBUG: Prayantardashas count = {len(prayantardashas)}")
            
            self.update_status(f"ဒသာတွက်ချက်ပြီးပါပြီ - လက်ရှိထူလဒသာ: {self.planet_names_mm.get(current_maha, current_maha)}")
            return True
            
        except Exception as e:
            self.update_status(f"တွက်ချက်မှုအမှား: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def set_dasa_data(self, mahadashas, antardashas, prayantardashas, current_maha=None):
        """ဒသာဒေတာများကို ဇယားတွင်ထည့်သွင်းခြင်း"""
        self.mahadashas = mahadashas or {}
        self.antardashas = antardashas or {}
        self.prayantardashas = prayantardashas or {}
        self.current_maha = current_maha
        self.current_antar = None
        self.selected_maha = None
        self.selected_antar = None
        
        self.current_path = []
        self.update_status_path()
        
        self.populate_mahadasha_table()
        self.antar_table.setRowCount(0)
        self.praya_table.setRowCount(0)

    # ==================== ထူလဒသာ ====================
    def populate_mahadasha_table(self):
        """ထူလဒသာဇယား ဖြည့်သွင်းခြင်း - မွေးဖွားချိန်မှ စတင်သော အစီအစဉ်အတိုင်း"""
        self.maha_table.setRowCount(0)
        
        if not self.mahadashas:
            self.maha_table.setRowCount(1)
            empty_item = QtWidgets.QTableWidgetItem("ဒသာဒေတာ မရှိပါ")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setFont(QFont("Pyidaungsu", 12))
            self.maha_table.setItem(0, 0, empty_item)
            self.maha_table.setSpan(0, 0, 1, 3)
            return
        
        count = 0
        for planet, data in self.mahadashas.items():
            if count >= 9:
                break
            
            row = self.maha_table.rowCount()
            self.maha_table.insertRow(row)
            
            display_name = data.get('name_mm', planet)
            name_item = QtWidgets.QTableWidgetItem(display_name)
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setFont(QFont("Pyidaungsu", 12))
            
            if planet == self.current_maha:
                name_item.setBackground(QColor(255, 215, 0, 150))
                name_item.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
            
            name_item.setData(Qt.UserRole, {
                'type': 'maha',
                'name': planet,
                'name_mm': display_name,
                'data': data
            })
            self.maha_table.setItem(row, 0, name_item)
            
            start_str = data.get('startDate', '')[:10]
            end_str = data.get('endDate', '')[:10]
             
            start_item = QtWidgets.QTableWidgetItem(start_str)
            end_item = QtWidgets.QTableWidgetItem(end_str)
            start_item.setFont(QFont("Pyidaungsu", 12))
            end_item.setFont(QFont("Pyidaungsu", 12))
            
            self.maha_table.setItem(row, 1, start_item)
            self.maha_table.setItem(row, 2, end_item)
            
            count += 1

    def on_maha_clicked(self, item):
        """ထူလဒသာ နှိပ်ပါက အန္တရဒသာများ ပြသမည်"""
        row = item.row()
        name_item = self.maha_table.item(row, 0)
        if name_item:
            data = name_item.data(Qt.UserRole)
            if data and data.get('type') == 'maha':
                self.selected_maha = data['name']
                
                self.current_path = [data['name_mm']]
                self.update_status_path() 
                
                print(f"DEBUG: Selected Maha = {data['name']}")
                
                self.populate_antardasha_table(data['name'])
                self.praya_table.setRowCount(0)
                self.period_selected.emit(data)
                self.level_changed.emit(1, data)

    # ==================== အန္တရဒသာ ====================
    def populate_antardasha_table(self, maha_name):
        """ရွေးချယ်ထားသော ထူလဒသာအတွက် အန္တရဒသာဇယားဖြည့်ခြင်း"""
        self.antar_table.setRowCount(0)
        
        print(f"DEBUG: Looking for Antardashas with key prefix '{maha_name}-'")
        print(f"DEBUG: Total antardashas = {len(self.antardashas)}")
        
        antar_list = []
        for key, data in self.antardashas.items():
            if key.startswith(f"{maha_name}-"):
                antar_list.append((data.get('startDate', ''), key, data['lord'], data))
                print(f"DEBUG: Found Antar: {data['lord']} (key={key})")
        
        antar_list.sort(key=lambda x: x[0])
        
        row = 0
        for _, key, antar_lord, data in antar_list:
            self.antar_table.insertRow(row)
            display_name = data.get('name_mm', antar_lord)
            name_item = QtWidgets.QTableWidgetItem(display_name)
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setFont(QFont("Pyidaungsu", 12))
            
            name_item.setData(Qt.UserRole, {
                'type': 'antar',
                'maha': maha_name,
                'antar': antar_lord,
                'name_mm': display_name,
                'key': key,
                'data': data
            })
            self.antar_table.setItem(row, 0, name_item)
            
            start_str = data.get('startDate', '')[:10]
            end_str = data.get('endDate', '')[:10]
            start_item = QtWidgets.QTableWidgetItem(start_str)
            end_item = QtWidgets.QTableWidgetItem(end_str)
            start_item.setFont(QFont("Pyidaungsu", 12))
            end_item.setFont(QFont("Pyidaungsu", 12))
            
            self.antar_table.setItem(row, 1, start_item)
            self.antar_table.setItem(row, 2, end_item)
            row += 1
        
        if row == 0:
            self.antar_table.setRowCount(1)
            empty_item = QtWidgets.QTableWidgetItem("အန္တရဒသာ မရှိပါ")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setFont(QFont("Pyidaungsu", 12))
            self.antar_table.setItem(0, 0, empty_item)
            self.antar_table.setSpan(0, 0, 1, 3)
            self.update_status(f"{maha_name} ထူလဒသာအတွင်း အန္တရဒသာ မရှိပါ")
        else:
            self.update_status(f"{self.planet_names_mm.get(maha_name, maha_name)} ထူလဒသာအတွင်း အန္တရဒသာ {row} ခု")

    def on_antar_clicked(self, item):
        """အန္တရဒသာ နှိပ်ပါက ပြတန္တရဒသာများ ပြသမည်"""
        row = item.row()
        name_item = self.antar_table.item(row, 0)
        if name_item:
            data = name_item.data(Qt.UserRole)
            if data and data.get('type') == 'antar':
                self.selected_antar = data['antar']
                
                if len(self.current_path) >= 1:
                    self.current_path = self.current_path[:1] + [data['name_mm']]
                else:
                    self.current_path = [self.selected_maha or '', data['name_mm']]
                self.update_status_path()
                
                self.populate_prayantardasha_table(data['maha'], data['antar'])
                self.period_selected.emit(data)
                self.level_changed.emit(2, data)

    # ==================== ပြတန္တရဒသာ ====================
    def populate_prayantardasha_table(self, maha_name, antar_name):
        """ရွေးချယ်ထားသော အန္တရဒသာအတွက် ပြတန္တရဒသာဇယားဖြည့်ခြင်း"""
        self.praya_table.setRowCount(0)
        
        key_prefix = f"{maha_name}-{antar_name}-"
        print(f"DEBUG: Looking for Prayas with key prefix '{key_prefix}'")
        
        praya_list = []
        for key, data in self.prayantardashas.items():
            if key.startswith(key_prefix):
                praya_list.append((data.get('startDate', ''), key, data['lord'], data))
                print(f"DEBUG: Found Praya: {data['lord']}")
        
        praya_list.sort(key=lambda x: x[0])
        
        row = 0
        for _, key, praya_lord, data in praya_list:
            self.praya_table.insertRow(row)
            display_name = data.get('name_mm', praya_lord)
            name_item = QtWidgets.QTableWidgetItem(display_name)
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setFont(QFont("Pyidaungsu", 12))
            
            name_item.setData(Qt.UserRole, {
                'type': 'praya',
                'maha': maha_name,
                'antar': antar_name,
                'praya': praya_lord,
                'name_mm': display_name,
                'data': data
            })
            self.praya_table.setItem(row, 0, name_item)
            
            start_str = data.get('startDate', '')[:10]
            end_str = data.get('endDate', '')[:10]
            start_item = QtWidgets.QTableWidgetItem(start_str)
            end_item = QtWidgets.QTableWidgetItem(end_str)
            start_item.setFont(QFont("Pyidaungsu", 12))
            end_item.setFont(QFont("Pyidaungsu", 12))
            
            self.praya_table.setItem(row, 1, start_item)
            self.praya_table.setItem(row, 2, end_item)
            row += 1
        
        if row == 0:
            self.praya_table.setRowCount(1)
            empty_item = QtWidgets.QTableWidgetItem("ပြတန္တရဒသာ မရှိပါ")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setFont(QFont("Pyidaungsu", 12))
            self.praya_table.setItem(0, 0, empty_item)
            self.praya_table.setSpan(0, 0, 1, 3)
        else:
            print(f"DEBUG: Found {row} prayas for {key_prefix}")

    def on_praya_clicked(self, item):
        """ပြတန္တရဒသာ နှိပ်ပါက Signal ထုတ်မည်"""
        row = item.row()
        name_item = self.praya_table.item(row, 0)
        if name_item:
            data = name_item.data(Qt.UserRole)
            if data and data.get('type') == 'praya':
                if len(self.current_path) >= 2:
                    self.current_path = self.current_path[:2] + [data['name_mm']]
                else:
                    self.current_path.append(data['name_mm'])
                self.update_status_path()
                
                self.period_selected.emit(data)
                self.level_changed.emit(3, data)

    def update_status(self, message):
        self.status_label.setText(f"✓ {message}")

    def update_status_path(self):
        """ဒဿာလမ်းကြောင်းကို ဇယားအောက်ခြေ Status တွင် ပြသရန်"""
        if self.current_path:
            self.status_label.setText("  >  ".join(self.current_path))
        else:
            self.status_label.setText("✓ အဆင်သင့်")

    def clear(self):
        self.mahadashas = {}
        self.antardashas = {}
        self.prayantardashas = {}
        self.current_maha = None
        self.current_antar = None
        self.selected_maha = None
        self.selected_antar = None
        self.maha_table.setRowCount(0)
        self.antar_table.setRowCount(0)
        self.praya_table.setRowCount(0)
        self.update_status("ဒေတာရှင်းလင်းပြီးပါပြီ")