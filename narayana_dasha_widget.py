# narayana_dasha_widget.py
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime

class NarayanaDashaWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.narayana_data = []
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("နာရာယဏဒဿာ (ရာသီအခြေပြု ဒဿာစနစ်)")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Pyidaungsu", 14, QFont.Bold))
        layout.addWidget(title)

        tables_layout = QtWidgets.QHBoxLayout()
        self._setup_table(tables_layout, "ရာသီဒဿာ", "maha")
        self._setup_table(tables_layout, "အန္တရဒဿာ", "antar")
        self._setup_table(tables_layout, "ပြတန္တရဒဿာ", "praya")
        layout.addLayout(tables_layout)

        self.status_label = QtWidgets.QLabel("ဇာတာတွက်ချက်ပါ။")
        self.status_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        layout.addWidget(self.status_label)

    def _setup_table(self, parent_layout, title, level):
        group = QtWidgets.QGroupBox(title)
        group.setFont(QFont("Pyidaungsu", 11, QFont.Bold))
        v_layout = QtWidgets.QVBoxLayout(group)
        
        table = QtWidgets.QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["ရာသီ", "စတင်ရက်", "ပြီးဆုံးရက်"])
        for i in range(3): table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget { gridline-color: #bdc3c7; background: white; }
            QHeaderView::section { background: #34495e; color: white; padding: 5px; font-weight: bold; }
        """)
        
        setattr(self, f"{level}_table", table)
        v_layout.addWidget(table)
        parent_layout.addWidget(group)

        if level == "maha": table.itemClicked.connect(self.on_maha_clicked)
        elif level == "antar": table.itemClicked.connect(self.on_antar_clicked)

    def set_data(self, data):
        self.narayana_data = data
        self._populate_maha()
        self.status_label.setText("✅ နာရာယဏဒဿာ တွက်ချက်ပြီးပါပြီ။")

    def _populate_maha(self):
        self.maha_table.setRowCount(0)
        for i, m in enumerate(self.narayana_data):
            self.maha_table.insertRow(i)
            self.maha_table.setItem(i, 0, QtWidgets.QTableWidgetItem(m['sign_name']))
            self.maha_table.setItem(i, 1, QtWidgets.QTableWidgetItem(m['start'].strftime("%Y-%m-%d")))
            self.maha_table.setItem(i, 2, QtWidgets.QTableWidgetItem(m['end'].strftime("%Y-%m-%d")))
            
            item = self.maha_table.item(i, 0)
            item.setData(Qt.UserRole, m)
            if m['start'] <= datetime.now() <= m['end']:
                item.setBackground(QColor(255, 215, 0, 150))
                item.setFont(QFont("Pyidaungsu", 11, QFont.Bold))

    def on_maha_clicked(self, item):
        row = item.row()
        data_item = self.maha_table.item(row, 0)
        if not data_item:
            return
        m = data_item.data(Qt.UserRole)
        if not m or 'antardashas' not in m:
            return
        self._populate_antar(m)
        self.praya_table.setRowCount(0)
        self.status_label.setText(f"🔍 {m['sign_name']} ရာသီဒဿာ ရွေးချယ်ထားသည်")

    def _populate_antar(self, maha_data):
        self.antar_table.setRowCount(0)
        if not maha_data or 'antardashas' not in maha_data:
            return
        for i, a in enumerate(maha_data['antardashas']):
            self.antar_table.insertRow(i)
            self.antar_table.setItem(i, 0, QtWidgets.QTableWidgetItem(a['sign_name']))
            self.antar_table.setItem(i, 1, QtWidgets.QTableWidgetItem(a['start'].strftime("%Y-%m-%d")))
            self.antar_table.setItem(i, 2, QtWidgets.QTableWidgetItem(a['end'].strftime("%Y-%m-%d")))
            item = self.antar_table.item(i, 0)
            item.setData(Qt.UserRole, a)
            if a['start'] <= datetime.now() <= a['end']:
                item.setBackground(QColor(144, 238, 144, 150))

    def on_antar_clicked(self, item):
        row = item.row()
        data_item = self.antar_table.item(row, 0)
        if not data_item:
            return
        a = data_item.data(Qt.UserRole)
        if not a:
            return
        self._populate_praya(a)
        self.status_label.setText(f"🔍 {a['sign_name']} အန္တရဒဿာ ရွေးချယ်ထားသည်")

    def _populate_praya(self, antar_data):
        self.praya_table.setRowCount(0)
        for i, p in enumerate(antar_data['pratyantardashas']):
            self.praya_table.insertRow(i)
            self.praya_table.setItem(i, 0, QtWidgets.QTableWidgetItem(p['sign_name']))
            self.praya_table.setItem(i, 1, QtWidgets.QTableWidgetItem(p['start'].strftime("%Y-%m-%d")))
            self.praya_table.setItem(i, 2, QtWidgets.QTableWidgetItem(p['end'].strftime("%Y-%m-%d")))
            if p['start'] <= datetime.now() <= p['end']:
                self.praya_table.item(i, 0).setBackground(QColor(173, 216, 230, 150))