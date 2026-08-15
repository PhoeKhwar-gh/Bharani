# kawzar_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QPushButton, QFrame, QHBoxLayout
from PyQt5.QtCore import QDateTime, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from chart_widget import BurmeseChartWidget
import swisseph as swe
import os
from datetime import datetime, timedelta

class KawzarWidget(QWidget):
    """
    ကောဇာဂြိုဟ်များအတွက် သီးသန့် Widget
    လက်ရှိအချိန်နှင့် နေရာအလိုက် ဂြိုဟ်တည်နေရာကို ပြသပေးသည်
    """
    now_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # === အခြေခံ Setup ===
        self.parent = parent
        self.current_datetime = QDateTime.currentDateTime()
        self.current_location = {
            'name': 'ရန်ကုန်',
            'lat': 16.8661,
            'lon': 96.1951
        }
        
        # === Widget အရွယ်အစား သတ်မှတ်ခြင်း ===
        self.setFixedSize(500, 700)
        
        # === Swisseph Path Setup ===
        ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
        if os.path.exists(ephe_path):
            swe.set_ephe_path(ephe_path)
        
        # === Main Widget Styling ===
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
            }
            QLabel {
                color: #2c3e50;
                padding: 3px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c638e;
            }
        """)
        
        # === Main Layout ===
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # === Header Section ===
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #3498db);
                border-radius: 10px;
            }
        """)
        self.header_frame.setFixedHeight(70)
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        self.lbl_title = QLabel("🔮 ကောဇာ ဂြိုဟ်တည်နေရာ")
        self.lbl_title.setFont(QFont("Pyidaungsu", 16, QFont.Bold))
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("color: white;")
        header_layout.addWidget(self.lbl_title)
        
        self.main_layout.addWidget(self.header_frame)
        
        # === Location & Time Info Card ===
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #dcdde1;
            }
        """)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(5, 5, 5, 5)
        info_layout.setSpacing(8)
        
        self.lbl_location = QLabel("📍 ရန်ကုန် (16.87°N, 96.20°E)")
        self.lbl_location.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
        self.lbl_location.setAlignment(Qt.AlignCenter)
        self.lbl_location.setStyleSheet("color: #2c3e50;")
        
        self.lbl_time = QLabel("🕐 ၀၁.၀၁.၂၀၂၄ ၁၂:၀၀:၀၀")
        self.lbl_time.setFont(QFont("Pyidaungsu", 11))
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setStyleSheet("color: #7f8c8d;")
        
        info_layout.addWidget(self.lbl_location)
        info_layout.addWidget(self.lbl_time)
        
        self.main_layout.addWidget(self.info_frame)
        
        # === Chart Widget Container ===
        self.chart_container = QFrame()
        self.chart_container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 2px solid #3498db;
            }
        """)
        chart_layout = QVBoxLayout(self.chart_container)
        chart_layout.setContentsMargins(5, 5, 5, 5)
        chart_layout.setAlignment(Qt.AlignCenter)
        
        self.chart_widget = BurmeseChartWidget()
        self.chart_widget.setFixedSize(420, 420)
        chart_layout.addWidget(self.chart_widget, alignment=Qt.AlignCenter)
        
        self.main_layout.addWidget(self.chart_container)
        
        # === Navigation Control Panel ===
        self.nav_frame = QFrame()
        self.nav_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #dcdde1;
            }
        """)
        nav_layout = QVBoxLayout(self.nav_frame)
        nav_layout.setContentsMargins(15, 12, 15, 12)
        nav_layout.setSpacing(10)
        
        # Step info label
        self.lbl_step = QLabel("📌 အဆင့်: ၁ မိနစ်")
        self.lbl_step.setFont(QFont("Pyidaungsu", 11, QFont.Bold))
        self.lbl_step.setAlignment(Qt.AlignCenter)
        self.lbl_step.setStyleSheet("color: #16a085; background-color: #e8f6f3; border-radius: 15px; padding: 6px;")
        nav_layout.addWidget(self.lbl_step)
        
        # Now Button
        self.btn_now = QPushButton("🕐 လက်ရှိအချိန်သို့ ပြန်သွားရန်")
        self.btn_now.setFont(QFont("Pyidaungsu", 11, QFont.Bold))
        self.btn_now.setMinimumHeight(42)
        self.btn_now.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.btn_now.clicked.connect(self.on_now_clicked)
        nav_layout.addWidget(self.btn_now)
        
        self.main_layout.addWidget(self.nav_frame)
        
        # === Bottom Note ===
        self.note_label = QLabel("💡 ကောဇာဂြိုဟ်များသည် နေ့စဉ်သုံး ဗေဒင်ဆိုင်ရာ\nတွက်ချက်မှုများအတွက် အသုံးဝင်ပါသည်။")
        self.note_label.setFont(QFont("Pyidaungsu", 9))
        self.note_label.setAlignment(Qt.AlignCenter)
        self.note_label.setStyleSheet("color: #95a5a6; background-color: transparent; padding: 5px;")
        self.note_label.setWordWrap(True)
        self.main_layout.addWidget(self.note_label)
        
        # === Initialize ===
        self.update_info_display()
        self.calculate_kawzar()
    
    def set_location(self, city_name, lat, lon):
        """နေရာအသစ် သတ်မှတ်ခြင်း"""
        self.current_location = {
            'name': city_name,
            'lat': float(lat),
            'lon': float(lon)
        }
        self.update_info_display()
        self.calculate_kawzar()
    
    def set_datetime(self, qdatetime):
        """အချိန်အသစ် သတ်မှတ်ခြင်း"""
        self.current_datetime = qdatetime
        self.update_info_display()
        self.calculate_kawzar()
    
    def update_info_display(self):
        """အချက်အလက်များကို ပြသခြင်း"""
        dt = self.current_datetime.toPyDateTime()
        time_str = dt.strftime("%d.%m.%Y %H:%M:%S")
        loc_str = f"{self.current_location['name']} ({self.current_location['lat']:.2f}°N, {self.current_location['lon']:.2f}°E)"
        
        self.lbl_location.setText(f"📍 {loc_str}")
        self.lbl_time.setText(f"🕐 {time_str}")
    
    def set_step_display(self, step_text):
        """အဆင့်အချက်အလက် ပြသခြင်း"""
        self.lbl_step.setText(f"📌 အဆင့်: {step_text}")
    
    def calculate_kawzar(self):
        """ကောဇာဂြိုဟ်များကို တွက်ချက်ခြင်း"""
        try:
            dt = self.current_datetime.toPyDateTime()
            
            # === UTC သို့ ပြောင်းလဲခြင်း (Myanmar Time UTC+6:30) ===
            utc_dt = dt - timedelta(hours=6.5)
             
            # === Julian Day တွက်ချက်ခြင်း ===
            jd = swe.julday(
                utc_dt.year, utc_dt.month, utc_dt.day,
                utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0
            )
            
            # === Ayanamsa Setup (Lahiri) ===
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            ayanamsa_val = swe.get_ayanamsa(jd)
            
            # === ဂြိုဟ်များ တွက်ချက်ခြင်း ===
            PLANET_IDS = [
                swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, 
                swe.JUPITER, swe.VENUS, swe.SATURN
            ]
            
            PLANET_NAMES_MM = {
                swe.SUN: 'နေ', swe.MOON: 'လ', swe.MARS: 'အင်္ဂါ',
                swe.MERCURY: 'ဗုဒ္ဓ', swe.JUPITER: 'ကြာသပတေး',
                swe.VENUS: 'သောကြာ',  swe.SATURN: 'စနေ'
            }
            
            PLANET_SYMBOLS = {
                swe.SUN: '၁', swe.MOON: '၂', swe.MARS: '၃',
                swe.MERCURY: '၄', swe.JUPITER: '၅',
                swe.VENUS: '၆', swe.SATURN: '၀'
            }
            
            results = []
            
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
                        'name': PLANET_NAMES_MM.get(pid, '?'),
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
            
            # === Lagna တွက်ချက်ခြင်း ===
            try:
                houses = swe.houses(jd, self.current_location['lat'], 
                                    self.current_location['lon'], b'E')
                asc_long_tropical = houses[0][0]
                asc_long_sidereal = (asc_long_tropical - ayanamsa_val) % 360
                
                asc_sign = int(asc_long_sidereal / 30)
                asc_deg = int(asc_long_sidereal % 30)
                asc_min = int((asc_long_sidereal * 60) % 60)
                
                lagna_data = {
                    'id': 'Lagna',
                    'name': 'လဂ်',
                    'symbol': 'လ',
                    'sign': asc_sign,
                    'deg': asc_deg,
                    'min': asc_min,
                    'retro': False,
                    'longitude': asc_long_sidereal
                }
                results.insert(0, lagna_data)
            except Exception as e:
                print(f"Lagna error: {e}")
            
            # === ရာဟု/ကေတု တွက်ချက်ခြင်း ===
            try:
                xx_rahu, retflag_rahu = swe.calc_ut(jd, swe.TRUE_NODE, 
                                                     swe.FLG_SIDEREAL | swe.FLG_SPEED)
                rahu_long = xx_rahu[0] % 360
                rahu_sign = int(rahu_long / 30)
                rahu_deg = int(rahu_long % 30)
                rahu_min = int((rahu_long * 60) % 60)
                
                rahu_data = {
                    'id': 'Rahu',
                    'name': 'ရာဟု',
                    'symbol': '၈',
                    'sign': rahu_sign,
                    'deg': rahu_deg,
                    'min': rahu_min,
                    'retro': False,
                    'longitude': rahu_long
                }
                results.append(rahu_data)
                
                # ကေတု (ရာဟု + ၁၈၀ ဒီဂရီ)
                ketu_long = (rahu_long + 180) % 360
                ketu_sign = int(ketu_long / 30)
                ketu_deg = int(ketu_long % 30)
                ketu_min = int((ketu_long * 60) % 60)
                
                ketu_data = {
                    'id': 'Ketu',
                    'name': 'ကိတ်',
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
            
            # === အိမ်တွက်ချက်ခြင်း ===
            if len(results) > 0 and results[0]['id'] == 'Lagna':
                asc_sign = results[0]['sign']
                for planet in results:
                    if planet['id'] != 'Lagna':
                        planet_sign = planet['sign']
                        house_number = (planet_sign + 12 - asc_sign) % 12 + 1
                        planet['house'] = house_number
            
            # === Chart Widget သို့ ဒေတာပို့ခြင်း ===
            self.chart_widget.set_planet_data(results, True, "ကောဇာ")
            
            return results
            
        except Exception as e:
            QMessageBox.critical(self, "တွက်ချက်မှု အမှား", 
                               f"ကောဇာတွက်ချက်ရာတွင် အမှားဖြစ်ပေါ်:\n{str(e)}")
            return []
    
    def navigate_time(self, direction, step_type):
        """အချိန်ကို ရွှေ့ပြောင်းခြင်း"""
        dt = self.current_datetime.toPyDateTime()
        
        if step_type == 'sec':
            delta = timedelta(seconds=direction * 1)
        elif step_type == 'min':
            delta = timedelta(minutes=direction * 1)
        elif step_type == 'hour':
            delta = timedelta(hours=direction * 1)
        elif step_type == 'day':
            delta = timedelta(days=direction * 1)
        elif step_type == 'month':
            delta = timedelta(days=direction * 30)
        elif step_type == 'year':
            delta = timedelta(days=direction * 365)
        else:
            delta = timedelta(minutes=direction * 1)
        
        new_dt = dt + delta
        self.current_datetime = QDateTime(new_dt)
        
        self.update_info_display()
        self.calculate_kawzar()
    
    def on_now_clicked(self):
        """Now ခလုတ်နှိပ်သည့်အခါ လက်ရှိအချိန်သို့ ပြန်သွားခြင်း"""
        self.now_clicked.emit()
        self.current_datetime = QDateTime.currentDateTime()
        
        if self.parent and hasattr(self.parent, 'update_kawzar_to_now'):
            self.parent.update_kawzar_to_now()
        else:
            self.update_info_display()
            self.calculate_kawzar()
    
    def get_current_datetime(self):
        """လက်ရှိအချိန်ကို ပြန်ပေးခြင်း"""
        return self.current_datetime
    
    def get_current_location(self):
        """လက်ရှိနေရာကို ပြန်ပေးခြင်း"""
        return self.current_location