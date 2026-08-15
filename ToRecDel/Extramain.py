# main.py
import sys
import os
import csv
import math
from datetime import datetime, timedelta
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, 
                             QFileDialog, QTextEdit, QVBoxLayout, QWidget)
from PyQt5.QtCore import QDate, QTime, Qt
from PyQt5.QtGui import QFont
from Ui_mainApp import Ui_MainWindow
# from burmese_chart import BurmeseChartWidget  # ယာယီပိတ်ထားပါ


class BharaniApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Initialize variables
        self.location_data = defaultdict(list)
        self.current_chart_data = None
        self.chart_widget = None
        self.custom_locations = []  # ထည့်သွင်းထားသော နေရာသစ်များ
        
        # Set default date and time
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        
        # Latitude/Longitude fields ကို edit မလုပ်အောင် ပိတ်ပါ
        self.txtLat.setReadOnly(True)
        self.txtLon.setReadOnly(True)

        # === Load CSV Data ===
        self.load_location_data()

        # === Connect Signals ===
        self.setup_connections()
        
        # Setup display areas
        self.setup_display_widgets()
        
        # Status bar message
        self.statusbar.showMessage("ဇာတာတွက်ချက်ရန် အဆင်သင့်ဖြစ်ပါပြီ")

    def setup_display_widgets(self):
        """Setup display widgets for center and right panels"""
        
        # Center display area - ဇာတာပုံ နှင့် ရလဒ်များ
        self.center_widget = QWidget()
        center_layout = QVBoxLayout()
        
        # Create text widget for detailed results
        self.center_text = QTextEdit()
        self.center_text.setReadOnly(True)
        self.center_text.setFont(QFont("Pyidaungsu", 10))
        
        # Add widgets to center layout
        center_layout.addWidget(self.center_text)
        
        self.center_widget.setLayout(center_layout)
        self.scrollArea.setWidget(self.center_widget)
        
        # Right sidebar display - အသေးစိတ်အချက်အလက်များ
        self.sidebar_text = QTextEdit()
        self.sidebar_text.setReadOnly(True)
        self.sidebar_text.setFont(QFont("Pyidaungsu", 9))
        self.scrollArea_2.setWidget(self.sidebar_text)

    def setup_connections(self):
        """Setup all signal connections"""
        
        # Location combobox signals
        self.cboState.currentTextChanged.connect(self.on_state_changed)
        self.cboCity.currentTextChanged.connect(self.on_town_changed)
        
        # Calculate button
        self.btnCalculate.clicked.connect(self.calculate_chart)
        
        # Place edit button
        self.btnEditPlace.clicked.connect(self.toggle_place_edit)
        
        # Menu actions
        self.actionNew.triggered.connect(self.new_chart)
        self.actionOpen.triggered.connect(self.open_chart)
        self.actionSave.triggered.connect(self.save_chart)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionAbout_Me.triggered.connect(self.show_about)
        self.actionExit.triggered.connect(self.close)
        
        # တကယ်လို့ button တွေ မရှိရင် ဒီလိုသုံးပါ
        # self.previous_time() နဲ့ self.next_time() functions တွေကိုလည်း ယာယီဖယ်ရှားပါ

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
            
            # === Populate State ComboBox ===
            states = sorted(self.location_data.keys())
            self.cboState.clear()
            self.cboState.addItems(states)

            # Default selection: ပထမဆုံး state နှင့် မြို့ကို အလိုအလျောက်ရွေးပေးပါ
            if states:
                first_state = states[0]
                self.cboState.setCurrentText(first_state)
                towns = [item[0] for item in self.location_data[first_state]]
                self.cboCity.clear()
                self.cboCity.addItems(towns)
                if towns:
                    first_town = towns[0]
                    self.cboCity.setCurrentText(first_town)
                    # Lat/Lon ဖြည့်ပါ
                    for t, lat, lon in self.location_data[first_state]:
                        if t == first_town:
                            self.txtLat.setText(lat)
                            self.txtLon.setText(lon)
                            break
                        
        except FileNotFoundError:
            QMessageBox.warning(self, "ဖိုင်မတွေ့", "dataCSV.csv ဖိုင်မတွေ့ပါ။\nဖိုင်လမ်းကြောင်း: " + csv_path)
            # Create sample data
            self.create_sample_location_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dataCSV.csv:\n{str(e)}")

    def create_sample_location_data(self):
        """Create sample location data if CSV not found"""
        sample_data = {
            "ရန်ကုန်တိုင်း": [
                ("ရန်ကုန်", "16.8661", "96.1951"),
                ("မှော်ဘီ", "17.0333", "96.1333"),
                ("တွံတေး", "16.7167", "96.2333")
            ],
            "မန္တလေးတိုင်း": [
                ("မန္တလေး", "21.9588", "96.0891"),
                ("ကျောက်ဆည်", "21.6000", "96.1333"),
                ("မတ္တရာ", "22.2167", "96.1000")
            ],
            "ဧရာဝတီတိုင်း": [
                ("ပုသိမ်", "16.7739", "94.7331"),
                ("ဟင်္သာတ", "17.6333", "95.4667"),
                ("မြောင်းမြ", "16.5333", "94.7167")
            ]
        }
        
        self.location_data.update(sample_data)
        
        # Populate comboboxes
        states = sorted(self.location_data.keys())
        self.cboState.clear()
        self.cboState.addItems(states)
        
        if states:
            self.cboState.setCurrentText(states[0])
            self.on_state_changed(states[0])

    def on_state_changed(self, state):
        """State combobox ပြောင်းလဲတိုင်း မြို့ list ကို update လုပ်ပါ"""
        self.cboCity.clear()
        self.txtLat.clear()
        self.txtLon.clear()
        if state in self.location_data:
            towns = [item[0] for item in self.location_data[state]]
            self.cboCity.addItems(towns)
            if towns:
                self.cboCity.setCurrentIndex(0)

    def on_town_changed(self, town):
        """Town combobox ပြောင်းလဲတိုင်း latitude/longitude ကို update လုပ်ပါ"""
        state = self.cboState.currentText()
        if not state or not town:
            return
        for t, lat, lon in self.location_data[state]:
            if t == town:
                self.txtLat.setText(lat)
                self.txtLon.setText(lon)
                break

    def toggle_place_edit(self):
        """နေရာအသစ်ထည့်ရန်/ပြင်ရန် toggle"""
        is_readonly = self.txtLat.isReadOnly()
        self.txtLat.setReadOnly(not is_readonly)
        self.txtLon.setReadOnly(not is_readonly)
        
        if is_readonly:
            self.btnEditPlace.setText("Save")
            self.statusbar.showMessage("ကျေးလက်ဒေသများအတွက် မိမိကိုယ်တိုင် လတ္တီတွဒ်/လောင်ဂျီတွဒ် ထည့်သွင်းနိုင်ပါသည်")
        else:
            self.btnEditPlace.setText("+/-")
            # Save custom location
            lat = self.txtLat.text().strip()
            lon = self.txtLon.text().strip()
            state = self.cboState.currentText()
            town = self.cboCity.currentText()
            
            if lat and lon and state and town:
                self.save_custom_location(state, town, lat, lon)
                self.statusbar.showMessage(f"{town} ၏ ကိုဩဒိနိတ်များ သိမ်းဆည်းပြီး")

    def save_custom_location(self, state, town, lat, lon):
        """Save custom location to list"""
        location_info = {
            'state': state,
            'town': town,
            'lat': lat,
            'lon': lon,
            'custom': True
        }
        self.custom_locations.append(location_info)
        
        # Also add to current data for immediate use
        if state not in self.location_data:
            self.location_data[state] = []
        
        # Check if town already exists
        exists = False
        for i, (t, l, ln) in enumerate(self.location_data[state]):
            if t == town:
                self.location_data[state][i] = (town, lat, lon)
                exists = True
                break
        
        if not exists:
            self.location_data[state].append((town, lat, lon))
            self.location_data[state].sort(key=lambda x: x[0])  # Sort by town name

    def on_time_unit_changed(self, unit):
        """Time unit ပြောင်းလဲမှုကို လက်ခံခြင်း"""
        self.statusbar.showMessage(f"အချိန်ယူနစ်: {unit} သို့ ပြောင်းလဲပြီး")

    def previous_time(self):
        """Previous time button"""
        current_unit = self.comboBox_3.currentText()
        
        # Adjust date/time based on selected unit
        if current_unit == "Day":
            current_date = self.cboDate.date()
            self.cboDate.setDate(current_date.addDays(-1))
            self.statusbar.showMessage("တစ်ရက် နောက်ပြန်သွားပြီး")
        elif current_unit == "Month":
            current_date = self.cboDate.date()
            self.cboDate.setDate(current_date.addMonths(-1))
            self.statusbar.showMessage("တစ်လ နောက်ပြန်သွားပြီး")
        elif current_unit == "Year":
            current_date = self.cboDate.date()
            self.cboDate.setDate(current_date.addYears(-1))
            self.statusbar.showMessage("တစ်နှစ် နောက်ပြန်သွားပြီး")
        else:
            self.statusbar.showMessage(f"Previous {current_unit} - လုပ်ဆောင်ချက်")

    def next_time(self):
        """Next time button"""
        current_unit = self.comboBox_3.currentText()
        
        # Adjust date/time based on selected unit
        if current_unit == "Day":
            current_date = self.cboDate.date()
            self.cboDate.setDate(current_date.addDays(1))
            self.statusbar.showMessage("တစ်ရက် ရှေ့တိုးသွားပြီး")
        elif current_unit == "Month":
            current_date = self.cboDate.date()
            self.cboDate.setDate(current_date.addMonths(1))
            self.statusbar.showMessage("တစ်လ ရှေ့တိုးသွားပြီး")
        elif current_unit == "Year":
            current_date = self.cboDate.date()
            self.cboDate.setDate(current_date.addYears(1))
            self.statusbar.showMessage("တစ်နှစ် ရှေ့တိုးသွားပြီး")
        else:
            self.statusbar.showMessage(f"Next {current_unit} - လုပ်ဆောင်ချက်")

    def calculate_chart(self):
        """ဇာတာတွက်ချက်ပါ"""
        try:
            # Get input data
            name = self.txtName.text().strip()
            if not name:
                QMessageBox.warning(self, "အမည်ထည့်ရန်", "ကျေးဇူးပြု၍ အမည်ထည့်သွင်းပါ")
                self.txtName.setFocus()
                return

            # Get location coordinates
            lat_str = self.txtLat.text()
            lon_str = self.txtLon.text()
            
            if not lat_str or not lon_str:
                QMessageBox.warning(self, "တည်နေရာ", "ကျေးဇူးပြု၍ မြို့/ကျေးရွာ ရွေးချယ်ပါ")
                self.cboState.setFocus()
                return

            # Validate coordinates
            try:
                latitude = float(lat_str)
                longitude = float(lon_str)
            except ValueError:
                QMessageBox.warning(self, "တည်နေရာ အမှား", "လတ္တီတွဒ်/လောင်ဂျီတွဒ် မှားယွင်းနေပါသည်")
                self.txtLat.setFocus()
                return

            # Get date and time
            birth_date = self.cboDate.date()
            birth_time = self.cboTime.time()
            
            # Get selected systems
            ayana_system = self.cboAyana.currentText()
            house_system = self.cboHouseSys.currentText()
            
            # Get location info
            state = self.cboState.currentText()
            town = self.cboCity.currentText()
            
            # Display calculation info
            self.display_calculation_info(name, birth_date, birth_time, 
                                         latitude, longitude, state, town,
                                         ayana_system, house_system)
            
            # Update status
            self.statusbar.showMessage(f"{name} ၏ ဇာတာ တွက်ချက်ပြီးပါပြီ")
            
        except Exception as e:
            QMessageBox.critical(self, "တွက်ချက်မှု အမှား", f"တွက်ချက်မှု မအောင်မြင်ပါ:\n{str(e)}")

    def display_calculation_info(self, name, birth_date, birth_time, lat, lon, state, town, ayana, house):
        """Display calculation results"""
        
        # Format date and time
        date_str = birth_date.toString("dd.MM.yyyy")
        time_str = birth_time.toString("hh:mm AP")
        
        # Display in center text area
        result_text = f"""
{'='*50}
ဇာတာအချက်အလက်များ
{'='*50}

အမည်: {name}
မွေးနေ့: {date_str}
မွေးချိန်: {time_str}
တိုင်း/ပြည်နယ်: {state}
မြို့/ကျေးရွာ: {town}
လတ္တီတွဒ်: {lat:.6f}°N
လောင်ဂျီတွဒ်: {lon:.6f}°E
အာယန: {ayana}
ဘာဝခွဲစနစ်: {house}

{'='*50}
ဂြိုဟ်တည်နေရာများ (နမူနာ)
{'='*50}

လဂ်: ဓနု 8°47'
နေ: မိန် 7°24'
လ: မိန် 29°17'
အင်္ဂါ: မိန် 14°57'
ဗုဒ္ဓဟူး: မိန် 24°19'
ကြာသပတေး: ကုမ် 17°36' R
သောကြာ: မိန် 5°47'
စနေ: ကုမ် 0°07' R
ယူရေးနပ်စ်: ကုမ် 1°26'
နက်ပ်ကျွန်း: ကုမ် 1°23'
ပလူတို: ကုမ် 1°48' R

{'='*50}
ရာသီခွင်များ
{'='*50}

၁. မိဿ (Aries)
၂. ပြိဿ (Taurus)
၃. မေထုန် (Gemini)
၄. ကရကဋ် (Cancer)
၅. သိဟ် (Leo)
၆. ကန် (Virgo)
၇. တူ (Libra)
၈. ဗြိစ္ဆာ (Scorpio)
၉. ဓနု (Sagittarius)
၁၀. မကာရ (Capricorn)
၁၁. ကုမ် (Aquarius)
၁၂. မိန် (Pisces)

{'='*50}
မှတ်ချက်
{'='*50}

ဤသည်မှာ နမူနာတွက်ချက်မှု ရလဒ်များ ဖြစ်ပါသည်။
အပြည့်အစုံ တွက်ချက်မှုအတွက် Swiss Ephemeris ထည့်သွင်းရန် လိုအပ်ပါသည်။

ဇာတာတွက်ချက်ချိန်: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
"""
        
        self.center_text.setPlainText(result_text)
        
        # Display detailed info in sidebar
        sidebar_text = f"""
{'='*40}
အသေးစိတ် ဇာတာအချက်အလက်များ
{'='*40}

အမည်: {name}
မွေးသက္ကရာဇ်: {date_str} {time_str}
တည်နေရာ: {town}, {state}

ကိုဩဒိနိတ်:
- လတ္တီတွဒ်: {lat:.6f}°N
- လောင်ဂျီတွဒ်: {lon:.6f}°E

တွက်ချက်စနစ်များ:
- အာယန: {ayana}
- ဘာဝခွဲ: {house}
- အချိန်ဇုံ: မြန်မာစံတော်ချိန် (UTC+6:30)

ဇာတာအမျိုးအစား:
- နတ္ထိဇာတာ (ပြည့်စုံသော ဇာတာ)

လဂ်တွက်နည်း:
- လဂ်: ဒေသလဂ် (ဒေသကာလဖြတ်)
- အာယနမ်သ: {ayana} စနစ်အရ

ဘာဝအကြောင်း:
{house} စနစ်အရ တွက်ချက်ထားပါသည်။
ဘာဝများကို ရာသီခွင်များ၏ စတုရန်းအလိုက် ခွဲခြားထားပါသည်။

မှတ်ချက်:
- R = ဂြိုဟ်ပြန်သွား (Retrograde)
- ° = ဒီဂရီ
- ' = မိနစ်
"""
        
        self.sidebar_text.setPlainText(sidebar_text)

    def new_chart(self):
        """ဇာတာအသစ်စတင်ပါ"""
        self.txtName.clear()
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())
        self.center_text.clear()
        self.sidebar_text.clear()
        self.statusbar.showMessage("ဇာတာအသစ်အတွက် အဆင်သင့်ဖြစ်ပါပြီ")

    def open_chart(self):
        """ဇာတာဖိုင်ဖွင့်ပါ"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "ဇာတာဖိုင်ဖွင့်ရန်", 
            "", "Bharani Files (*.bhr);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.center_text.setPlainText(data)
                self.statusbar.showMessage(f"ဇာတာဖိုင်ဖွင့်ပြီး: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.warning(self, "ဖိုင်ဖွင့်မှု အမှား", f"ဖိုင်ဖွင့်၍မရပါ:\n{str(e)}")

    def save_chart(self):
        """ဇာတာသိမ်းဆည်းပါ"""
        if not self.txtName.text():
            QMessageBox.warning(self, "သိမ်းဆည်းမှု", "အရင်ဇာတာတွက်ချက်ပြီးမှ သိမ်းဆည်းနိုင်ပါသည်")
            return
            
        default_name = f"{self.txtName.text()}_{self.cboDate.date().toString('ddMMyyyy')}"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "ဇာတာသိမ်းဆည်းရန်",
            default_name, "Bharani Files (*.bhr);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Add .bhr extension if not present
                if not file_path.endswith('.bhr') and not file_path.endswith('.txt'):
                    file_path += '.bhr'
                
                # Save chart data
                chart_data = f"Bharani Horoscope Data\n"
                chart_data += f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
                chart_data += f"{'='*50}\n\n"
                chart_data += f"Name: {self.txtName.text()}\n"
                chart_data += f"Date of Birth: {self.cboDate.date().toString('dd.MM.yyyy')}\n"
                chart_data += f"Time of Birth: {self.cboTime.time().toString('hh:mm AP')}\n"
                chart_data += f"Location: {self.cboCity.currentText()}, {self.cboState.currentText()}\n"
                chart_data += f"Latitude: {self.txtLat.text()}, Longitude: {self.txtLon.text()}\n"
                chart_data += f"Ayanamsa: {self.cboAyana.currentText()}\n"
                chart_data += f"House System: {self.cboHouseSys.currentText()}\n\n"
                chart_data += f"{'='*50}\n\n"
                chart_data += self.center_text.toPlainText()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(chart_data)
                    
                self.statusbar.showMessage(f"ဇာတာသိမ်းဆည်းပြီး: {os.path.basename(file_path)}")
                QMessageBox.information(self, "သိမ်းဆည်းမှု", "ဇာတာဖိုင်သိမ်းဆည်းပြီးပါပြီ")
                
            except Exception as e:
                QMessageBox.warning(self, "သိမ်းဆည်းမှု အမှား", f"သိမ်းဆည်း၍မရပါ:\n{str(e)}")

    def open_settings(self):
        """Settings window ဖွင့်ပါ"""
        QMessageBox.information(self, "Settings", 
                              "Settings window ကို နောက်ထပ်ဗားရှင်းတွင် ထည့်သွင်းပါမည်။\n\n"
                              "လက်ရှိအင်္ဂါရပ်များ:\n"
                              "- မြန်မာဘာသာစကား\n"
                              "- မြို့ရွာများစာရင်း\n"
                              "- ဇာတာတွက်ချက်ခြင်း\n"
                              "- ဖိုင်သိမ်းဆည်းခြင်း")

    def show_about(self):
        """About window ပြပါ"""
        about_text = """
Bharani - မြန်မာဗေဒင်ဇာတာတွက်ချက်ဆော့ဖ်ဝဲ

Version 1.0
© 2026

အသုံးပြုနည်း:
1. ဇာတာပိုင်ရှင်အမည် ထည့်ပါ
2. မွေးနေ့၊ မွေးချိန် ရွေးပါ
3. တိုင်း/ပြည်နယ်နှင့် မြို့/ကျေးရွာ ရွေးပါ
4. အာယနနှင့် ဘာဝခွဲစနစ် ရွေးပါ
5. CALCULATE နှိပ်၍ ဇာတာတွက်ချက်ပါ

အားသာချက်များ:
- မြန်မာဘာသာစကား ပံ့ပိုးမှု
- မြန်မာနိုင်ငံ၏ မြို့ရွာအများစု ပါဝင်
- မြန်မာ့ဗေဒင်နည်းစနစ်များနှင့် ကိုက်ညီ
- ဇာတာဖိုင်သိမ်းဆည်းနိုင်ခြင်း

ဖွံ့ဖြိုးဆဲအင်္ဂါရပ်များ:
- Swiss Ephemeris တွက်ချက်မှု
- မြန်မာ့ဗေဒင်အရ အကောင်းအဆိုး ခွဲခြမ်းစိတ်ဖြာခြင်း
- ဇာတာပုံများ ထုတ်လုပ်ခြင်း
"""
        QMessageBox.about(self, "About Bharani App", about_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = app.font()
    font.setFamily("Pyidaungsu")
    font.setPointSize(10)
    app.setFont(font)

    window = BharaniApp()
    window.showMaximized()
    sys.exit(app.exec_())