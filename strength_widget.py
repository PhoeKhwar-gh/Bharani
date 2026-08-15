"""
strength_widget.py - ဂြိုဟ်အားဗလနှင့် ကာရက (Karaka) ဇယား (ဂန္တဝင်စနစ် - ဂြိုဟ် ၇ လုံး)
"""
from PyQt5 import QtWidgets, QtCore, QtGui  # <--- QtGui ကို ထည့်ပါ
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt5.QtGui import QPainter, QFont, QColor, QLinearGradient, QPen, QBrush, QPainterPath # <--- QPainterPath ကို ထည့်ပါ
import swisseph as swe

# ==================== ကိန်းသေများ (Constants) ====================

# ✅ ဂြိုဟ် ၇ လုံးအတွက် အမည်များ (မြန်မာ့ရိုးရာ)
PLANET_NAMES_MM = {
    swe.SUN: 'တနင်္ဂနွေ', 
    swe.MOON: 'တနင်္လာ', 
    swe.MARS: 'အင်္ဂါ', 
    swe.MERCURY: 'ဗုဒ္ဓဟူး',
    swe.JUPITER: 'ကြာသပတေး', 
    swe.VENUS: 'သောကြာ', 
    swe.SATURN: 'စနေ',
    'Sun': 'တနင်္ဂနွေ', 
    'Moon': 'တနင်္လာ', 
    'Mars': 'အင်္ဂါ', 
    'Mercury': 'ဗုဒ္ဓဟူး',
    'Jupiter': 'ကြာသပတေး', 
    'Venus': 'သောကြာ', 
    'Saturn': 'စနေ'
}

# ✅ ဂြိုဟ် ၇ လုံးအတွက် သင်္ကေတများ (မြန်မာဂဏန်းများ)
PLANET_SYMBOLS = {
    swe.SUN: '၁', 
    swe.MOON: '၂', 
    swe.MARS: '၃', 
    swe.MERCURY: '၄',
    swe.JUPITER: '၅', 
    swe.VENUS: '၆', 
    swe.SATURN: '၀',
    'Sun': '၁', 
    'Moon': '၂', 
    'Mars': '၃', 
    'Mercury': '၄',
    'Jupiter': '၅', 
    'Venus': '၆', 
    'Saturn': '၀'
}

# ✅ ဂြိုဟ်များ၏ စံအမည်များ (ဂဏန်းမပါ)
PLANET_SIMPLE_NAMES = {
    swe.SUN: 'တနင်္ဂနွေ', 
    swe.MOON: 'တနင်္လာ', 
    swe.MARS: 'အင်္ဂါ', 
    swe.MERCURY: 'ဗုဒ္ဓဟူး',
    swe.JUPITER: 'ကြာသပတေး', 
    swe.VENUS: 'သောကြာ', 
    swe.SATURN: 'စနေ',
    'Sun': 'တနင်္ဂနွေ', 
    'Moon': 'တနင်္လာ', 
    'Mars': 'အင်္ဂါ', 
    'Mercury': 'ဗုဒ္ဓဟူး',
    'Jupiter': 'ကြာသပတေး', 
    'Venus': 'သောကြာ', 
    'Saturn': 'စနေ'
}

# ✅ ကာရက (Karaka) အမည်များ မြန်မာလို
KARAKA_NAMES_MM = [
    "၁. အတ္တမာကာရက (Atmakaraka)",
    "၂. အမတ္တရုကာရက (Amatyakaraka)",
    "၃. ဘရတ္တရုကာရက (Bhratrukaraka)",
    "၄. မတ္တရုကာရက (Matrukaraka)",
    "၅. ပိတ္တရုကာရက (Pitrukaraka)",
    "၆. ပုတ္တရကာရက (Putrakaraka)",
    "၇. ဉာတိကာရက (Gnati/Gyatrikaraka)"
]

# ✅ ကာရက (Karaka) အဓိပ္ပါယ်များ
KARAKA_MEANINGS_MM = [
    "ကိုယ်တိုင်၊ စိတ်, ဝိညာဉ်",
    "စိတ်၊ ရာထူး၊ လုပ်ငန်း",
    "မွေးချင်းများ",
    "အမိ",
    "အဖ",
    "သားသမီး",
    "ဆွေမျိုး"
]

# ✅ ဂြိုဟ် ၇ လုံးအတွက် ရာသီအားဗလ
SIGN_STRENGTH = {
    swe.SUN: {'own': [4], 'exalt': [0], 'debil': [6], 'friend': [1, 3, 7], 'enemy': [5, 9], 'neutral': [2, 8, 10, 11]},
    swe.MOON: {'own': [3], 'exalt': [1], 'debil': [9], 'friend': [0, 1, 2], 'enemy': [8, 9, 10], 'neutral': [4, 5, 6, 7, 11]},
    swe.MARS: {'own': [0, 7], 'exalt': [9], 'debil': [3], 'friend': [0, 3, 4, 9, 11], 'enemy': [1, 5, 6], 'neutral': [2, 8, 10]},
    swe.MERCURY: {'own': [2, 5], 'exalt': [5], 'debil': [8], 'friend': [0, 1, 3, 4, 6], 'enemy': [3], 'neutral': [7, 9, 10, 11]},
    swe.JUPITER: {'own': [8, 11], 'exalt': [3], 'debil': [2], 'friend': [0, 1, 3, 4, 6, 7], 'enemy': [2, 5], 'neutral': [9, 10]},
    swe.VENUS: {'own': [1, 6], 'exalt': [2], 'debil': [9], 'friend': [2, 4, 5, 6, 10], 'enemy': [0, 3, 7], 'neutral': [1, 8, 9, 11]},
    swe.SATURN: {'own': [9, 10], 'exalt': [6], 'debil': [0], 'friend': [2, 4, 5, 6, 10], 'enemy': [0, 1, 3, 7], 'neutral': [8, 9, 11]},
    # String keys
    'Sun': {'own': [4], 'exalt': [0], 'debil': [6], 'friend': [1, 3, 7], 'enemy': [5, 9], 'neutral': [2, 8, 10, 11]},
    'Moon': {'own': [3], 'exalt': [1], 'debil': [9], 'friend': [0, 1, 2], 'enemy': [8, 9, 10], 'neutral': [4, 5, 6, 7, 11]},
    'Mars': {'own': [0, 7], 'exalt': [9], 'debil': [3], 'friend': [0, 3, 4, 9, 11], 'enemy': [1, 5, 6], 'neutral': [2, 8, 10]},
    'Mercury': {'own': [2, 5], 'exalt': [5], 'debil': [8], 'friend': [0, 1, 3, 4, 6], 'enemy': [3], 'neutral': [7, 9, 10, 11]},
    'Jupiter': {'own': [8, 11], 'exalt': [3], 'debil': [2], 'friend': [0, 1, 3, 4, 6, 7], 'enemy': [2, 5], 'neutral': [9, 10]},
    'Venus': {'own': [1, 6], 'exalt': [2], 'debil': [9], 'friend': [2, 4, 5, 6, 10], 'enemy': [0, 3, 7], 'neutral': [1, 8, 9, 11]},
    'Saturn': {'own': [9, 10], 'exalt': [6], 'debil': [0], 'friend': [2, 4, 5, 6, 10], 'enemy': [0, 1, 3, 7], 'neutral': [8, 9, 11]}
}

HOUSE_STRENGTH = {
    1: 4.0, 2: 2.0, 3: 2.5, 4: 4.0, 5: 3.5, 6: 1.5,
    7: 4.0, 8: 2.0, 9: 3.5, 10: 4.0, 11: 2.5, 12: 1.5
}


# ==================== Shadbala Strength Chart (ပုံပါအတိုင်း) ====================

class PlanetStrengthChartWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.strengths = {}  # ဂြိုဟ်တွေရဲ့ Shadbala Rupas တွေ သိမ်းမယ်
        self.min_requirements = {
            'Sun': 5.0, 'Moon': 6.0, 'Mars': 5.0,
            'Mercury': 7.0, 'Jupiter': 6.5, 'Venus': 5.5, 'Saturn': 5.0
        }
        self.planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        self.planet_short = {
            'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma',
            'Mercury': 'Me', 'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa'
        }
        self.planet_names_mm = {
            'Sun': 'နေ', 'Moon': 'လ', 'Mars': 'အင်္ဂါ',
            'Mercury': 'ဗုဒ္ဓဟူး', 'Jupiter': 'ကြာသပတေး',
            'Venus': 'သောကြာ', 'Saturn': 'စနေ'
        }
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")
    
    def update_strengths(self, strengths_data):
        """strengths_data က ဂြိုဟ်တစ်လုံးချင်းစီရဲ့ Shadbala Rupas တွေ"""
        self.strengths = strengths_data
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Background
        painter.fillRect(self.rect(), QColor("#ffffff"))
        
        # Title
        painter.setFont(QFont("Pyidaungsu", 14, QFont.Bold))
        painter.setPen(QColor("#2c3e50"))
        # Title is now handled by the Label in the parent widget, so we can skip drawing it here or keep it small
        # painter.drawText(QRectF(0, 5, w, 30), Qt.AlignCenter, "Shadbala Strength") 
        
        # Chart area settings
        chart_top = 40
        chart_bottom = h - 60
        chart_height = chart_bottom - chart_top
        
        # Column settings
        col_width = 65
        gap = 15
        total_width = len(self.planet_order) * col_width + (len(self.planet_order) - 1) * gap
        start_x = (w - total_width) / 2
        
        # Draw Base Line (1.0)
        base_y = chart_top + chart_height * 0.5
        painter.setPen(QPen(QColor("#bdc3c7"), 1, Qt.DashLine))
        painter.drawLine(int(start_x), int(base_y), int(start_x + total_width), int(base_y))
        
        # Draw Grid Lines & Labels
        painter.setFont(QFont("Pyidaungsu", 9))
        painter.setPen(QColor("#95a5a6"))
        
        # 2.0, 1.5, 1.0, 0.5, 0.0 Labels
        labels = [("2.0", 0.0), ("1.5", 0.25), ("1.0", 0.5), ("0.5", 0.75), ("0.0", 1.0)]
        for text, ratio in labels:
            y = chart_top + (chart_height * ratio)
            painter.drawText(int(start_x - 35), int(y + 4), text)
            if ratio != 0.5: # Skip drawing line for 1.0 as we drew it dashed above
                painter.setPen(QPen(QColor("#ecf0f1"), 1))
                painter.drawLine(int(start_x), int(y), int(start_x + total_width), int(y))
                painter.setPen(QColor("#95a5a6"))

        # Draw Columns
        for i, planet_id in enumerate(self.planet_order):
            x = start_x + i * (col_width + gap)
            
            rupa = self.strengths.get(planet_id, 0)
            min_req = self.min_requirements.get(planet_id, 5.0)
            ratio = rupa / min_req if min_req > 0 else 0
            
            # Bar Height Calculation
            max_ratio = 2.2 # Allow a bit more space above 2.0
            bar_height = (ratio / max_ratio) * chart_height
            if bar_height > chart_height: bar_height = chart_height
            
            # Gradient Color for Bars
            if ratio >= 1.2:
                top_color = QColor("#2ecc71") # Emerald Green
                bottom_color = QColor("#27ae60")
            elif ratio >= 1.0:
                top_color = QColor("#3498db") # Blue
                bottom_color = QColor("#2980b9")
            elif ratio >= 0.8:
                top_color = QColor("#f1c40f") # Yellow
                bottom_color = QColor("#f39c12")
            else:
                top_color = QColor("#e74c3c") # Red
                bottom_color = QColor("#c0392b")
            
            # Create Gradient
            gradient = QLinearGradient(x, base_y - bar_height, x, base_y)
            gradient.setColorAt(0, top_color)
            gradient.setColorAt(1, bottom_color)
            
            # Draw Bar (Rounded Rect)
            bar_rect = QRectF(x + 2, base_y - bar_height, col_width - 4, bar_height)
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(top_color.darker(120), 1))
            
            # Draw Rounded Rectangle manually for better look
            path = QtGui.QPainterPath()
            path.addRoundedRect(bar_rect, 5, 5)
            painter.drawPath(path)
            
            # Draw Value Text
            painter.setFont(QFont("Pyidaungsu", 10, QFont.Bold))
            value_text = f"{ratio:.2f}"
            
            # Text Position Logic
            if bar_height > 25:
                # Inside Bar (White Text)
                painter.setPen(QColor("#ffffff"))
                text_rect = QRectF(x + 2, base_y - bar_height + 5, col_width - 4, 20)
                painter.drawText(text_rect, Qt.AlignCenter, value_text)
            else:
                # Outside Bar (Dark Text)
                painter.setPen(QColor("#2c3e50"))
                if ratio >= 1.0:
                    text_rect = QRectF(x + 2, base_y - bar_height - 20, col_width - 4, 20)
                else:
                    text_rect = QRectF(x + 2, base_y + 5, col_width - 4, 20)
                painter.drawText(text_rect, Qt.AlignCenter, value_text)
            
            # Draw Planet Symbol & Name
            # Symbol (Large)
            painter.setFont(QFont("Pyidaungsu", 12, QFont.Bold))
            painter.setPen(QColor("#2c3e50"))
            symbol_rect = QRectF(x + 2, base_y + 25, col_width - 4, 20)
            painter.drawText(symbol_rect, Qt.AlignCenter, self.planet_short.get(planet_id, ''))
            
            # Name (Small, Gray)
            painter.setFont(QFont("Pyidaungsu", 9))
            painter.setPen(QColor("#7f8c8d"))
            name_rect = QRectF(x + 2, base_y + 42, col_width - 4, 18)
            painter.drawText(name_rect, Qt.AlignCenter, self.planet_names_mm.get(planet_id, ''))
        
        # Footer Note
        painter.setFont(QFont("Pyidaungsu", 8))
        painter.setPen(QColor("#bdc3c7"))
        painter.drawText(QRectF(10, h - 20, w - 20, 20), Qt.AlignRight, "Strength Ratio = Shadbala Rupas / Minimum Requirement")
        
        painter.end()


#========================= ဘာဝ ဗလ ဇယားတွက်ပုံ ====================

class BhavaBalaCalculator:
    """ဘာဝဗလ တွက်ချက်ခြင်း"""
    
    def __init__(self):
        self.bhava_strengths = {}
    
    def calculate_bhava_bala(self, planet_data, asc_longitude, house_cusps):
        """
        Bhava Bala (ဘာဝဗလ) တွက်ချက်ခြင်း
        ဘာဝတစ်ခုချင်းစီ၏ အားကို တွက်ချက်သည်
        
        Parameters:
        -----------
        planet_data : list - ဂြိုဟ်များ၏အချက်အလက်
        asc_longitude : float - လဂ်၏ဒီဂရီ
        house_cusps : list - အိမ်စွန်းများ
        """
        # အိမ် ၁၂ လုံး၏ အားများကို သတ်မှတ်ခြင်း
        bhava_strengths = {}
        
        # အိမ်အမျိုးအစားများ
        kendras = [1, 4, 7, 10]      # ကင်္ျအိမ်များ - အားအပြင်းဆုံး
        panapharas = [2, 5, 8, 11]   # ပနဖရအိမ်များ - အားအလယ်အလတ်
        apoklimas = [3, 6, 9, 12]    # အပိုကလိမာအိမ်များ - အားအနည်းဆုံး
        
        # အိမ်တစ်ခုချင်းစီအတွက် အားတွက်ချက်ခြင်း
        for house in range(1, 13):
            # အခြေခံအိမ်အား
            if house in kendras:
                base_strength = 60.0  # ကင်္ျအိမ်များ
            elif house in panapharas:
                base_strength = 30.0  # ပနဖရအိမ်များ
            else:
                base_strength = 15.0  # အပိုကလိမာအိမ်များ
            
            # အိမ်၏အကျယ်အဝန်းအရ အားထပ်ပေါင်းခြင်း
            house_width = self.calculate_house_width(house, house_cusps)
            width_bonus = house_width * 0.5  # အိမ်ကျယ်လေအားများလေ
            
            # ဂြိုဟ်များ၏အားပေါင်းခြင်း
            planet_strength = self.calculate_planets_in_house_strength(house, planet_data)
            
            # စုစုပေါင်းအား
            total_strength = base_strength + width_bonus + planet_strength
            
            bhava_strengths[house] = {
                'base_strength': base_strength,
                'width_bonus': width_bonus,
                'planet_strength': planet_strength,
                'total_strength': total_strength,
                'planets_in_house': self.get_planets_in_house(house, planet_data)
            }
        
        return bhava_strengths
    
    def calculate_house_width(self, house, house_cusps):
        """အိမ်၏အကျယ်အဝန်းတွက်ချက်ခြင်း"""
        if len(house_cusps) < 13:
            return 30.0  # Default value
            
        if house == 12:
            # 12th house width = cusp1 + 360 - cusp12
            width = (house_cusps[0] + 360) - house_cusps[11]
        else:
            width = house_cusps[house] - house_cusps[house-1]
        
        # Normalize to 0-360 range
        if width < 0:
            width += 360
        return width
    
    def calculate_planets_in_house_strength(self, house, planet_data):
        """အိမ်တစ်ခုအတွင်းရှိ ဂြိုဟ်များ၏အားပေါင်းခြင်း"""
        total_strength = 0
        planets_in_house = self.get_planets_in_house(house, planet_data)
        
        for planet in planets_in_house:
            # ဂြိုဟ်အမျိုးအစားအလိုက်အား
            planet_type_strength = self.get_planet_type_strength(planet)
            
            # ဂြိုဟ်၏အိမ်အတွင်းတည်နေရာအားအလိုက်အား
            position_strength = self.get_planet_position_strength(planet, house)
            
            total_strength += planet_type_strength + position_strength
        
        return total_strength
    
    def get_planets_in_house(self, house, planet_data):
        """အိမ်တစ်ခုအတွင်းရှိ ဂြိုဟ်များစာရင်း"""
        planets = []
        for planet in planet_data:
            if planet.get('house') == house:
                planets.append(planet)
        return planets
    
    def get_planet_type_strength(self, planet):
        """ဂြိုဟ်အမျိုးအစားအလိုက်အား"""
        planet_id = planet.get('id')
        
        # ကျေးဇူးပြုဂြိုဟ်များ
        benefics = [swe.JUPITER, swe.VENUS, swe.MOON, 'Jupiter', 'Venus', 'Moon']
        # အန္တရာယ်ပေးဂြိုဟ်များ
        malefics = [swe.SATURN, swe.MARS, swe.SUN, 'Saturn', 'Mars', 'Sun']
        # ကြားခံဂြိုဟ်များ
        neutrals = [swe.MERCURY, 'Mercury']
        
        if planet_id in benefics:
            return 10.0
        elif planet_id in malefics:
            return 5.0
        else:
            return 7.5
    
    def get_planet_position_strength(self, planet, house):
        """ဂြိုဟ်၏အိမ်အတွင်းတည်နေရာအား"""
        longitude = planet.get('longitude', 0)
        
        # အိမ်၏အစကနေ ဂြိုဟ်၏အကွာအဝေး
        if hasattr(self, 'house_cusps') and len(self.house_cusps) > house:
            house_start = self.house_cusps[house-1]
            distance_in_house = (longitude - house_start) % 360
            
            # အိမ်၏အလယ်ဗဟိုနားရောက်လေအားများလေ
            house_width = self.calculate_house_width(house, self.house_cusps)
            distance_from_center = abs(distance_in_house - (house_width / 2))
            
            # ဗဟိုနီးလေအားများလေ
            center_strength = max(0, 10 - (distance_from_center * 0.2))
            return center_strength
        
        return 5.0


class BhavaBalaWidget(QtWidgets.QWidget):
    """ဘာဝဗလ ဇယားဖော်ပြခြင်း"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bhava_data = {}
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
    
    def update_bhava_bala(self, bhava_data):
        self.bhava_data = bhava_data
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Header
        painter.setFont(QFont("Pyidaungsu", 14, QFont.Bold))
        painter.setPen(QColor(139, 69, 19))
        painter.drawText(QRectF(0, 15, self.width(), 30), Qt.AlignCenter, "🏠 Bhava Bala - ဘာဝဗလ")
        
        y_offset = 60
        row_height = 35
        header_height = 40
        
        # Column widths
        col_widths = {
            'bhava': 80,        # ဘာဝ
            'name': 120,         # အမည်
            'base': 80,          # အခြေခံအား
            'width': 80,         # အကျယ်အားဖြည့်
            'planets': 120,      # ဂြိုဟ်အားပေါင်း
            'total': 100,        # စုစုပေါင်း
            'planets_list': 200  # ဂြိုဟ်စာရင်း
        }
        
        table_width = sum(col_widths.values())
        margin = (self.width() - table_width) / 2
        
        # Header background
        painter.setBrush(QColor(52, 73, 94))
        painter.setPen(Qt.NoPen)
        painter.drawRect(int(margin), int(y_offset), int(table_width), int(header_height))
        
        # Header text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Pyidaungsu", 10, QFont.Bold))
        
        x_pos = margin
        headers = [
            ("ဘာဝ", col_widths['bhava']),
            ("အမည်", col_widths['name']),
            ("အခြေခံအား", col_widths['base']),
            ("အကျယ်အား", col_widths['width']),
            ("ဂြိုဟ်အား", col_widths['planets']),
            ("စုစုပေါင်း", col_widths['total']),
            ("ဂြိုဟ်များ", col_widths['planets_list'])
        ]
        
        for header, width in headers:
            painter.drawText(QRectF(x_pos, y_offset, width, header_height), 
                           Qt.AlignCenter, header)
            x_pos += width
        
        y_offset += header_height
        
        # Bhava names in Myanmar
        bhava_names = {
            1: "တနင်္ဂနွေ (လဂ်)",
            2: "တနင်္လာ (ဒြပွန)",
            3: "အင်္ဂါ (သဟဇာတ)",
            4: "ဗုဒ္ဓဟူး (ဗန္ဓ)",
            5: "ကြာသပတေး (ပုတ္တ)",
            6: "သောကြာ (အာတာဝ)",
            7: "စနေ (ယုဂ)",
            8: "အာတာဝ (မရဏ)",
            9: "ဒြပွန (ဓန)",
            10: "သဟဇာတ (ကာမ)",
            11: "ဗန္ဓ (လာဘ)",
            12: "ပုတ္တ (ဝယ)"
        }
        
        # House types
        kendra_houses = [1, 4, 7, 10]
        panaphara_houses = [2, 5, 8, 11]
        apoklima_houses = [3, 6, 9, 12]
        
        for house in range(1, 13):
            if house not in self.bhava_data:
                continue
                
            data = self.bhava_data[house]
            
            # Row background based on house type
            if house in kendra_houses:
                bg_color = QColor(220, 245, 220)  # Light green for kendras
            elif house in panaphara_houses:
                bg_color = QColor(245, 245, 220)  # Light yellow for panapharas
            else:
                bg_color = QColor(245, 220, 220)  # Light red for apoklimas
            
            painter.setBrush(bg_color)
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(margin), int(y_offset), int(table_width), int(row_height))
            
            # Border
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.drawLine(int(margin), int(y_offset), int(margin + table_width), int(y_offset))
            
            # Data
            painter.setPen(QColor(44, 62, 80))
            painter.setFont(QFont("Pyidaungsu", 9))
            
            x_pos = margin
            
            # ဘာဝနံပါတ်
            painter.drawText(QRectF(x_pos, y_offset, col_widths['bhava'], row_height), 
                           Qt.AlignCenter, str(house))
            x_pos += col_widths['bhava']
            
            # ဘာဝအမည်
            bhava_name = bhava_names.get(house, f"ဘာဝ {house}")
            painter.drawText(QRectF(x_pos, y_offset, col_widths['name'], row_height), 
                           Qt.AlignCenter, bhava_name)
            x_pos += col_widths['name']
            
            # အခြေခံအား
            base_str = data.get('base_strength', 0)
            painter.drawText(QRectF(x_pos, y_offset, col_widths['base'], row_height), 
                           Qt.AlignCenter, f"{base_str:.1f}")
            x_pos += col_widths['base']
            
            # အကျယ်အား
            width_str = data.get('width_bonus', 0)
            painter.drawText(QRectF(x_pos, y_offset, col_widths['width'], row_height), 
                           Qt.AlignCenter, f"{width_str:.1f}")
            x_pos += col_widths['width']
            
            # ဂြိုဟ်အား
            planet_str = data.get('planet_strength', 0)
            painter.drawText(QRectF(x_pos, y_offset, col_widths['planets'], row_height), 
                           Qt.AlignCenter, f"{planet_str:.1f}")
            x_pos += col_widths['planets']
            
            # စုစုပေါင်း
            total_str = data.get('total_strength', 0)
            painter.setFont(QFont("Pyidaungsu", 9, QFont.Bold))
            painter.drawText(QRectF(x_pos, y_offset, col_widths['total'], row_height), 
                           Qt.AlignCenter, f"{total_str:.1f}")
            x_pos += col_widths['total']
            
            # ဂြိုဟ်များ
            planets_list = data.get('planets_in_house', [])
            planet_names = []
            for planet in planets_list:
                planet_id = planet.get('id')
                planet_name = self.get_planet_name(planet_id)
                planet_names.append(planet_name)
            
            planets_text = ", ".join(planet_names) if planet_names else "-"
            painter.setFont(QFont("Pyidaungsu", 8))
            painter.drawText(QRectF(x_pos, y_offset, col_widths['planets_list'], row_height), 
                           Qt.AlignCenter, planets_text)
            
            y_offset += row_height
        
        # Final border
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawLine(int(margin), int(y_offset), int(margin + table_width), int(y_offset))
        
        # Summary
        y_offset += 20
        painter.setFont(QFont("Pyidaungsu", 10, QFont.Bold))
        painter.setPen(QColor(139, 69, 19))
        
        # Find strongest and weakest houses
        if self.bhava_data:
            sorted_houses = sorted(self.bhava_data.items(), 
                                 key=lambda x: x[1].get('total_strength', 0), reverse=True)
            
            strongest = sorted_houses[0] if sorted_houses else (0, {})
            weakest = sorted_houses[-1] if sorted_houses else (0, {})
            
            summary_text = f"အားအပြင်းဆုံးဘာဝ: {strongest[0]} ({strongest[1].get('total_strength', 0):.1f}) | "
            summary_text += f"အားအနည်းဆုံးဘာဝ: {weakest[0]} ({weakest[1].get('total_strength', 0):.1f})"
            
            painter.drawText(QRectF(margin, y_offset, table_width, 25), 
                           Qt.AlignCenter, summary_text)
        
        painter.end()
    
    def get_planet_name(self, planet_id):
        """ဂြိုဟ်အမည်ရယူခြင်း"""
        planet_names = {
            swe.SUN: 'နေ', swe.MOON: 'လ', swe.MARS: 'အင်္ဂါ',
            swe.MERCURY: 'ဗုဒ္ဓဟူး', swe.JUPITER: 'ကြာသပတေး',
            swe.VENUS: 'သောကြာ', swe.SATURN: 'စနေ',
            'Sun': 'နေ', 'Moon': 'လ', 'Mars': 'အင်္ဂါ',
            'Mercury': 'ဗုဒ္ဓဟူး', 'Jupiter': 'ကြာသပတေး',
            'Venus': 'သောကြာ', 'Saturn': 'စနေ',
            'Lagna': 'လဂ်', 'Rahu': 'ရာဟု', 'Ketu': 'ကိတ်'
        }
        return planet_names.get(planet_id, str(planet_id))


# ==================== ကာရက (Karaka) ဇယား ====================

class KarakaTableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.karakas = []
        self.setMinimumSize(320, 600)
        self.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px;")
    
    def update_karakas(self, karakas_data):
        self.karakas = karakas_data
        self.update()
        print(f"KarakaTableWidget update: {len(self.karakas)} karakas received")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Header
        painter.setFont(QFont("Pyidaungsu", 14, QFont.Bold))
        painter.setPen(QColor(139, 69, 19))
        painter.drawText(QRectF(0, 10, self.width(), 30), Qt.AlignCenter, "🌟 ကာရက ၇ ပါး")
        
        # ==================== အပေါ်ပိုင်း ဇယား (ကာရကအချက်အလက်) ====================
        y_offset = 50
        row_height = 35
        header_height = 28
        
        # ကော်လံအကျယ်များ သတ်မှတ်ခြင်း
        col_serial_width = 35      # "စဉ်"
        col_karaka_width = 150      # "ကာရက"
        col_planet_width = 150      # "ဂြိုဟ်"
        col_degree_width = 70      # "ဒီဂရီ"
        col_meaning_width = 200     # "အဓိပ္ပါယ်" (အတိုကောက်)
        
        # ကော်လံများ၏ x-position များ တွက်ချက်ခြင်း
        margin = 5
        x_serial = margin
        x_karaka = x_serial + col_serial_width + 3
        x_planet = x_karaka + col_karaka_width + 3
        x_degree = x_planet + col_planet_width + 3
        x_meaning = x_degree + col_degree_width + 3
        
        # ဇယားဘောင်ဆွဲခြင်း
        table_width = self.width() - 10
        table_height = header_height + (row_height * len(self.karakas)) + 5
        
        # အပေါ်ပိုင်းဇယားအတွက် နောက်ခံအရောင်
        painter.fillRect(int(margin), int(y_offset - 2), int(table_width), int(table_height + 4), QColor(250, 250, 250))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(int(margin), int(y_offset - 2), int(table_width), int(table_height + 4))
        
        # ===== ဇယားခေါင်းစဉ်တန်း =====
        painter.setFont(QFont("Pyidaungsu", 9, QFont.Bold))
        painter.setPen(QColor(44, 62, 80))
        painter.fillRect(int(margin), int(y_offset), int(table_width), int(header_height), QColor(52, 73, 94))
        
        # ခေါင်းစဉ်များ (အဖြူရောင်)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(x_serial, y_offset, col_serial_width, header_height), Qt.AlignCenter, "စဉ်")
        painter.drawText(QRectF(x_karaka, y_offset, col_karaka_width, header_height), Qt.AlignCenter, "ကာရက")
        painter.drawText(QRectF(x_planet, y_offset, col_planet_width, header_height), Qt.AlignCenter, "ဂြိုဟ်")
        painter.drawText(QRectF(x_degree, y_offset, col_degree_width, header_height), Qt.AlignCenter, "ဒီဂရီ")
        painter.drawText(QRectF(x_meaning, y_offset, col_meaning_width, header_height), Qt.AlignCenter, "အဓိပ္ပါယ်")
        
        y_offset += header_height
        
        # ===== ဇယားအတန်းများ =====
        for i, karaka in enumerate(self.karakas):
            if i >= 7:
                break
            
            # အတန်းအလိုက် နောက်ခံအရောင်
            if i % 2 == 0:
                painter.fillRect(int(margin), int(y_offset), int(table_width), int(row_height - 1), QColor(255, 255, 255))
            else:
                painter.fillRect(int(margin), int(y_offset), int(table_width), int(row_height - 1), QColor(240, 248, 255))
            
            # ဇယားကွက်လိုင်းများ
            painter.setPen(QPen(QColor(220, 220, 220), 1))
            painter.drawLine(int(margin), int(y_offset), int(margin + table_width), int(y_offset))
            
            painter.setFont(QFont("Pyidaungsu", 9))
            painter.setPen(QColor(44, 62, 80))
            
            # စဉ်
            painter.drawText(QRectF(x_serial, y_offset, col_serial_width, row_height), Qt.AlignCenter, str(i + 1))
            
            # ကာရက အမည် (အတိုကောက်)
            karaka_name = karaka.get('karaka_name', '')
            if karaka_name:
                parts = karaka_name.split()
                if len(parts) >= 2:
                    if '.' in parts[0]:
                        karaka_short = parts[1]
                    else:
                        karaka_short = parts[0]
                else:
                    karaka_short = karaka_name[:10]
            else:
                karaka_short = ''
            
            painter.drawText(QRectF(x_karaka, y_offset, col_karaka_width, row_height), 
                           Qt.AlignLeft, karaka_short)
            
            # ဂြိုဟ် (သင်္ကေတ + အမည်)
            planet_symbol = karaka.get('planet_symbol', '?')
            planet_name = karaka.get('planet_name', '')
            planet_text = f"{planet_symbol} {planet_name}"
            painter.drawText(QRectF(x_planet, y_offset, col_planet_width, row_height), 
                           Qt.AlignLeft, planet_text)
            
            # ဒီဂရီ (ဒီဂရီ/မိနစ်)
            deg = karaka.get('deg', 0)
            min_val = karaka.get('min', 0)
            deg_text = f"{deg}°{min_val:02d}'"
            painter.drawText(QRectF(x_degree, y_offset, col_degree_width, row_height), 
                           Qt.AlignCenter, deg_text)
            
            # အဓိပ္ပါယ် (အတိုကောက်)
            meaning = karaka.get('meaning', '')
            painter.drawText(QRectF(x_meaning, y_offset, col_meaning_width, row_height), 
                           Qt.AlignLeft, meaning)
            
            y_offset += row_height
        
        # ဇယားအောက်ခြေလိုင်း
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawLine(int(margin), int(y_offset), int(margin + table_width), int(y_offset))
        
        # ==================== အောက်ပိုင်း ဇယား (အဓိပ္ပါယ်အပြည့်အစုံ) ====================
        y_offset += 15
        meaning_header_y = y_offset
        
        # အောက်ပိုင်းဇယားခေါင်းစဉ်
        painter.setFont(QFont("Pyidaungsu", 10, QFont.Bold))
        painter.setPen(QColor(139, 69, 19))
        painter.drawText(QRectF(margin, meaning_header_y, table_width, 25), 
                        Qt.AlignCenter, "📖 ကာရကအဓိပ္ပါယ်ဖွင့်ဆိုချက်များ")
        
        y_offset += 30
        
        # အောက်ပိုင်းဇယားဘောင်
        meaning_table_height = 25 + (20 * len(self.karakas)) + 5
        painter.fillRect(int(margin), int(y_offset - 2), int(table_width), int(meaning_table_height), QColor(250, 250, 250))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(int(margin), int(y_offset - 2), int(table_width), int(meaning_table_height))
        
        # အောက်ပိုင်းဇယားခေါင်းစဉ်တန်း
        painter.setFont(QFont("Pyidaungsu", 9, QFont.Bold))
        painter.fillRect(int(margin), int(y_offset), int(table_width), 25, QColor(69, 95, 121))
        painter.setPen(QColor(255, 255, 255))
        
        # ကော်လံအကျယ်များ ပြန်သတ်မှတ်
        col_num_width = 35
        col_full_meaning_width = table_width - col_num_width - 20
        
        painter.drawText(QRectF(margin + 5, y_offset, col_num_width, 25), Qt.AlignCenter, "စဉ်")
        painter.drawText(QRectF(margin + col_num_width + 5, y_offset, col_full_meaning_width, 25), 
                        Qt.AlignCenter, "အဓိပ္ပါယ်အပြည့်အစုံ")
        
        y_offset += 25
        
        # အောက်ပိုင်းဇယားအတန်းများ
        for i, karaka in enumerate(self.karakas):
            if i >= 7:
                break
            
            # အတန်းအလိုက် နောက်ခံအရောင်
            if i % 2 == 0:
                painter.fillRect(int(margin), int(y_offset), int(table_width), 20, QColor(255, 255, 255))
            else:
                painter.fillRect(int(margin), int(y_offset), int(table_width), 20, QColor(240, 248, 255))
            
            painter.setPen(QPen(QColor(220, 220, 220), 1))
            painter.drawLine(int(margin), int(y_offset), int(margin + table_width), int(y_offset))
            
            painter.setFont(QFont("Pyidaungsu", 9))
            painter.setPen(QColor(44, 62, 80))
            
            # စဉ်
            painter.drawText(QRectF(margin + 5, y_offset, col_num_width, 20), Qt.AlignCenter, str(i + 1))
            
            # အဓိပ္ပါယ်အပြည့်အစုံ
            meaning = karaka.get('meaning', '')
            painter.drawText(QRectF(margin + col_num_width + 5, y_offset, col_full_meaning_width, 20), 
                           Qt.AlignLeft | Qt.AlignVCenter, f"  {meaning}")
            
            y_offset += 20
        
        # အောက်ဆုံးလိုင်း
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawLine(int(margin), int(y_offset), int(margin + table_width), int(y_offset))
        
        painter.end()


# ==================== ကာရက (Karaka) တွက်ချက်ခြင်း ====================

def calculate_karakas(planet_data):
    """
    ဇေမီနိ စာရကာရက (Jaimini Chara Karaka) ၇ ပါး တွက်ချက်ခြင်း
    (ဂန္တဝင်စနစ် - ဂြိုဟ် ၇ လုံး၊ ရာဟုမပါ)
    
    Parameters:
    -----------
    planet_data : list
        ဂြိုဟ်များ၏ ဒေတာစာရင်း (ဒီဂရီ၊ ရာသီ၊ အိမ် အပါအဝင်)
    
    Returns:
    --------
    list
        ကာရက ၇ ပါးစီအလိုက် ဂြိုဟ်အမည်နှင့် ဒီဂရီများ
    """
    # ဂြိုဟ် ၇ လုံးအတွက် ဒေတာစုဆောင်းမယ် (Lagna နှင့် ရာဟု မပါ)
    planets_for_karaka = []
    
    # ခွင့်ပြုဂြိုဟ်များ (ဂြိုဟ် ၇ လုံး - ရာဟုမပါ)
    allowed_planets_int = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, 
                           swe.JUPITER, swe.VENUS, swe.SATURN]
    allowed_planets_str = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    
    for planet in planet_data:
        pid = planet.get('id')
        
        # Lagna ကို ကျော်မယ်
        if pid == 'Lagna':
            continue
        
        # ဂြိုဟ်ခွင့်ပြုမပြု စစ်ဆေးခြင်း (ရာဟုကို ကျော်မယ်)
        is_allowed = False
        if isinstance(pid, int):
            if pid in allowed_planets_int:
                is_allowed = True
        elif isinstance(pid, str):
            if pid in allowed_planets_str:
                is_allowed = True
        
        if not is_allowed:
            continue
        
        # ဂြိုဟ်၏ ရာသီအတွင်းဒီဂရီ
        longitude = planet.get('longitude', 0)
        deg_in_sign = longitude % 30
        
        # ဒီဂရီကို မိနစ်အထိ တိကျအောင် သိမ်းမယ်
        deg_int = int(deg_in_sign)
        min_int = int((deg_in_sign * 60) % 60)
        sec_int = int((deg_in_sign * 3600) % 60)
        
        # ဒဿမကိန်းအဖြစ် (တိကျစွာ နှိုင်းယှဉ်ရန်)
        decimal_deg = deg_in_sign
        
        # ဂြိုဟ်အမည်ရယူခြင်း
        planet_name = PLANET_SIMPLE_NAMES.get(pid, str(pid))
        planet_symbol = PLANET_SYMBOLS.get(pid, '?')
        
        planets_for_karaka.append({
            'id': pid,
            'name': planet_name,
            'symbol': planet_symbol,
            'deg': deg_int,
            'min': min_int,
            'sec': sec_int,
            'decimal_deg': decimal_deg
        })
    
    # ဒီဂရီအများဆုံးမှ အနည်းဆုံးသို့ စီခြင်း
    planets_for_karaka.sort(key=lambda x: x['decimal_deg'], reverse=True)
    
    # ကာရက အမည်များ သတ်မှတ်ခြင်း (၇ ပါး)
    karaka_names = [
        "၁. အတ္တမာကာရက (Atmakaraka)",
        "၂. အမတ္တရုကာရက (Amatyakaraka)",
        "၃. ဘရတ္တရုကာရက (Bhratrukaraka)",
        "၄. မတ္တရုကာရက (Matrukaraka)",
        "၅. ပိတ္တရုကာရက (Pitrukaraka)",
        "၆. ပုတ္တရကာရက (Putrakaraka)",
        "၇. ဉာတိကာရက (Gnati/Gyatrikaraka)"
    ]
    
    karaka_meanings = [
        "ကိုယ်တိုင်၊ ဝိညာဉ် (Soul, Self)",
        "စိတ်၊ ရာထူး၊ လုပ်ငန်း (Mind, Career, Close associate)",
        "မွေးချင်း (Siblings, Coborn)",
        "အမိ (Mother)",
        "အဖ (Father)",
        "သားသမီး (Offspring)",
        "ဆွေမျိုး (Relatives)"
    ]
    
    karakas = []
    for i, planet in enumerate(planets_for_karaka):
        if i >= len(karaka_names):
            break
            
        karakas.append({
            'index': i + 1,
            'karaka_name': karaka_names[i],
            'meaning': karaka_meanings[i],
            'planet_id': planet['id'],
            'planet_name': planet['name'],
            'planet_symbol': planet['symbol'],
            'deg': planet['deg'],
            'min': planet['min'],
            'sec': planet['sec'],
            'decimal_deg': planet['decimal_deg']
        })
    
    return karakas


# ==================== ဂြိုဟ်အားဗလ တွက်ချက်ခြင်း ====================

def calculate_planet_strengths(planet_data, asc_sign, house_cusps=None):
    """
    ဂြိုဟ် ၇ လုံးအတွက် အားဗလ တွက်ချက်ခြင်း
    (ဂန္တဝင်စနစ် - ရာဟုမပါ)
    """
    results = {}
    
    # ဂြိုဟ် ၇ လုံးအတွက် ID များ - integer နဲ့ string နှစ်မျိုးလုံး လက်ခံမယ်
    allowed_planets = [
        swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, 
        swe.JUPITER, swe.VENUS, swe.SATURN,
        'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'
    ]
    
    # ဂြိုဟ် ၇ လုံးကိုသာ ထည့်သွင်းစဉ်းစားမယ် (Lagna, Ketu, Rahu စတာတွေ မပါ)
    for planet in planet_data:
        pid = planet.get('id')
        
        # Lagna (Ascendant) ကို ကျော်မယ်
        if pid == 'Lagna':
            continue
            
        # ဂြိုဟ် ၇ လုံးထဲမှာ ပါမပါ စစ်ဆေးခြင်း
        is_allowed = False
        
        # integer နဲ့ စစ်ဆေး
        if isinstance(pid, int):
            if pid in [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, 
                       swe.JUPITER, swe.VENUS, swe.SATURN]:
                is_allowed = True
        # string နဲ့ စစ်ဆေး
        elif isinstance(pid, str):
            if pid in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
                is_allowed = True
        
        if not is_allowed:
            continue
            
        sign = planet.get('sign', 0)
        house = planet.get('house', 1)
        is_retro = planet.get('retro', False)
        
        components = {}
        total = 0
        
        # ၁။ ရာသီအား (Rasi Bala)
        rasi_bala = calculate_rasi_bala(pid, sign)
        components['ရာသီ'] = rasi_bala
        total += rasi_bala
        
        # ၂။ အိမ်အား (Bhava Bala)
        bhava_bala = HOUSE_STRENGTH.get(house, 2.0) * 5
        components['အိမ်'] = bhava_bala
        total += bhava_bala
        
        # ၃။ ဝက္ကအား (Retrograde Bala) - ဂြိုဟ် ၅ လုံးအတွက်သာ
        retro_bala = 0
        retro_planets = [swe.MARS, swe.MERCURY, swe.JUPITER, swe.SATURN, 
                        'Mars', 'Mercury', 'Jupiter', 'Saturn']
        
        if is_retro and pid in retro_planets:
            retro_bala = 10
        components['ဝက္ကဳ'] = retro_bala
        total += retro_bala
        
        # ၄။ သဘာဝအား (Natural Strength)
        natural_order = [swe.MOON, swe.MERCURY, swe.VENUS, swe.SUN, 
                        swe.MARS, swe.JUPITER, swe.SATURN,
                        'Moon', 'Mercury', 'Venus', 'Sun', 'Mars', 'Jupiter', 'Saturn']
        
        natural_bala = 10  # Default value
        
        if pid in natural_order:
            try:
                # ဂြိုဟ်ရဲ့ သဘာဝအဆင့်ကို ရှာမယ်
                for i, p in enumerate(natural_order):
                    # integer နဲ့ string နှိုင်းယှဉ်တဲ့အခါ သတိထားရမယ်
                    if (isinstance(p, int) and isinstance(pid, int) and p == pid) or \
                       (isinstance(p, str) and isinstance(pid, str) and p == pid):
                        natural_bala = (i + 1) * (20 / 7)
                        break
            except:
                natural_bala = 10
            
        components['သဘာဝ'] = natural_bala
        total += natural_bala
        
        # ၅။ အချိန်အား (Kala Bala)
        kala_bala = 10
        # နေအတွက် Kendra ရာသီများ (Aries, Cancer, Libra, Capricorn)
        sun_kendra = [0, 3, 6, 9]
        # လအတွက် Kendra ရာသီများ (Taurus, Leo, Scorpio, Aquarius)
        moon_kendra = [1, 4, 7, 10]
        
        if pid in [swe.SUN, 'Sun'] and sign in sun_kendra:
            kala_bala = 15
        elif pid in [swe.MOON, 'Moon'] and sign in moon_kendra:
            kala_bala = 15
            
        components['အချိန်'] = kala_bala
        total += kala_bala
        
        # စုစုပေါင်း (အများဆုံး 100)
        total = min(total, 100)
        
        results[pid] = {
            'total': total,
            'components': components,
            'details': {'sign': sign, 'house': house, 'retrograde': is_retro}
        }
    
    return results


def calculate_rasi_bala(planet_id, sign):
    """ရာသီအား တွက်ချက်ခြင်း"""
    if planet_id not in SIGN_STRENGTH:
        return 15
        
    rules = SIGN_STRENGTH[planet_id]
    
    if sign in rules.get('exalt', []):
        return 30
    elif sign in rules.get('own', []):
        return 25
    elif sign in rules.get('friend', []):
        return 20
    elif sign in rules.get('neutral', []):
        return 15
    elif sign in rules.get('enemy', []):
        return 10
    elif sign in rules.get('debil', []):
        return 5
    else:
        return 15


def get_planet_strengths_for_chart(planet_data, birth_time):
    """ဇာတာအတွက် ဂြိုဟ်အားဗလများ ရယူခြင်း"""
    asc_sign = planet_data[0].get('sign', 0) if planet_data else 0
    return calculate_planet_strengths(planet_data, asc_sign)