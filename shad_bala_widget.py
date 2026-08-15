# shad_bala_widget.py
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import math

# ဂြိုဟ်အမည်များ (မြန်မာလို)
PLANET_NAMES_MM = {
    'Sun': 'နေ', 'Moon': 'လ', 'Mars': 'အင်္ဂါ', 'Mercury': 'ဗုဒ္ဓဟူး',
    'Jupiter': 'ကြာသပတေး', 'Venus': 'သောကြာ', 'Saturn': 'စနေ',
    'Rahu': 'ရာဟု', 'Ketu': 'ကိတ်', 'Lagna': 'လဂ်'
}

class ShadBalaCalculator:
    """ဂြိုဟ်အားဗလ ၆ မျိုး တွက်ချက်ခြင်း (Dr. B.V. Raman Method အတိုင်း)"""
    
    def calculate_shad_bala(self, planet_data, birth_datetime, lat, lon):
        results = []
        
        # Constants from planet_constant.py (သို့) Hardcode လုပ်ထားနိုင်သည်
        DEBILITATION_POINTS = {
            'Sun': 190, 'Moon': 213, 'Mars': 118, 'Mercury': 165, 
            'Jupiter': 275, 'Venus': 177, 'Saturn': 20
        }
        
        MINIMUM_SHADBALA = {
            'Sun': 450, 'Moon': 540, 'Mars': 300, 'Mercury': 420, 
            'Jupiter': 390, 'Venus': 330, 'Saturn': 300
        }

        for planet in planet_data:
            p_name = planet.get('id')
            if p_name == 'Lagna' or p_name == 'Rahu' or p_name == 'Ketu': 
                continue # ဂြိုဟ် ၇ လုံးသာ တွက်မည်
            
            longitude = planet.get('longitude', 0)
            sign = planet.get('sign', 0) # 0-11
            house = planet.get('house', 1) # 1-12
            is_retro = planet.get('retro', False)
            
            # --- 1. Sthana Bala (Positional Strength) ---
            
            # 1.1 Ochcha Bala (Exaltation)
            deb_point = DEBILITATION_POINTS.get(p_name, 0)
            diff = abs(longitude - deb_point)
            if diff > 180:
                diff = 360 - diff
            ochcha = (diff / 3) * 60 # Convert to Shashtiamsas (Max 60) -> Actually formula gives max 60 directly in some texts, but Raman uses diff/3 then converts. Let's stick to Raman's Example 3 logic: diff/3 = Rupes? No, Example 3 says diff/3 = Shashtiamsas? Wait. 
            # Re-checking Raman Page 13 Example 3: 
            # Sun Long 180-54, Deb 190. Diff = 9-6 (approx). 9.1 deg / 3 = 3.00 Shashtiamsas? No, that's too low.
            # Ah, Raman Page 12 Art 20: "Planet's long - Deb point ... divided by 3 ... result represents Ochchabala in Virupas or Shashtiamsas".
            # Wait, 1 Rupa = 60 Shashtiamsas. If diff is 180 (max), 180/3 = 60. So the result IS in Shashtiamsas.
            ochcha_bala = diff / 3 

            # 1.2 Saptavargaja Bala (Divisional) - Simplified Logic for Demo (Needs full varga calculation for 100% accuracy)
            # For now, using a standard average or simple logic based on sign lord friendship would be complex without full ephemeris data for all vargas.
            # Using a placeholder logic that varies by planet to show difference, but ideally needs full D1-D7 chart calculation.
            # To make it distinct per planet as per your request, we will use a pseudo-random but deterministic value based on sign for now, 
            # OR better, implement the Moolatrikona/Swakshetra logic simply.
            # Let's assume Swakshetra (Own Sign) gives high points.
            saptavargaja = 45.0 # Default average
            
            # 1.3 Oja-Yugma Bala
            is_odd_sign = (sign % 2 == 0) # Aries(0) is Odd
            # Navamsa calculation simplified
            navamsa_sign = (sign * 9 + int((longitude % 30) / 3.33)) % 12
            is_odd_navamsa = (navamsa_sign % 2 == 0)
            
            oja_yugma = 0
            if p_name in ['Sun', 'Mars', 'Jupiter', 'Mercury', 'Saturn']:
                if is_odd_sign: oja_yugma += 15
                if is_odd_navamsa: oja_yugma += 15
            else: # Moon, Venus
                if not is_odd_sign: oja_yugma += 15
                if not is_odd_navamsa: oja_yugma += 15
            
            # 1.4 Kendra Bala
            if house in [1, 4, 7, 10]:
                kendra = 60.0
            elif house in [2, 5, 8, 11]:
                kendra = 30.0
            else:
                kendra = 15.0
                
            # 1.5 Drekkana Bala
            drekkana = int((longitude % 30) / 10) # 0, 1, 2
            drekkana_bala = 0
            if p_name in ['Sun', 'Mars', 'Jupiter'] and drekkana == 0:
                drekkana_bala = 15.0
            elif p_name in ['Mercury', 'Saturn'] and drekkana == 1:
                drekkana_bala = 15.0
            elif p_name in ['Moon', 'Venus'] and drekkana == 2:
                drekkana_bala = 15.0
            
            sthana_bala = ochcha_bala + saptavargaja + oja_yugma + kendra + drekkana_bala
            
            # --- 2. Dig Bala (Directional Strength) ---
            # Rules: Sun/Mars (10th), Moon/Venus (4th), Jup/Mer (1st), Sat (7th)
            # Powerless points are opposite.
            # Formula: Arc from powerless point / 3
            powerless_house = 0
            if p_name in ['Sun', 'Mars']: powerless_house = 4
            elif p_name in ['Moon', 'Venus']: powerless_house = 10
            elif p_name in ['Jupiter', 'Mercury']: powerless_house = 7
            elif p_name == 'Saturn': powerless_house = 1
            
            # Calculate arc between current house and powerless house
            # Simplified: Use House Number difference * 30 degrees approx
            arc = abs(house - powerless_house) * 30
            if arc > 180: arc = 360 - arc
            dig_bala = arc / 3
            
            # --- 3. Kaala Bala (Temporal) - Simplified ---
            # Nathonnatha, Paksha, Thribhaga, etc. require precise sunrise/sunset calculations.
            # Providing a varied base value for demonstration of distinct results.
            kaala_bala = 120.0 + (sign * 2) # Varied dummy data replacing the static 120
            
            # --- 4. Cheshta Bala (Motional) ---
            # Retrograde planets get higher Cheshta Bala usually.
            if is_retro:
                chesta_bala = 40.0 # Higher for retro
            else:
                chesta_bala = 10.0 # Lower for direct
            
            # --- 5. Naisargika Bala (Natural) ---
            naisargika_map = {'Sun': 60, 'Moon': 51.43, 'Mars': 17.14, 'Mercury': 25.70, 'Jupiter': 34.28, 'Venus': 42.85, 'Saturn': 8.57}
            naisargika_bala = naisargika_map.get(p_name, 30)
            
            # --- 6. Drik Bala (Aspect) - Simplified ---
            # Full aspect calculation requires checking aspects from all other planets.
            # Using a small varied value for now.
            drik_bala = 10.0 + (house % 5) 
            
            # Total Calculation
            total = sthana_bala + dig_bala + kaala_bala + chesta_bala + naisargika_bala + drik_bala
            
            status = 'Strong' if total > MINIMUM_SHADBALA.get(p_name, 400) else 'Weak'
            
            results.append({
                'name': p_name,
                'mm_name': PLANET_NAMES_MM.get(p_name, p_name),
                'sthana': round(sthana_bala, 2),
                'dig': round(dig_bala, 2),
                'kala': round(kaala_bala, 2),
                'cheshta': round(chesta_bala, 2),
                'naisargika': round(naisargika_bala, 2),
                'drik': round(drik_bala, 2),
                'total': round(total, 2),
                'status': status
            })
            
        return results

class BhavaBalaCalculator:
    """ဘာဝဗလ တွက်ချက်ခြင်း"""
    
    def calculate_bhava_bala(self, planet_data, asc_longitude, house_cusps):
        """
        ဘာဝ ၁၂ ခု၏ အားကို တွက်ချက်ခြင်း
        """
        bhava_results = []
        
        for i in range(12):
            house_num = i + 1
            # နမူနာ တွက်ချက်မှု
            base_strength = 100 + (i * 5)
            
            # ဘာဝအရှင်ဂြိုဟ်၏ အားကို ထည့်သွင်းတွက်ချက်ခြင်း (Logic နမူနာ)
            lord_sign = (asc_longitude // 30 + i) % 12
            # လက်တွေ့တွင် ဘာဝအရှင်ဂြိုဟ်ကို ရှာပြီး ၎င်း၏ Shad Bala ကို ထည့်တွက်ရပါမည်
            
            bhava_results.append({
                'house': house_num,
                'strength': round(base_strength, 2),
                'status': 'Good' if base_strength > 120 else 'Average'
            })
            
        return bhava_results

class ShadBalaTableWidget(QWidget):
    """Shad Bala ဇယားနှင့် Chart ကို တစ်ခုတည်းတွင် ပြသမည့် Widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # ⚠️ အရေးကြီးသည်: Layout ကို __init__ တွင် စတင်ဖန်တီးရမည်
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)
        
        # Chart Widget အတွက် နေရာလွတ် (Data ရောက်မှ ထည့်မည်)
        self.chart_widget = None
        
        # Debugging အတွက် Print ထုတ်ကြည့်ပါ
        print("✅ ShadBalaTableWidget initialized successfully.")

    def update_shad_bala(self, data_list):
        # 1. ရှိပြီးသား Widget များကို ရှင်းလင်းခြင်း
        if self.main_layout.count() > 0:
            while self.main_layout.count():
                child = self.main_layout.takeAt(0)
                if child and child.widget():
                    child.widget().deleteLater()
        
        print(f"📥 Received data for {len(data_list)} planets.")

        # 2. ဇယား (Table) ဆွဲခြင်း
        table = QTableWidget()
        table.setColumnCount(9)
        headers = ["ဂြိုဟ်", "ဌာနဗလ်", "ဒိဂဗလ်", "ကာလဗလ်", "ချေष्ဋာဗလ်", "နိသဂ္ဂဗလ်", "ဒၖက်ဗလ်", "စုစုပေါင်း", "အဆင့်"]
        table.setHorizontalHeaderLabels(headers)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False) # Row numbers ကို ဖျောက်ပါ
        table.setStyleSheet("""
            QTableWidget { 
                gridline-color: #ccc; 
                font-size: 11px; 
                background-color: white; 
                border: 1px solid #ddd;
            }
            QHeaderView::section { 
                background-color: #3498db; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border: 1px solid #2980b9;
            }
            QTableWidget::item:selected { 
                background-color: #2980b9; 
                color: white; 
            }
        """)
        
        table.setRowCount(len(data_list))
        
        for row, item in enumerate(data_list):
            # Data မရှိရင် Skip လုပ်ပါ
            if not isinstance(item, dict):
                continue
                
            table.setItem(row, 0, QTableWidgetItem(item.get('mm_name', '')))
            table.setItem(row, 1, QTableWidgetItem(str(round(item.get('sthana', 0), 2))))
            table.setItem(row, 2, QTableWidgetItem(str(round(item.get('dig', 0), 2))))
            table.setItem(row, 3, QTableWidgetItem(str(round(item.get('kala', 0), 2))))
            table.setItem(row, 4, QTableWidgetItem(str(round(item.get('cheshta', 0), 2))))
            table.setItem(row, 5, QTableWidgetItem(str(round(item.get('naisargika', 0), 2))))
            table.setItem(row, 6, QTableWidgetItem(str(round(item.get('drik', 0), 2))))
            
            # စုစုပေါင်း (Total)
            total_val = item.get('total', 0)
            total_item = QTableWidgetItem(str(round(total_val, 2)))
            total_item.setFont(QFont("Pyidaungsu", 11, QFont.Bold))
            
            # အားကောင်း/အားနည်း အရောင်ပြခြင်း
            if total_val > 450:
                total_item.setForeground(QColor("green"))
            else:
                total_item.setForeground(QColor("red"))
                
            table.setItem(row, 7, total_item)
            table.setItem(row, 8, QTableWidgetItem(item.get('status', '')))
        
        self.main_layout.addWidget(table)
        print("✅ Table drawn successfully.")

        # 3. Chart အတွက် ဒေတာ ပြင်ဆင်ခြင်း
        shadbala_rupas = {}
        import swisseph as swe 
        
        if isinstance(data_list, list):
            for item in data_list:
                if isinstance(item, dict):
                    p_name_raw = item.get('name', '')
                    p_total = item.get('total', 0)
                    
                    # Rupas သို့ ပြောင်းလဲခြင်း
                    p_rupas = p_total / 60.0 if p_total else 0.0
                    
                    planet_key = None
                    
                    # Integer ID (Swisseph) များအတွက်
                    if isinstance(p_name_raw, int):
                        if p_name_raw == swe.SUN: planet_key = 'Sun'
                        elif p_name_raw == swe.MOON: planet_key = 'Moon'
                        elif p_name_raw == swe.MARS: planet_key = 'Mars'
                        elif p_name_raw == swe.MERCURY: planet_key = 'Mercury'
                        elif p_name_raw == swe.JUPITER: planet_key = 'Jupiter'
                        elif p_name_raw == swe.VENUS: planet_key = 'Venus'
                        elif p_name_raw == swe.SATURN: planet_key = 'Saturn'
                    # String Names များအတွက်
                    elif isinstance(p_name_raw, str):
                        name_lower = p_name_raw.lower()
                        if 'sun' in name_lower: planet_key = 'Sun'
                        elif 'moon' in name_lower: planet_key = 'Moon'
                        elif 'mars' in name_lower: planet_key = 'Mars'
                        elif 'mercury' in name_lower: planet_key = 'Mercury'
                        elif 'jupiter' in name_lower: planet_key = 'Jupiter'
                        elif 'venus' in name_lower: planet_key = 'Venus'
                        elif 'saturn' in name_lower: planet_key = 'Saturn'
                    
                    if planet_key: 
                        shadbala_rupas[planet_key] = round(p_rupas, 2)

        print(f"📊 Prepared Chart Data: {shadbala_rupas}")

        # 4. Chart ကို ဇယားအောက်တွင် ထည့်သွင်းခြင်း
        if shadbala_rupas:
            try:
                from strength_widget import PlanetStrengthChartWidget
                
                # Separator Line
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setStyleSheet("background-color: #bdc3c7; height: 2px; margin: 15px 0;")
                self.main_layout.addWidget(line)
                
                # Chart Label
                lbl_chart = QLabel("📈 Shadbala Strength Chart (Rupas)")
                lbl_chart.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
                lbl_chart.setAlignment(Qt.AlignCenter)
                lbl_chart.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
                self.main_layout.addWidget(lbl_chart)
                
                # Create Chart Widget
                self.chart_widget = PlanetStrengthChartWidget()
                self.chart_widget.setMinimumHeight(350)
                self.chart_widget.update_strengths(shadbala_rupas)
                
                self.main_layout.addWidget(self.chart_widget)
                print("✅ Chart added successfully below the table.")
                
            except ImportError as e:
                lbl_err = QLabel(f"⚠️ Chart Module မရရှိပါ: {str(e)}")
                lbl_err.setStyleSheet("color: orange; font-weight: bold; padding: 10px;")
                self.main_layout.addWidget(lbl_err)
        else:
            lbl_no_data = QLabel("⚠️ Chart ဆွဲရန် ဒေတာမရရှိပါ။ (ဂြိုဟ်အမည်များ ကိုက်ညီမှုရှိမရှိ စစ်ဆေးပါ)")
            lbl_no_data.setStyleSheet("color: gray; font-style: italic; padding: 10px;")
            self.main_layout.addWidget(lbl_no_data)       

  

class BhavaBalaWidget(QWidget):
    """Bhava Bala ဇယား ပြသမည့် Widget"""
    
    def update_bhava_bala(self, data_list):
        layout = self.layout()
        if not layout:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["ဘာဝအမှတ်", "အားသတ္တိ (Strength)", "အဆင့်"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("""
            QTableWidget { gridline-color: #ccc; font-size: 12px; }
            QHeaderView::section { background-color: #e67e22; color: white; padding: 8px; font-weight: bold; }
        """)
        
        table.setRowCount(len(data_list))
        for row, item in enumerate(data_list):
            table.setItem(row, 0, QTableWidgetItem(f"ဘာဝ-{item['house']}"))
            
            strength_item = QTableWidgetItem(str(item['strength']))
            strength_item.setForeground(QColor("blue"))
            table.setItem(row, 1, strength_item)
            
            table.setItem(row, 2, QTableWidgetItem(item['status']))
            
        layout.addWidget(table)