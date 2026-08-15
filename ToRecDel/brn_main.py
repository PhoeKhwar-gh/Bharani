# brn_main.py
import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QFileDialog, 
                             QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea)
from PyQt5.QtCore import QDate, QTime, Qt
from PyQt5 import QtGui

# Try to import brn_ui, show error if not found
try:
    from brn_ui import Ui_MainWindow
    print("Successfully imported brn_ui")
except ImportError as e:
    print(f"Error importing brn_ui: {e}")
    print("Make sure brn_ui.py is in the same directory")
    sys.exit(1)

from brn_calculator import ChartCalculator

class DataManager:
    def save_chart_data(self, file_path, data):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    def load_chart_data(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading file: {e}")
            return None

class ChartWidget(QWidget):
    def __init__(self, chart_data, chart_type="Rasi"):
        super().__init__()
        self.chart_data = chart_data
        self.chart_type = chart_type
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel(f"<h3>{self.chart_type} ဇယား</h3>")
        layout.addWidget(title)
        
        info = QLabel("ဇာတာဇယားကို ဒီနေရာမှာ ဆွဲပေးပါမည်။")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        self.setLayout(layout)
        self.setStyleSheet("border: 1px solid gray; padding: 10px;")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup UI from brn_ui.py
        self.setupUi(self)
        print("UI setup completed successfully")
        
        self.calculator = ChartCalculator()
        self.data_manager = DataManager()
        
        # Locations data
        self.locations = {
            "ရန်ကုန်": {"ရန်ကုန်": (16.8409, 96.1735)},
            "မန္တလေး": {"မန္တလေး": (21.9588, 96.0892)},
            "နေပြည်တော်": {"နေပြည်တော်": (19.7633, 96.0785)},
        }
        
        # Initialize UI components
        self.init_ui_components()
        self.setup_connections()
        
        self.statusbar.showMessage("ဇာတာအသစ်တစ်ခု တည်ဆောက်ရန် အသင့်ဖြစ်ပါပြီ။")
    
    def init_ui_components(self):
        """Initialize UI components with data"""
        # Check if UI components exist
        ui_components = [
            'cboState', 'cboCity', 'cboTimezone', 'cboCheckable',
            'cboDate', 'cboTime', 'txtLat', 'txtLon', 'txtName',
            'btnCalculate', 'btnNew', 'btnOpen', 'btnSave',
            'btnEditPlace', 'btnPreVal', 'btnNextVal',
            'cboAyana', 'cboHouseSys', 'chkDivision',
            'actionNew', 'actionOpen', 'actionSave', 'actionExit', 'actionAbout_Me'
        ]
        
        for comp in ui_components:
            if not hasattr(self, comp):
                print(f"Warning: UI component '{comp}' not found")
        
        # Populate states
        if hasattr(self, 'cboState'):
            self.cboState.addItems(self.locations.keys())
        
        # Populate timezone
        if hasattr(self, 'cboTimezone') and self.cboTimezone.count() == 0:
            timezones = [
                "UTC-12:00", "UTC-11:00", "UTC-10:00", "UTC-09:30", "UTC-09:00",
                "UTC-08:00", "UTC-07:00", "UTC-06:00", "UTC-05:00", "UTC-04:30",
                "UTC-04:00", "UTC-03:30", "UTC-03:00", "UTC-02:00", "UTC-01:00",
                "UTC±00:00", "UTC+01:00", "UTC+02:00", "UTC+03:00", "UTC+03:30",
                "UTC+04:00", "UTC+04:30", "UTC+05:00", "UTC+05:30", "UTC+05:45",
                "UTC+06:00", "UTC+06:30", "UTC+07:00", "UTC+08:00", "UTC+08:45",
                "UTC+09:00", "UTC+09:30", "UTC+10:00", "UTC+10:30", "UTC+11:00",
                "UTC+12:00", "UTC+12:45", "UTC+13:00", "UTC+14:00"
            ]
            self.cboTimezone.addItems(timezones)
            # Set Myanmar Time (UTC+6:30)
            index = self.cboTimezone.findText("UTC+06:30")
            if index >= 0:
                self.cboTimezone.setCurrentIndex(index)
        
        # Populate chart selection
        if hasattr(self, 'cboCheckable'):
            chart_list = [
                "Rasi (D1)", "Bhava", "Navamsa (D9)",
                "Hora (D2)", "Saptamsa (D7)", "Dasamsa (D10)",
                "Dwadasamsa (D12)", "Vimsamsa (D20)", "Trimsamsa (D30)",
                "Shashtiamsa (D60)"
            ]
            self.cboCheckable.addItems(chart_list)
        
        # Set default date and time
        if hasattr(self, 'cboDate'):
            self.cboDate.setDate(QDate.currentDate())
        if hasattr(self, 'cboTime'):
            self.cboTime.setTime(QTime(12, 0))
        
        # Trigger state changed to populate cities
        if hasattr(self, 'cboState'):
            self.on_state_changed(self.cboState.currentText())
    
    def setup_connections(self):
        """Setup signal connections"""
        # Button connections
        if hasattr(self, 'btnCalculate'):
            self.btnCalculate.clicked.connect(self.calculate_chart)
        if hasattr(self, 'btnNew'):
            self.btnNew.clicked.connect(self.new_chart)
        if hasattr(self, 'btnOpen'):
            self.btnOpen.clicked.connect(self.open_chart)
        if hasattr(self, 'btnSave'):
            self.btnSave.clicked.connect(self.save_chart)
        if hasattr(self, 'btnEditPlace'):
            self.btnEditPlace.clicked.connect(self.toggle_place_edit)
        if hasattr(self, 'btnPreVal'):
            self.btnPreVal.clicked.connect(self.previous_chart)
        if hasattr(self, 'btnNextVal'):
            self.btnNextVal.clicked.connect(self.next_chart)
        
        # Combo box connections
        if hasattr(self, 'cboState'):
            self.cboState.currentTextChanged.connect(self.on_state_changed)
        if hasattr(self, 'cboCity'):
            self.cboCity.currentTextChanged.connect(self.on_city_changed)
        if hasattr(self, 'cboCheckable'):
            self.cboCheckable.currentIndexChanged.connect(self.on_chart_selected)
        
        # Checkbox
        if hasattr(self, 'chkDivision'):
            self.chkDivision.stateChanged.connect(self.toggle_division_charts)
        
        # Menu connections
        if hasattr(self, 'actionNew'):
            self.actionNew.triggered.connect(self.new_chart)
        if hasattr(self, 'actionOpen'):
            self.actionOpen.triggered.connect(self.open_chart)
        if hasattr(self, 'actionSave'):
            self.actionSave.triggered.connect(self.save_chart)
        if hasattr(self, 'actionExit'):
            self.actionExit.triggered.connect(self.close)
        if hasattr(self, 'actionAbout_Me'):
            self.actionAbout_Me.triggered.connect(self.show_about_dialog)
    
    def on_state_changed(self, state):
        """Handle state selection change"""
        if hasattr(self, 'cboCity'):
            self.cboCity.clear()
            if state in self.locations:
                cities = list(self.locations[state].keys())
                self.cboCity.addItems(cities)
    
    def on_city_changed(self, city):
        """Handle city selection change"""
        state = self.cboState.currentText() if hasattr(self, 'cboState') else ""
        if state in self.locations and city in self.locations[state]:
            lat, lon = self.locations[state][city]
            if hasattr(self, 'txtLat'):
                self.txtLat.setText(str(lat))
            if hasattr(self, 'txtLon'):
                self.txtLon.setText(str(lon))
    
    def toggle_place_edit(self):
        """Toggle latitude/longitude edit mode"""
        if hasattr(self, 'txtLat') and hasattr(self, 'txtLon') and hasattr(self, 'btnEditPlace'):
            is_readonly = self.txtLat.isReadOnly()
            self.txtLat.setReadOnly(not is_readonly)
            self.txtLon.setReadOnly(not is_readonly)
            if is_readonly:
                self.btnEditPlace.setText("သိမ်း")
            else:
                self.btnEditPlace.setText("+/-")
    
    def previous_chart(self):
        """Navigate to previous chart"""
        if hasattr(self, 'cboCheckable'):
            current = self.cboCheckable.currentIndex()
            if current > 0:
                self.cboCheckable.setCurrentIndex(current - 1)
    
    def next_chart(self):
        """Navigate to next chart"""
        if hasattr(self, 'cboCheckable'):
            current = self.cboCheckable.currentIndex()
            if current < self.cboCheckable.count() - 1:
                self.cboCheckable.setCurrentIndex(current + 1)
    
    def on_chart_selected(self, index):
        """Handle chart selection"""
        if index >= 0 and hasattr(self, 'cboCheckable') and hasattr(self, 'statusbar'):
            chart_name = self.cboCheckable.currentText()
            self.statusbar.showMessage(f"{chart_name} ဇာတာကို ရွေးချယ်ပြီးပါပြီ")
    
    def toggle_division_charts(self, state):
        """Toggle division charts visibility"""
        # Implement if you have division charts container
        pass
    
    def calculate_chart(self):
        """Calculate chart"""
        QMessageBox.information(self, "သတင်း", "ဇာတာတွက်ချက်ခြင်း - လုပ်ဆောင်ဆဲ")
        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage("ဇာတာတွက်ချက်ပြီးပါပြီ")
    
    def new_chart(self):
        """Clear all data for new chart"""
        reply = QMessageBox.question(self, "ဇာတာအသစ်", 
                                    "လက်ရှိဒေတာများ ပျက်သွားပါမည်။ ဆက်လုပ်မည်မှာ သေချာပါသလား?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if hasattr(self, 'txtName'):
                self.txtName.clear()
            if hasattr(self, 'cboDate'):
                self.cboDate.setDate(QDate.currentDate())
            if hasattr(self, 'cboTime'):
                self.cboTime.setTime(QTime(12, 0))
            if hasattr(self, 'txtLat'):
                self.txtLat.clear()
            if hasattr(self, 'txtLon'):
                self.txtLon.clear()
            if hasattr(self, 'statusbar'):
                self.statusbar.showMessage("ဇာတာအသစ်အတွက် အဆင်သင့်ဖြစ်ပါပြီ")
    
    def open_chart(self):
        """Open chart file"""
        file_name, _ = QFileDialog.getOpenFileName(self, "ဇာတာဖိုင်ကို ဖွင့်ရန်", "", "JSON Files (*.json)")
        if file_name:
            chart_data = self.data_manager.load_chart_data(file_name)
            if chart_data and hasattr(self, 'txtName'):
                self.txtName.setText(chart_data.get("name", ""))
                # ... load other data ...
                if hasattr(self, 'statusbar'):
                    self.statusbar.showMessage(f"'{file_name}' ဖိုင်ကို ဖွင့်ပြီးပါပြီ")
    
    def save_chart(self):
        """Save chart data"""
        if not hasattr(self, 'txtName') or not self.txtName.text():
            QMessageBox.warning(self, "သတိပေးချက်", "အမည်ထည့်သွင်းပါ")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(self, "ဇာတာကို သိမ်းဆည်းရန်", "", "JSON Files (*.json)")
        if file_name:
            chart_data = {
                "name": self.txtName.text() if hasattr(self, 'txtName') else "",
                "date": self.cboDate.date().toString("yyyy-MM-dd") if hasattr(self, 'cboDate') else "",
                "time": self.cboTime.time().toString("HH:mm") if hasattr(self, 'cboTime') else "",
                "timezone": self.cboTimezone.currentText() if hasattr(self, 'cboTimezone') else "",
                "state": self.cboState.currentText() if hasattr(self, 'cboState') else "",
                "city": self.cboCity.currentText() if hasattr(self, 'cboCity') else "",
                "lat": self.txtLat.text() if hasattr(self, 'txtLat') else "",
                "lon": self.txtLon.text() if hasattr(self, 'txtLon') else "",
                "ayana": self.cboAyana.currentText() if hasattr(self, 'cboAyana') else "",
                "house_system": self.cboHouseSys.currentText() if hasattr(self, 'cboHouseSys') else ""
            }
            if self.data_manager.save_chart_data(file_name, chart_data) and hasattr(self, 'statusbar'):
                self.statusbar.showMessage(f"ဇာတာကို '{file_name}' ဖိုင်အဖြစ် သိမ်းဆည်းပြီးပါပြီ")
    
    def show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.about(self, "အကြောင်းကြားစာ", 
                         "Bharani Myanmar Astrology App\nVersion 1.0\n\nDeveloped with PyQt5.")

def main():
    app = QApplication(sys.argv)
    font = QtGui.QFont("Pyidaungsu", 10)
    app.setFont(font)
    
    print("Starting Bharani Myanmar Astrology...")
    window = MainWindow()
    window.show()
    print("Application started successfully")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()