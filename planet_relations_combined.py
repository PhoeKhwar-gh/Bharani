# planet_relations_combined.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QProgressBar,QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

class CombinedRelationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header = QLabel("🔗 ဂြိုဟ်ဆက်နွယ်မှု ပေါင်းစပ်ခွဲခြမ်းစိတ်ဖြာချက်")
        header.setStyleSheet("font-size: 12pt; font-weight: bold; padding: 8px; background: #3498db; color: white; border-radius: 5px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ဂြိုဟ်", "မူလဆက်နွယ်", "ဂုဏ်သတ္တိ", "အမြင်(Aspect)", "အိမ်တည်နေရာ", "စုစုပေါင်း%", "အဆင့်"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { font-size: 9pt; border: 1px solid #dee2e6; }
            QHeaderView::section { 
                background-color: #2c3e50; color: white; padding: 6px; font-weight: bold; 
            }
            QProgressBar { border: 1px solid #bdc3c7; border-radius: 3px; text-align: center; }
            QProgressBar::chunk { border-radius: 3px; }
        """)
        layout.addWidget(self.table)
    
    def calculate_dignity_score(self, planet_name, lon_d1, lon_d9, planet_data):
        """ဂြိုဟ်ဂုဏ်သတ္တိ (Dignity) အမှတ်ပေးခြင်း (0-100)"""
        score = 50  # Base neutral
        sign_d1 = int(lon_d1 // 30)
        deg_d1 = lon_d1 % 30
        sign_d9 = int(lon_d9 // 30)
        
        # 🔹 ဥုစ်အား (Exaltation) = +40
        exalt_map = {'Sun': (0,10), 'Moon': (1,3), 'Mars': (9,28), 'Mercury': (5,15),
                     'Jupiter': (3,5), 'Venus': (11,27), 'Saturn': (6,20)}
        if planet_name in exalt_map:
            ex_sign, ex_deg = exalt_map[planet_name]
            if sign_d1 == ex_sign:
                score += 40 - abs(deg_d1 - ex_deg) * 0.5  # ဒီဂရီနီးလေ ပိုကောင်းလေ
        
        # 🔹 နိစ်အား (Debilitation) = -40
        deb_map = {'Sun': (6,10), 'Moon': (7,3), 'Mars': (3,28), 'Mercury': (11,15),
                   'Jupiter': (9,5), 'Venus': (5,27), 'Saturn': (0,20)}
        if planet_name in deb_map:
            db_sign, db_deg = deb_map[planet_name]
            if sign_d1 == db_sign:
                score -= 40 - abs(deg_d1 - db_deg) * 0.5
        
        # 🔹 ကသစ်/မူလတြိဂုဏ် = +25
        own_signs = {'Sun': [4], 'Moon': [3], 'Mars': [0,7], 'Mercury': [2,5],
                     'Jupiter': [8,11], 'Venus': [1,6], 'Saturn': [9,10]}
        if planet_name in own_signs and sign_d1 in own_signs[planet_name]:
            score += 25
        
        # 🔹 ဝဂ္ဂုတ္တမ (D1 & D9 same sign) = +15
        if sign_d1 == sign_d9:
            score += 15
        
        # 🔹 နဝင်းအား (Own sign in D9) = +10
        own_d9 = {'Sun': 4, 'Moon': 1, 'Mars': 0, 'Mercury': 2, 'Jupiter': 8, 'Venus': 1, 'Saturn': 10}
        if planet_name in own_d9 and sign_d9 == own_d9[planet_name]:
            score += 10
        
        return max(0, min(100, score))
    
    def calculate_aspect_score(self, p1_name, p1_lon, p2_name, p2_lon):
        """ဂြိုဟ်အမြင် (Aspect) အမှတ်ပေးခြင်း"""
        diff = abs(p1_lon - p2_lon)
        if diff > 180: diff = 360 - diff
        
        # 🔹 Special Aspects by Planet
        aspect_bonus = 0
        
        # Saturn: 3rd, 7th, 10th aspect (full)
        if p1_name == 'Saturn':
            if abs(diff - 180) < 5: aspect_bonus += 30  # 7th
            elif abs(diff - 120) < 5 or abs(diff - 240) < 5: aspect_bonus += 25  # 3rd/10th
            elif abs(diff - 90) < 5 or abs(diff - 270) < 5: aspect_bonus += 15  # 4th/8th
        
        # Jupiter: 5th, 7th, 9th aspect (full)
        elif p1_name == 'Jupiter':
            if abs(diff - 180) < 5: aspect_bonus += 30  # 7th
            elif abs(diff - 120) < 5 or abs(diff - 240) < 5: aspect_bonus += 25  # 5th/9th
        
        # Mars: 4th, 7th, 8th aspect (full)
        elif p1_name == 'Mars':
            if abs(diff - 180) < 5: aspect_bonus += 30  # 7th
            elif abs(diff - 90) < 5 or abs(diff - 270) < 5: aspect_bonus += 25  # 4th/8th
        
        # 🔹 General proximity bonus (within 5° orb)
        if diff < 5:
            aspect_bonus += 20
        elif diff < 10:
            aspect_bonus += 10
        
        # 🔹 Malefic aspect penalty (if aspecting a benefic)
        benefics = ['Jupiter', 'Venus', 'Mercury', 'Moon']
        malefics = ['Saturn', 'Mars', 'Sun', 'Rahu', 'Ketu']
        if p1_name in malefics and p2_name in benefics:
            aspect_bonus -= 10
        
        return max(0, min(100, 50 + aspect_bonus))
    
    def calculate_house_score(self, p1_house, p2_house):
        """အိမ်တည်နေရာ အမှတ်ပေးခြင်း (1-12)"""
        # 🔹 Kendra (1,4,7,10) = +20, Trikona (1,5,9) = +25
        kendra = [1, 4, 7, 10]
        trikona = [1, 5, 9]
        dusthana = [6, 8, 12]
        
        score = 50  # Base
        
        # Both in Kendra/Trikona = Good relationship
        if p1_house in kendra and p2_house in kendra:
            score += 15
        if p1_house in trikona and p2_house in trikona:
            score += 20
        
        # One in Dusthana = Slight penalty
        if p1_house in dusthana or p2_house in dusthana:
            score -= 10
        
        # 🔹 Mutual Kendra-Trikona relationship = Excellent
        if (p1_house in kendra and p2_house in trikona) or (p1_house in trikona and p2_house in kendra):
            score += 25
        
        # 🔹 6/8 relationship (Shadashtaka) = Challenging
        if abs(p1_house - p2_house) in [5, 7]:
            score -= 20
        
        return max(0, min(100, score))
    
    def calculate_combined_percentage(self, natural_rel, dignity_p1, dignity_p2, 
                                   aspect_score, house_score):
        """အချက် (၄) ချက်ကို ပေါင်းစပ်တွက်ချက်ခြင်း"""
        # Natural relation: friend=80, neutral=50, enemy=20
        nat_map = {'friend': 80, 'neutral': 50, 'enemy': 20}
        nat_score = nat_map.get(natural_rel, 50)
        
        # Average dignity of both planets
        avg_dignity = (dignity_p1 + dignity_p2) / 2
        
        # Weighted combination
        total = (
            nat_score * 0.30 +      # Natural relation 30%
            avg_dignity * 0.40 +    # Dignity 40%
            aspect_score * 0.20 +   # Aspect 20%
            house_score * 0.10      # House 10%
        )
        return round(total, 1)
    
    def get_rating_label(self, percent):
        """ရာခိုင်နှုန်းအလိုက် အဆင့်သတ်မှတ်ခြင်း"""
        if percent >= 85: return "🟢 အလွန်ကောင်း", "#27ae60"
        elif percent >= 70: return "🔵 ကောင်း", "#2980b9"
        elif percent >= 55: return "🟡 သင့်တင့်", "#f39c12"
        elif percent >= 40: return "🟠 အားနည်း", "#e67e22"
        else: return "🔴 ရန်ဘက်", "#c0392b"
    
    def update_analysis(self, planet_data, houses_cusps=None):
        """ဂြိုဟ်ဒေတာမှ ပေါင်းစပ်ခွဲခြမ်းစိတ်ဖြာချက် ဇယားဖန်တီးခြင်း"""
        planets = [p for p in planet_data if p['name'] in 
                  ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']]
        
        # Natural relations lookup
        natural_rels = {
            'Sun': {'Moon':'friend','Mars':'friend','Jupiter':'friend','Venus':'enemy','Saturn':'enemy','Mercury':'neutral'},
            'Moon': {'Sun':'friend','Mercury':'friend','Mars':'neutral','Jupiter':'neutral','Venus':'neutral','Saturn':'neutral'},
            'Mars': {'Sun':'friend','Moon':'friend','Jupiter':'friend','Mercury':'enemy','Saturn':'neutral'},
            'Mercury': {'Sun':'friend','Venus':'friend','Moon':'enemy','Mars':'neutral','Jupiter':'neutral','Saturn':'neutral'},
            'Jupiter': {'Sun':'friend','Moon':'friend','Mars':'friend','Mercury':'enemy','Venus':'enemy','Saturn':'neutral'},
            'Venus': {'Mercury':'friend','Saturn':'friend','Sun':'enemy','Moon':'enemy','Mars':'neutral','Jupiter':'neutral'},
            'Saturn': {'Mercury':'friend','Venus':'friend','Sun':'enemy','Moon':'enemy','Mars':'enemy','Jupiter':'neutral'},
            'Rahu': {'Mercury':'friend','Venus':'friend','Saturn':'friend','Sun':'enemy','Moon':'enemy'},
            'Ketu': {'Mars':'friend','Jupiter':'friend','Saturn':'friend','Sun':'enemy','Venus':'enemy'}
        }
        
        self.table.setRowCount(len(planets))
        
        for i, p1 in enumerate(planets):
            name1 = p1['name']
            lon1 = p1['longitude']
            lon1_d9 = self.calculate_d9_longitude(lon1)  # Helper function needed
            
            # Calculate Dignity for planet 1
            dignity1 = self.calculate_dignity_score(name1, lon1, lon1_d9, planet_data)
            
            # Get house position
            house1 = self.get_house_number(lon1, houses_cusps) if houses_cusps else (int(lon1//30) + 1)
            
            # Natural relation with a reference planet (e.g., Lagna lord or Moon)
            ref_planet = next((p for p in planets if p['name'] == 'Moon'), planets[0])
            nat_rel = natural_rels.get(name1, {}).get(ref_planet['name'], 'neutral')
            
            # Aspect score with reference planet
            aspect_score = self.calculate_aspect_score(name1, lon1, ref_planet['name'], ref_planet['longitude'])
            
            # House score with reference planet
            house2 = self.get_house_number(ref_planet['longitude'], houses_cusps) if houses_cusps else (int(ref_planet['longitude']//30) + 1)
            house_score = self.calculate_house_score(house1, house2)
            
            # Combined percentage
            combined = self.calculate_combined_percentage(nat_rel, dignity1, 50, aspect_score, house_score)
            label, color = self.get_rating_label(combined)
            
            # Fill row
            self.table.setItem(i, 0, QTableWidgetItem(f"{name1}"))
            self.table.setItem(i, 1, QTableWidgetItem(nat_rel.upper()))
            self.table.setItem(i, 2, QTableWidgetItem(f"{dignity1:.0f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{aspect_score:.0f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"House {house1}"))
            
            # Progress bar for total
            progress = QProgressBar()
            progress.setValue(int(combined))
            progress.setFormat(f"{combined}%")
            progress.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
            progress.setTextVisible(True)
            self.table.setCellWidget(i, 5, progress)
            
            self.table.setItem(i, 6, QTableWidgetItem(label))
            
            # Center align text items
            for col in range(7):
                item = self.table.item(i, col)
                if item: item.setTextAlignment(Qt.AlignCenter)
        
        self.table.resizeColumnsToContents()
    
    def calculate_d9_longitude(self, lon_d1):
        """D9 (Navamsa) longitude တွက်ချက်ခြင်း"""
        sign_d1 = int(lon_d1 // 30)
        deg_in_sign = lon_d1 % 30
        amsa_len = 30.0 / 9.0
        amsa_idx = int(deg_in_sign / amsa_len)
        d9_sign = (sign_d1 * 9 + amsa_idx) % 12
        return d9_sign * 30 + (deg_in_sign % amsa_len)
    
    def get_house_number(self, longitude, cusps):
        """ဂြိုဟ်၏ လောင်ဂျီတွဒ်အရ အိမ်နံပါတ် (1-12) တွက်ချက်ခြင်း"""
        if not cusps or len(cusps) < 2:
            return int(longitude // 30) + 1
        c_list = cusps[:12]
        for i in range(12):
            c1, c2 = c_list[i], c_list[(i+1)%12]
            if c1 <= c2:
                if c1 <= longitude < c2: return i+1
            else:
                if longitude >= c1 or longitude < c2: return i+1
        return 12