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
    ဒီဇိုင်းညီညာမှု၊ Font Size နှင့် Chart အရွယ်အစားကို ပြင်ဆင်ထားသည်
    """
    now_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_datetime = QDateTime.currentDateTime()
        self.current_location = {'name': 'ရန်ကုန်', 'lat': 16.8661, 'lon': 96.1951}
        
        # Widget အရွယ်အစား (Chart 420x420 နှင့် UI များ လုံလောက်စွာဆန့်ဝင်ရန်)
        self.setFixedSize(420, 520)
        
        # Swisseph Path Setup
        ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
        if os.path.exists(ephe_path):
            swe.set_ephe_path(ephe_path)
            
        self._setup_ui()
        self.update_info_display()
        self.calculate_kawzar()

    def _setup_ui(self):
        """Clean & Balanced Layout Setup"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # === 2. တည်နေရာ & အချိန် ကတ် (Font 14) ===
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("background-color: #a3d2fa; border-radius: 8px; border: 1px solid #0757fe;")
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(0,0,0,0)
        info_layout.setSpacing(0)

        self.lbl_location = QLabel("📍 တောင်ကြီး (20.77°N, 97.04°E)")
        self.lbl_location.setAlignment(Qt.AlignCenter)
        self.lbl_location.setFont(QFont("Pyidaungsu", 14, QFont.Bold))
        self.lbl_location.setStyleSheet("color: #000000;")

        self.lbl_time = QLabel("🕐 22-04-2026 12:23:48")
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setFont(QFont("Pyidaungsu", 16,QFont.Bold))
        self.lbl_time.setStyleSheet("color: #004000;")

        info_layout.addWidget(self.lbl_location)
        info_layout.addWidget(self.lbl_time)
        main_layout.addWidget(self.info_frame)

        # === 3. ကောဇာဇာတာ Chart (420x420) ===
        self.chart_frame = QFrame()
        self.chart_frame.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #dcdde1;")
        self.chart_frame.setMaximumSize(420,420)
        
        chart_layout = QVBoxLayout(self.chart_frame)
        chart_layout.setContentsMargins(5,5,5,5)
        chart_layout.setAlignment(Qt.AlignCenter)

        self.chart_widget = BurmeseChartWidget()
        self.chart_widget.setFixedSize(400, 400)
        chart_layout.addWidget(self.chart_widget, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.chart_frame)

        # === 4. Navigation Controls ===
        self.ctrl_frame = QFrame()
        self.ctrl_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 8px; border: 1px solid #e0e4e8;")
        ctrl_layout = QHBoxLayout(self.ctrl_frame)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)  # ✅ ပြင်ဆင်ပြီး
        ctrl_layout.setSpacing(5)

        self.lbl_step = QLabel("📌 ကြာချိန် ")
        self.lbl_step.setAlignment(Qt.AlignCenter)
        self.lbl_step.setFont(QFont("Pyidaungsu", 11, QFont.Bold))
        self.lbl_step.setStyleSheet("color: #16a085; background-color: #e8f6f3; border-radius: 12px; padding: 0px 0px;")
        ctrl_layout.addWidget(self.lbl_step, 1)

        self.btn_now = QPushButton("🕐 လက်ရှိအချိန်သို့ ပြန်သွားရန်")
        self.btn_now.setFont(QFont("Pyidaungsu", 11, QFont.Bold))
        self.btn_now.setMinimumHeight(38)
        self.btn_now.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border: none; border-radius: 6px; padding: 0px; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1c638e; }
        """)
        self.btn_now.clicked.connect(self.on_now_clicked)
        ctrl_layout.addWidget(self.btn_now, 2)

        main_layout.addWidget(self.ctrl_frame)

        # # === 5. အောက်ခြေမှတ်စု ===
        # self.note_label = QLabel("💡 ကောဇာဂြိုဟ်များသည် နေ့စဉ်သုံး ဗေဒင်ဆိုင်ရာ တွက်ချက်မှုများအတွက် အသုံးဝင်ပါသည်။")
        # self.note_label.setAlignment(Qt.AlignCenter)
        # self.note_label.setWordWrap(True)
        # self.note_label.setFont(QFont("Pyidaungsu", 9))
        # self.note_label.setStyleSheet("color: #95a5a6; padding-top: 6px;")
        # main_layout.addWidget(self.note_label)

    # ==================== လုပ်ဆောင်ချက်များ (မူလအတိုင်း) ====================
    def set_location(self, city_name, lat, lon):
        self.current_location = {'name': city_name, 'lat': float(lat), 'lon': float(lon)}
        self.update_info_display()
        self.calculate_kawzar()

    def set_datetime(self, qdatetime):
        self.current_datetime = qdatetime
        self.update_info_display()
        self.calculate_kawzar()

    def update_info_display(self):
        dt = self.current_datetime.toPyDateTime()
        time_str = dt.strftime("%d-%m-%Y %H:%M:%S")
        loc_str = f"{self.current_location['name']} ({self.current_location['lat']:.2f}°N, {self.current_location['lon']:.2f}°E)"
        self.lbl_location.setText(f"📍 {loc_str}")
        self.lbl_time.setText(f"🕐 {time_str}")

    def set_step_display(self, step_text):
        self.lbl_step.setText(f"📌 အဆင့်: {step_text}")


    def calculate_kawzar(self):
        try:
            dt = self.current_datetime.toPyDateTime()
            utc_dt = dt - timedelta(hours=6.5)
            jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                            utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            ayanamsa_val = swe.get_ayanamsa(jd)
            
            PLANET_IDS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN]
            PLANET_NAMES_MM = {swe.SUN: 'နေ', swe.MOON: 'လ', swe.MARS: 'အင်္ဂါ', swe.MERCURY: 'ဗုဒ္ဓ', swe.JUPITER: 'ကြာသပတေး', swe.VENUS: 'သောကြာ', swe.SATURN: 'စနေ'}
            PLANET_SYMBOLS = {swe.SUN: '၁', swe.MOON: '၂', swe.MARS: '၃', swe.MERCURY: '၄', swe.JUPITER: '၅', swe.VENUS: '၆', swe.SATURN: '၀'}
            
            results = []
            for pid in PLANET_IDS:
                xx, retflag = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
                planet_long = xx[0] % 360
                results.append({
                    'id': pid, 'name': PLANET_NAMES_MM.get(pid, '?'), 'symbol': PLANET_SYMBOLS.get(pid, '?'),
                    'sign': int(planet_long / 30), 'deg': int(planet_long % 30),
                    'min': int((planet_long * 60) % 60), 'retro': (xx[3] < 0), 'longitude': planet_long
                })
            
            # Rahu & Ketu တွက်ချက်ခြင်း
            xx_rahu, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SIDEREAL | swe.FLG_SPEED)
            rahu_long = xx_rahu[0] % 360
            results.append({'id': 'Rahu', 'name': 'ရာဟု', 'symbol': '၈', 'sign': int(rahu_long / 30), 
                            'deg': int(rahu_long % 30), 'min': int((rahu_long * 60) % 60), 'retro': False, 'longitude': rahu_long})
            ketu_long = (rahu_long + 180) % 360
            results.append({'id': 'Ketu', 'name': 'ကိတ်', 'symbol': '၉', 'sign': int(ketu_long / 30), 
                            'deg': int(ketu_long % 30), 'min': int((ketu_long * 60) % 60), 'retro': False, 'longitude': ketu_long})
            
            # 🔄 Lagna ကို results ထဲ မထည့်တော့ပါ။ 
            # သို့သော် ဂြိုဟ်များ၏ ဘာဝ(House) သတ်မှတ်ရန် Ascendant Sign ကို သီးသန့် တွက်ယူပါမည်။
            houses = swe.houses(jd, self.current_location['lat'], self.current_location['lon'], b'E')
            asc_long_sidereal = (houses[0][0] - ayanamsa_val) % 360
            asc_sign = int(asc_long_sidereal / 30)
            
            # ဂြိုဟ်တစ်ခုစီအတွက် ဘာဝ (House) တွက်ချက်ခြင်း
            for p in results:
                p['house'] = (p['sign'] + 12 - asc_sign) % 12 + 1
                
            self.chart_widget.set_planet_data(results, True, "ကောဇာ")
            return results
            
        except Exception as e:
            QMessageBox.critical(self, "တွက်ချက်မှု အမှား", f"ကောဇာတွက်ချက်ရာတွင် အမှားဖြစ်ပေါ်:\n{str(e)}")
            return []
    
    #+++++++++++++++++++++++++++++++++++++  ပြီးပါပြီ +++++++++++++++++++++++++++++++++++++++++++
    #လဂ်မပါပဲ တွက်ချင် အပေါ်ကဟာယူ
    # def calculate_kawzar(self):
    #     try:
    #         dt = self.current_datetime.toPyDateTime()
    #         utc_dt = dt - timedelta(hours=6.5)
    #         jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
    #                         utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    #         swe.set_sid_mode(swe.SIDM_LAHIRI)
    #         ayanamsa_val = swe.get_ayanamsa(jd)
            
    #         PLANET_IDS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN]
    #         PLANET_NAMES_MM = {swe.SUN: 'နေ', swe.MOON: 'လ', swe.MARS: 'အင်္ဂါ', swe.MERCURY: 'ဗုဒ္ဓ', swe.JUPITER: 'ကြာသပတေး', swe.VENUS: 'သောကြာ', swe.SATURN: 'စနေ'}
    #         PLANET_SYMBOLS = {swe.SUN: '၁', swe.MOON: '၂', swe.MARS: '၃', swe.MERCURY: '၄', swe.JUPITER: '၅', swe.VENUS: '၆', swe.SATURN: '၀'}
            
    #         results = []
    #         for pid in PLANET_IDS:
    #             xx, retflag = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    #             planet_long = xx[0] % 360
    #             results.append({
    #                 'id': pid, 'name': PLANET_NAMES_MM.get(pid, '?'), 'symbol': PLANET_SYMBOLS.get(pid, '?'),
    #                 'sign': int(planet_long / 30), 'deg': int(planet_long % 30),
    #                 'min': int((planet_long * 60) % 60), 'retro': (xx[3] < 0), 'longitude': planet_long
    #             })
            
    #         houses = swe.houses(jd, self.current_location['lat'], self.current_location['lon'], b'E')
    #         asc_long_sidereal = (houses[0][0] - ayanamsa_val) % 360
    #         # results.insert(0, {
    #         #     'id': 'Lagna', 'name': 'လဂ်', 'symbol': 'လ',
    #         #     'sign': int(asc_long_sidereal / 30), 'deg': int(asc_long_sidereal % 30),
    #         #     'min': int((asc_long_sidereal * 60) % 60), 'retro': False, 'longitude': asc_long_sidereal
    #         # })
            
    #         xx_rahu, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    #         rahu_long = xx_rahu[0] % 360
    #         results.append({'id': 'Rahu', 'name': 'ရာဟု', 'symbol': '၈', 'sign': int(rahu_long / 30), 
    #                         'deg': int(rahu_long % 30), 'min': int((rahu_long * 60) % 60), 'retro': False, 'longitude': rahu_long})
    #         ketu_long = (rahu_long + 180) % 360
    #         results.append({'id': 'Ketu', 'name': 'ကိတ်', 'symbol': '၉', 'sign': int(ketu_long / 30), 
    #                         'deg': int(ketu_long % 30), 'min': int((ketu_long * 60) % 60), 'retro': False, 'longitude': ketu_long})
            
    #         asc_sign = results[0]['sign']
    #         for p in results:
    #             #if p['id'] != 'Lagna':
    #             p['house'] = (p['sign'] + 12 - asc_sign) % 12 + 1
            
    #         self.chart_widget.set_planet_data(results, True, "ကောဇာ")
    #         return results
    #     except Exception as e:
    #         QMessageBox.critical(self, "တွက်ချက်မှု အမှား", f"ကောဇာတွက်ချက်ရာတွင် အမှားဖြစ်ပေါ်:\n{str(e)}")
    #         return []
    
    
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def navigate_time(self, direction, step_type):
        dt = self.current_datetime.toPyDateTime()
        delta_map = {'sec': timedelta(seconds=direction), 'min': timedelta(minutes=direction), 
                     'hour': timedelta(hours=direction), 'day': timedelta(days=direction),
                     'month': timedelta(days=direction * 30), 'year': timedelta(days=direction * 365)}
        self.current_datetime = QDateTime(dt + delta_map.get(step_type, timedelta(minutes=direction)))
        self.update_info_display()
        self.calculate_kawzar()

    def on_now_clicked(self):
        self.now_clicked.emit()
        self.current_datetime = QDateTime.currentDateTime()
        if self.parent and hasattr(self.parent, 'update_kawzar_to_now'):
            self.parent.update_kawzar_to_now()
        else:
            self.update_info_display()
            self.calculate_kawzar()

    def get_current_datetime(self): 
        return self.current_datetime
    
    def get_current_location(self): 
        return self.current_location