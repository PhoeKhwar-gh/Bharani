"""
dasa_table.py
ဝိသောတ္တရီဒသာ - ထူလဒသာ၊ အန္တရဒသာ၊ ပြတန္တရဒသာ ဇယားများ
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush
from datetime import datetime


class DasaTableWidget(QtWidgets.QWidget):
    """ဝိသောတ္တရီဒသာ - ဘေးတိုက်ဇယား"""
    
    # Signals
    level_changed = pyqtSignal(int, dict)  # level, data
    period_selected = pyqtSignal(dict)      # period data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Size policy
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Expanding
        )
        self.setMinimumHeight(500)
        
        self.mahadashas = {}
        self.antardashas = {}
        self.prayantardashas = {}
        self.current_maha = None
        self.current_antar = None
        
        # ဂြိုဟ်အမည်များ (မြန်မာလို)
        self.planet_names_mm = {
            'Ketu': 'ကိတ်', 'Venus': 'သောကြာ', 'Sun': 'နေ',
            'Moon': 'လ', 'Mars': 'အင်္ဂါ', 'Rahu': 'ရာဟု',
            'Jupiter': 'ကြာသပတေး', 'Saturn': 'စနေ', 'Mercury': 'ဗုဒ္ဓဟူး'
        }
        
        # ဂြိုဟ်အစီအစဉ် (ဝိသောတ္တရီဒသာ အစီအစဉ်)
        self.planet_order = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        
        # ရွေးချယ်ထားသော ဒသာအုပ်စု
        self.selected_maha = None
        self.selected_antar = None
        
        self.init_ui()
    
    def init_ui(self):
        """UI ကို စတင်တည်ဆောက်ခြင်း"""
        # Main layout - margins ကို 0 ချထား
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== ခေါင်းစဉ် =====
        title_label = QtWidgets.QLabel("ဝိသောတ္တရီဒသာ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Pyidaungsu", 16, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #8B4513;
                padding: 10px;
                background-color: #FDF5E6;
                border-bottom: 2px solid #DEB887;
                margin: 0px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # ===== Horizontal Layout for Tables (၃ ခုညီညီခွဲ) =====
        tables_layout = QtWidgets.QHBoxLayout()
        tables_layout.setSpacing(10)
        tables_layout.setContentsMargins(5, 10, 5, 5)
        
        # ထူလဒသာ ဇယား (၁)
        self.setup_mahadasha_table(tables_layout)
        
        # အန္တရဒသာ ဇယား (၂)
        self.setup_antardasha_table(tables_layout)
        
        # ပြတန္တရဒသာ ဇယား (၃)
        self.setup_prayantardasha_table(tables_layout)
        
        main_layout.addLayout(tables_layout)
        
        # ===== အခြေအနေဘား =====
        self.setup_status_bar(main_layout)
    
    def setup_mahadasha_table(self, parent_layout):
        """ထူလဒသာ ဇယား တည်ဆောက်ခြင်း"""
        # Group Box
        group_box = QtWidgets.QGroupBox("ထူလဒသာ")
        group_box.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
        group_box.setStyleSheet("""
            
            QGroupBox {
                background-color: #FFF8E7;
                border: 2px solid #CD853F;
                border-radius: 8px;
                margin-top: 5px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #8B4513;
                background-color: #FFF8E7;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group_box)
        layout.setContentsMargins(5, 15, 5, 5)
        
        # Table
        self.maha_table = QtWidgets.QTableWidget()
        self.maha_table.setColumnCount(3)
        self.maha_table.setHorizontalHeaderLabels(["ဂြိုဟ်", "စတင်ရက်", "ပြီးဆုံးရက်"])
        
        # Column widths - အညီအမျှခွဲ
        self.maha_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.maha_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.maha_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        self.maha_table.setMinimumWidth(250)
        self.maha_table.setAlternatingRowColors(True)
        self.maha_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.maha_table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.maha_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        
        # Styling
        self.maha_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #D2B48C;
                selection-background-color: #CD853F;
                selection-color: white;
                border: 1px solid #DEB887;
                border-radius: 3px;
                font-size: 11px;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #CD853F;
                color: white;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #8B4513;
                color: white;
                padding: 5px;
                font-weight: bold;
                font-size: 11px;
                border: none;
            }
        """)
        
        self.maha_table.itemClicked.connect(self.on_maha_clicked)
        
        layout.addWidget(self.maha_table)
        parent_layout.addWidget(group_box)
    
    def setup_antardasha_table(self, parent_layout):
        """အန္တရဒသာ ဇယား တည်ဆောက်ခြင်း"""
        group_box = QtWidgets.QGroupBox("အန္တရဒသာ")
        group_box.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
        group_box.setStyleSheet("""
            QGroupBox {
                background-color: #FFF8E7;
                border: 2px solid #B8860B;
                border-radius: 8px;
                margin-top: 5px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #8B4513;
                background-color: #FFF8E7;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group_box)
        layout.setContentsMargins(5, 15, 5, 5)
        
        # Table
        self.antar_table = QtWidgets.QTableWidget()
        self.antar_table.setColumnCount(3)
        self.antar_table.setHorizontalHeaderLabels(["ဂြိုဟ်", "စတင်ရက်", "ပြီးဆုံးရက်"])
        
        # Column widths - အညီအမျှခွဲ
        self.antar_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.antar_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.antar_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        self.antar_table.setMinimumWidth(250)
        self.antar_table.setAlternatingRowColors(True)
        self.antar_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.antar_table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.antar_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.antar_table.setStyleSheet(self.maha_table.styleSheet())
        
        self.antar_table.itemClicked.connect(self.on_antar_clicked)
        
        layout.addWidget(self.antar_table)
        parent_layout.addWidget(group_box)
    
    def setup_prayantardasha_table(self, parent_layout):
        """ပြတန္တရဒသာ ဇယား တည်ဆောက်ခြင်း"""
        group_box = QtWidgets.QGroupBox("ပြတန္တရဒသာ")
        group_box.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
        group_box.setStyleSheet("""
            QGroupBox {
                background-color: #FFF8E7;
                border: 2px solid #DAA520;
                border-radius: 8px;
                margin-top: 5px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #8B4513;
                background-color: #FFF8E7;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(group_box)
        layout.setContentsMargins(5, 15, 5, 5)
        
        # Table
        self.praya_table = QtWidgets.QTableWidget()
        self.praya_table.setColumnCount(3)
        self.praya_table.setHorizontalHeaderLabels(["ဂြိုဟ်", "စတင်ရက်", "ပြီးဆုံးရက်"])
        
        # Column widths - အညီအမျှခွဲ
        self.praya_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.praya_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.praya_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        self.praya_table.setMinimumWidth(250)
        self.praya_table.setAlternatingRowColors(True)
        self.praya_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.praya_table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.praya_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.praya_table.setStyleSheet(self.maha_table.styleSheet())
        
        self.praya_table.itemClicked.connect(self.on_praya_clicked)
        
        layout.addWidget(self.praya_table)
        parent_layout.addWidget(group_box)
    
    def setup_status_bar(self, parent_layout):
        """အခြေအနေဘား တည်ဆောက်ခြင်း"""
        status_layout = QtWidgets.QHBoxLayout()
        status_layout.setContentsMargins(5, 5, 5, 5)
        
        self.status_label = QtWidgets.QLabel("✓ အဆင်သင့်")
        self.status_label.setFont(QFont("Pyidaungsu", 10))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                padding: 5px;
                background-color: #FDF5E6;
                border-radius: 3px;
                border: 1px solid #DEB887;
            }
        """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        parent_layout.addLayout(status_layout)
    
    
    def set_dasa_data(self, mahadashas, antardashas, prayantardashas):
        """ဒသာဒေတာအပြည့်အစုံ ထည့်သွင်းခြင်း"""
        print("=" * 50)
        print("DasaTableWidget.set_dasa_data called")
        print(f"Mahadashas received: {len(mahadashas)}")
        
        self.mahadashas = mahadashas
        self.antardashas = antardashas
        self.prayantardashas = prayantardashas
        
        # လက်ရှိဒသာ (စောင့်ရင်းဒသာ) ရှာဖွေခြင်း
        self.current_maha = None
        for name, data in mahadashas.items():
            if data.get('is_current', False):
                self.current_maha = name
                print(f"Current Mahadasha: {name}")
                break
        
        # Clear sub-tables if no data available
        if not antardashas:
            self.antar_table.setRowCount(1)
            empty_item = QtWidgets.QTableWidgetItem("အန္တရဒသာ မရှိပါ")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.antar_table.setItem(0, 0, empty_item)
            self.antar_table.setSpan(0, 0, 1, 3)
        
        if not prayantardashas:
            self.praya_table.setRowCount(1)
            empty_item = QtWidgets.QTableWidgetItem("ပြတန္တရဒသာ မရှိပါ")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.praya_table.setItem(0, 0, empty_item)
            self.praya_table.setSpan(0, 0, 1, 3)
        # ထူလဒသာ ဇယားဖြည့်
        self.populate_mahadasha_table()
        
        # Update status
        self.update_status("ဒသာဒေတာ ထည့်သွင်းပြီးပါပြီ")
        print("Dasa data set completed")
        print("=" * 50)
    
    def populate_mahadasha_table(self):
        """ထူလဒသာဇယား ဖြည့်သွင်းခြင်း - မွေးဖွားချိန်မှ စတင်သော အစီအစဉ်အတိုင်း ပြသမည်"""
        self.maha_table.setRowCount(0)

        # ✅ ပြင်ဆင်ချက်: Brnmain.py မှ ဒေတာထည့်သွင်းထားသော အစီအစဉ် (မွေးစမှ စတင်သော အစဉ်) 
        # အတိုင်း တိုက်ရိုက်ပြသပါမည်။ ဇယားအစီအစဉ် ပြောင်းလဲခြင်း မပြုတော့ပါ။
        for planet, data in self.mahadashas.items():
            row = self.maha_table.rowCount()
            self.maha_table.insertRow(row)

            display_name = self.planet_names_mm.get(planet, planet)
            name_item = QtWidgets.QTableWidgetItem(display_name)
            name_item.setTextAlignment(Qt.AlignCenter)

            # လက်ရှိဒဿာကို အရောင်ခွဲပြမည် (ဇယားအစီအစဉ် မရွှေ့ဘဲ မူလနေရာတွင်သာ Highlight ပြမည်)
            if data.get('is_current', False):
                name_item.setBackground(QColor(255, 215, 0, 150)) # ရွှေရောင်
                name_item.setFont(QFont("Pyidaungsu", 13, QFont.Bold))
                name_item.setToolTip("လက်ရှိ စောင့်ရင်းဒဿာ")

            name_item.setData(Qt.UserRole, {'type': 'maha', 'name': planet, 'data': data})
            self.maha_table.setItem(row, 0, name_item)

            # ရက်စွဲများ
            start_str = self.format_date_display(data.get('startDate', str(data.get('start', ''))[:10]))
            end_str = self.format_date_display(data.get('endDate', str(data.get('end', ''))[:10]))

            start_item = QtWidgets.QTableWidgetItem(start_str)
            start_item.setTextAlignment(Qt.AlignCenter)
            start_item.setFont(QFont("Pyidaungsu", 12))  # ✅ ဖောင့် 12 သို့ တိုးခြင်း
            
            end_item = QtWidgets.QTableWidgetItem(end_str)
            end_item.setTextAlignment(Qt.AlignCenter)
            end_item.setFont(QFont("Pyidaungsu", 12))  # ✅ ဖောင့် 12 သို့ တိုးခြင်း

            self.maha_table.setItem(row, 1, start_item)
            self.maha_table.setItem(row, 2, end_item)
    
    def format_date_display(self, date_str):
        """ရက်စွဲကို YYYY-MM-DD ပုံစံပြင်ဆင်ခြင်း"""
        if not date_str:
            return ""
        if len(date_str) >= 10:
            return date_str[:10]
        return date_str
    
    def on_maha_clicked(self, item):
        """ထူလဒသာ တစ်ခုခုကို နှိပ်လိုက်လျှင်"""
        row = item.row()
        name_item = self.maha_table.item(row, 0)
        
        if name_item:
            data = name_item.data(Qt.UserRole)
            if data and data['type'] == 'maha':
                maha_name = data['name']
                
                # ရွေးချယ်ထားသော ထူလဒသာကို သိမ်းဆည်း
                self.selected_maha = maha_name
                
                # အန္တရဒသာဇယားကို အပ်ဒိတ်လုပ်
                self.populate_antardasha_table(maha_name)
                
                # ပြတန္တရဒသာဇယားကို ရှင်းလင်း
                self.praya_table.setRowCount(0)
                
                # Signal ပို့ရန်
                self.period_selected.emit(data)
                self.level_changed.emit(1, data)
                
                # အခြေအနေဘား အပ်ဒိတ်
                display_name = self.planet_names_mm.get(maha_name, maha_name)
                self.update_status(f"{display_name} ထူလဒသာ ရွေးချယ်ထားသည်")
    
    def populate_antardasha_table(self, maha_name):
        """ရွေးချယ်ထားသော ထူလဒသာအတွက် အန္တရဒသာဇယား ဖြည့်သွင်းခြင်း"""
        self.antar_table.setRowCount(0)
        antar_list = []
        
        for key, data in self.antardashas.items():
            if key.startswith(f"{maha_name}-"):
                # ရက်စွဲအစဉ်လိုက် စီနိုင်ရန် startDate ကို အတူယူမည်
                antar_list.append((data.get('startDate', ''), key, data['lord'], data))

        # ✅ ကာလအစဉ်လိုက် (Chronological) အတိအကျ စီပေးခြင်း
        antar_list.sort(key=lambda x: x[0])

        for _, key, antar_lord, data in antar_list:
            row = self.antar_table.rowCount()
            self.antar_table.insertRow(row)
            
            display_name = self.planet_names_mm.get(antar_lord, antar_lord)
            name_item = QtWidgets.QTableWidgetItem(display_name)
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setData(Qt.UserRole, {
                'type': 'antar', 'maha': maha_name, 'antar': antar_lord, 'key': key, 'data': data
            })
            
            # လက်ရှိအန္တရဒသာ Highlight ပြခြင်း
            today = datetime.now().date()
            if 'startDate' in data:
                try:
                    start_date = datetime.strptime(data['startDate'][:10], "%Y-%m-%d").date()
                    end_date = datetime.strptime(data['endDate'][:10], "%Y-%m-%d").date()
                    if start_date <= today <= end_date:
                        name_item.setBackground(QColor(144, 238, 144, 150))
                        name_item.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
                        name_item.setToolTip("လက်ရှိအန္တရဒသာ")
                        self.current_antar = antar_lord
                except: pass
            
            self.antar_table.setItem(row, 0, name_item)
            
            start_str = self.format_date_display(data.get('startDate', str(data.get('start', ''))[:10]))
            end_str = self.format_date_display(data.get('endDate', str(data.get('end', ''))[:10]))
            self.antar_table.setItem(row, 1, QtWidgets.QTableWidgetItem(start_str))
            self.antar_table.setItem(row, 2, QtWidgets.QTableWidgetItem(end_str))
    
    def on_antar_clicked(self, item):
        """အန္တရဒသာ တစ်ခုခုကို နှိပ်လိုက်လျှင်"""
        row = item.row()
        name_item = self.antar_table.item(row, 0)
        
        if name_item:
            data = name_item.data(Qt.UserRole)
            if data and data['type'] == 'antar':
                maha_name = data['maha']
                antar_name = data['antar']
                
                # ရွေးချယ်ထားသော အန္တရဒသာကို သိမ်းဆည်း
                self.selected_antar = antar_name
                
                # ပြတန္တရဒသာဇယားကို အပ်ဒိတ်လုပ်
                self.populate_prayantardasha_table(maha_name, antar_name)
                
                # Signal ပို့ရန်
                self.period_selected.emit(data)
                self.level_changed.emit(2, data)
                
                # အခြေအနေဘား အပ်ဒိတ်
                maha_display = self.planet_names_mm.get(maha_name, maha_name)
                antar_display = self.planet_names_mm.get(antar_name, antar_name)
                self.update_status(f"{maha_display}-{antar_display} အန္တရဒသာ ရွေးချယ်ထားသည်")
    
    def populate_prayantardasha_table(self, maha_name, antar_name):
        """ပြတန္တရဒသာဇယား ဖြည့်သွင်းခြင်း"""
        self.praya_table.setRowCount(0)
        key_prefix = f"{maha_name}-{antar_name}-"
        praya_list = []
        
        for key, data in self.prayantardashas.items():
            if key.startswith(key_prefix):
                praya_list.append((data.get('startDate', ''), key, data['lord'], data))

        # ✅ ကာလအစဉ်လိုက် (Chronological) အတိအကျ စီပေးခြင်း
        praya_list.sort(key=lambda x: x[0])

        for _, key, praya_lord, data in praya_list:
            row = self.praya_table.rowCount()
            self.praya_table.insertRow(row)
            
            display_name = self.planet_names_mm.get(praya_lord, praya_lord)
            name_item = QtWidgets.QTableWidgetItem(display_name)
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setData(Qt.UserRole, {
                'type': 'praya', 'maha': maha_name, 'antar': antar_name, 'praya': praya_lord, 'data': data
            })
            
            # လက်ရှိပြတန္တရဒသာ Highlight ပြခြင်း
            today = datetime.now().date()
            if 'startDate' in data:
                try:
                    start_date = datetime.strptime(data['startDate'][:10], "%Y-%m-%d").date()
                    end_date = datetime.strptime(data['endDate'][:10], "%Y-%m-%d").date()
                    if start_date <= today <= end_date:
                        name_item.setBackground(QColor(173, 216, 230, 150))
                        name_item.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
                        name_item.setToolTip("လက်ရှိပြတန္တရဒသာ")
                except: pass
            
            self.praya_table.setItem(row, 0, name_item)
            
            start_str = self.format_date_display(data.get('startDate', str(data.get('start', ''))[:10]))
            end_str = self.format_date_display(data.get('endDate', str(data.get('end', ''))[:10]))
            self.praya_table.setItem(row, 1, QtWidgets.QTableWidgetItem(start_str))
            self.praya_table.setItem(row, 2, QtWidgets.QTableWidgetItem(end_str))
    
    def on_praya_clicked(self, item):
        """ပြတန္တရဒသာ တစ်ခုခုကို နှိပ်လိုက်လျှင်"""
        row = item.row()
        name_item = self.praya_table.item(row, 0)
        
        if name_item:
            data = name_item.data(Qt.UserRole)
            if data and data['type'] == 'praya':
                maha_name = data['maha']
                antar_name = data['antar']
                praya_name = data['praya']
                
                # Signal ပို့ရန်
                self.period_selected.emit(data)
                self.level_changed.emit(3, data)
                
                # အခြေအနေဘား အပ်ဒိတ်
                maha_display = self.planet_names_mm.get(maha_name, maha_name)
                antar_display = self.planet_names_mm.get(antar_name, antar_name)
                praya_display = self.planet_names_mm.get(praya_name, praya_name)
                self.update_status(f"{maha_display}-{antar_display}-{praya_display} ပြတန္တရဒသာ ရွေးချယ်ထားသည်")
    
    def update_status(self, message):
        """အခြေအနေဘား အပ်ဒိတ်လုပ်ခြင်း"""
        self.status_label.setText(f"✓ {message}")
    
    def clear(self):
        """ဒေတာအားလုံး ရှင်းလင်းခြင်း"""
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