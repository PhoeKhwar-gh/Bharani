# chart_widget.py

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
import math

# ရာသီအမည်များ (Burmese Zodiac Names)
ZODIAC_SIGNS_MM = [
    "မိဿ", "ပြိဿ", "မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်",
    "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုံ", "မိန်"
]


class BurmeseChartWidget(QWidget):
    """
    Center Frame တွင် ပုံဖော်ပြရန် Widget (400x400)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # မူလတန်ဖိုးများ
        self.planet_data = [] 
        self.show_degrees = True  # Default: show degrees
        self.chart_type = "ရာသီ"  # Default chart type
        
        # === Size ကို 400x400 သတ်မှတ်ခြင်း ===
        self.setFixedSize(400, 400)
        
        # Grid အတွက် Cell Size
        self.cell_size = 60 
        
        # Center Point (400 / 2)
        self.center_x = 200
        self.center_y = 200
        
        # === FONT SIZES (ဒီနေရာမှာ ပြောင်းပါ) ===
        # ဂြိုဟ်သင်္ကေတ အရွယ်အစား (သေးချင်/ကြီးချင် ဒီကိန်းကို ပြောင်းပါ)
        SYMBOL_SIZE = 11
        # ဒီဂရီ/မိနစ် အရွယ်အစား
        DEGREE_SIZE = 7
        # အလယ်ဗဟို ဇာတာအမည် အရွယ်အစား
        CHART_NAME_SIZE = 14
        # ရာသီ/ဘာဝ/နဝင်း စာသား အရွယ်အစား
        ZODIAC_TYPE_SIZE = 10
        
        # Font များအတွက် mapping
        self._font_sizes = {
            "ရာသီ": {"symbol": SYMBOL_SIZE, "degree": DEGREE_SIZE, "chart_name": CHART_NAME_SIZE, "zodiac_type": ZODIAC_TYPE_SIZE},
            "ဘာဝ": {"symbol": SYMBOL_SIZE, "degree": 0, "chart_name": CHART_NAME_SIZE, "zodiac_type": ZODIAC_TYPE_SIZE},
            "နဝင်း": {"symbol": SYMBOL_SIZE, "degree": 0, "chart_name": CHART_NAME_SIZE, "zodiac_type": ZODIAC_TYPE_SIZE}
        }
        
        # Default fonts
        self._symbol_font = QFont("Pyidaungsu", SYMBOL_SIZE)
        self._degree_font = QFont("Pyidaungsu", DEGREE_SIZE)
        self._chart_name_font = QFont("Pyidaungsu", CHART_NAME_SIZE, QFont.Bold)
        self._zodiac_type_font = QFont("Pyidaungsu", ZODIAC_TYPE_SIZE)
        
        # Chart type mapping for center display
        self.center_text_map = {
            "ရာသီစက်": "ရာသီ",
            "ရာသီ": "ရာသီ",
            "Rasi": "ရာသီ",
            "Rasi (D1)": "ရာသီ",
            "D1": "ရာသီ",
            "Bhava": "ဘာဝ",
            "Bhava Chalit": "ဘာဝ",
            "Navamsa": "နဝင်း",
            "Navamsa (D9)": "နဝင်း",
            "ဘာဝစက်": "ဘာဝ",
            "နဝင်းစက်": "နဝင်း"
        }
        
        self.chart_title = ""  # Full chart name (D1 - Rāśi, D2 - Hora, etc.)
        self.zodiac_type = "ရာသီ"  # Zodiac type (ရာသီ, ဘာဝ, နဝင်း, etc.)
    
    def set_planet_data(self, planet_data, show_degrees=True, chart_type="ရာသီစက်"):
        """
        planet_data: list of dicts with keys: id, symbol, sign, deg, min, retro
        show_degrees: False for Navamsa (symbols only)
        chart_type: ရာသီစက်, ဘာဝစက်, နဝင်းစက်
        """
        self.planet_data = planet_data
        self.show_degrees = show_degrees
        
        if chart_type:
            self.chart_title = chart_type  # Store full chart name (D1 - Rāśi, etc.)
            
            # Determine zodiac type for bottom center
            self.zodiac_type = "ရာသီ"  # default
            
            if "ရာသီ" in chart_type or "Rasi" in chart_type or "D1" in chart_type:
                self.zodiac_type = "ရာသီ"
            elif "ဘာဝ" in chart_type or "Bhava" in chart_type:
                self.zodiac_type = "ဘာဝ"
            elif "နဝင်း" in chart_type or "Navamsa" in chart_type:
                self.zodiac_type = "နဝင်း"
            elif "Hora" in chart_type or "D2" in chart_type:
                self.zodiac_type = "ဟောရာ"
            elif "Saptāṁśa" in chart_type or "D7" in chart_type:
                self.zodiac_type = "သတ္တံသ"
            elif "Daśāṁśa" in chart_type or "D10" in chart_type:
                self.zodiac_type = "ဒဿံသ"
            elif "Dvādashāṁśa" in chart_type or "D12" in chart_type:
                self.zodiac_type = "ဒွါဒဿံသ"
            elif "Vimshāṁśa" in chart_type or "D20" in chart_type:
                self.zodiac_type = "ဝိံသံသ"
            elif "Trimshāṁśa" in chart_type or "D30" in chart_type:
                self.zodiac_type = "တြိံသံသ"
            elif "Shashtyāṁśa" in chart_type or "D60" in chart_type:
                self.zodiac_type = "သဋ္ဌိံသ"

            
            # Update fonts based on chart type
            chart_key = None
            if self.zodiac_type in ["ရာသီ", "ဘာဝ", "နဝင်း"]:
                chart_key = self.zodiac_type
            else:
                chart_key = "ရာသီ"  # default
            
            if chart_key in self._font_sizes:
                sizes = self._font_sizes[chart_key]
                
                # ဂြိုဟ်သင်္ကေတ ဖောင့်ဆိုဒ်
                self._symbol_font = QFont("Pyidaungsu", sizes["symbol"])
                
                # ဒီဂရီ/မိနစ် ဖောင့်ဆိုဒ်
                if sizes["degree"] > 0:
                    self._degree_font = QFont("Pyidaungsu", sizes["degree"])
                
                # ဇာတာအမည် ဖောင့်ဆိုဒ်
                self._chart_name_font = QFont("Pyidaungsu", sizes["chart_name"], QFont.Bold)
                
                # ရာသီအမျိုးအစား ဖောင့်ဆိုဒ်
                self._zodiac_type_font = QFont("Pyidaungsu", sizes["zodiac_type"])
    
            self.update()

   
    
    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)

            # Background (အခြေခံအပြာရင့်)
            #painter.fillRect(self.rect(), QColor(228, 228, 230, int(0.812 * 255)))

            # === စတုရန်းပုံသဏ္ဍာန် သတ်မှတ်ချက်များ ===
            square_size = 395  # 400x400 အတွင်း 360x360 စတုရန်း
            margin = (400 - square_size) // 2  # margin = 20
            
            # === ဇာတာကွက်တစ်ခုလုံး နောက်ခံအရောင်ခွဲခြားခြင်း ===
            if self.chart_title:
                chart_code = self.chart_title[:3].strip()
                
                # အုပ်စုအလိုက် နောက်ခံအရောင်များ
                if chart_code in ["D1", "D2", "D7"]:
                    bg_color = QColor(230, 245, 255)  # အပြာဖျော့
                elif chart_code in ["D9", "D10", "D12"]:
                    bg_color = QColor(255, 255, 220)  # အဝါဖျော့
                elif chart_code in ["D20", "D30", "D60"]:
                    bg_color = QColor(230, 255, 230)  # အစိမ်းဖျော့
                else:
                    bg_color = QColor(255, 255, 255)
                
                # စတုရန်းနောက်ခံဆွဲခြင်း
                painter.fillRect(QRectF(margin, margin, square_size, square_size), bg_color)
            
            # === ⭐⭐⭐ Grid ဆွဲခြင်း - Grid ကို ထင်ထင်ရှားရှားမြင်ရအောင် မဲမဲဆွဲမယ် ⭐⭐⭐ ===
            pen = QPen(Qt.black, 2)
            painter.setPen(pen)
            self.draw_grid(painter)
            
            # Chart name ဆွဲခြင်း
            if self.chart_title:
                painter.setPen(Qt.black)
                chart_code = self.chart_title[:3].strip()
                painter.setFont(QFont("Pyidaungsu", 16, QFont.Bold))
                
                # === မြန်မာအမည်များ ထည့်သွင်းခြင်း ===
                burmese_chart_names = {
                    "D1": "ရာသီ",
                    "D2": "ဟောရာ",
                    "D3": "တြိကဏ",
                    "D4": "စတုတ္ထံသ",
                    "D5": "ပဉ္စမံသ",
                    "D7": "သတ္တမံသ",
                    "D9": "နဝင်း",
                    "D10": "ဒသမံသ",
                    "D12": "ဒွါဒသမံသ",
                    "D20": "ဝိံသမံသ",
                    "D30": "တြိံသမံသ",
                    "D60": "သဋ္ဌိမံသ",
                    "Bha": "ဘာဝ"}
                
                chart_name= burmese_chart_names.get(chart_code, chart_code)
               
                # Y Position
                y_pos = 180
                if chart_code in ["D1", "D2", "D7"]:
                    y_pos = 180
                elif chart_code in ["D9", "D10", "D12"]:
                    y_pos = 180
                elif chart_code in ["D20", "D30", "D60"]:
                    y_pos = 180
                    
                painter.drawText(QRectF(0, y_pos, 400, 50), Qt.AlignCenter, chart_name)
            # Planet symbols / degree strings
            self.draw_planets(painter)


        except Exception as e:
            print(f"Error paintEvent in BurmeseChartWidget  rid: {e}")
        finally:
            painter.end()
        
    def draw_grid(self, painter):
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        
        c_x, c_y, cell = self.center_x, self.center_y, self.cell_size
        
        # Vertical Lines
        painter.drawLine(int(c_x - cell), int(c_y - 5*cell), 
                        int(c_x - cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y - 5*cell), 
                        int(c_x + cell), int(c_y + 5*cell))
        
        # Horizontal Lines
        painter.drawLine(int(c_x - 5*cell), int(c_y - cell), 
                        int(c_x + 5*cell), int(c_y - cell))
        painter.drawLine(int(c_x - 5*cell), int(c_y + cell), 
                        int(c_x + 5*cell), int(c_y + cell))
        
        # Diagonal Lines (Diamond Shape)
        painter.drawLine(int(c_x - 5*cell), int(c_y - 5*cell), 
                        int(c_x - cell), int(c_y - cell))
        painter.drawLine(int(c_x + 5*cell), int(c_y - 5*cell), 
                        int(c_x + cell), int(c_y - cell))
        painter.drawLine(int(c_x - cell), int(c_y + cell), 
                        int(c_x - 5*cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y + cell), 
                        int(c_x + 5*cell), int(c_y + 5*cell))

    def get_zodiac_positions(self):
        """ရာသီအမည်များ ထားရမည့်နေရာများ"""

        # === 1. Rasi (D1) အတွက် မူရင်း ကိန်းဂဏာန်းများ ===
        base_coordsRasi = [
            ("မိဿ", 270, 20), ("ပြိဿ", 155, 20), ("မေထုန်", 85, 80),
            ("ကရကဋ်", 85, 195), ("သိဟ်", 85, 345), ("ကန်", 165, 415),
            ("တူ", 270, 345), ("ဗြိစ္ဆာ", 405, 405), ("ဓနု", 485, 345),
            ("မကာရ", 420, 195), ("ကုံ", 505, 80), ("မိန်", 405, 20)
        ]

        # === 2. အခြား Charts (Bhava, Navamsa, D60, etc.) အတွက် ကိန်းဂဏာန်းများ ===
        base_coordsOther = [
            ("မိဿ", 300, 25), ("ပြိဿ", 165, 25), ("မေထုန်", 95, 80),
            ("ကရကဋ်", 95, 195), ("သိဟ်", 100, 350), ("ကန်", 165, 415),
            ("တူ", 300, 350), ("ဗြိစ္ဆာ", 405, 405), ("ဓနု", 485, 350),
            ("မကာရ", 420, 195), ("ကုံ", 505, 85), ("မိန်", 415, 25)
        ]

        # === Chart Type အလိုက် ကိန်းဂဏာန်းများ ရွေးချယ်ခြင်း ===
        selected_coords = base_coordsOther

        if self.chart_title:
            if "Rasi" in self.chart_title or "ရာသီ" in self.chart_title or "D1" in self.chart_title:
                selected_coords = base_coordsRasi

        # === တွက်ချက်မှု Logic ===
        pos_dict = {}
        scale = 0.8
        
        for name, bx, by in selected_coords:
            x = (bx - 250) * scale + self.center_x
            y = (by - 250) * scale + self.center_y
            pos_dict[name] = QPointF(x, y)
            
        return pos_dict

    def draw_planets(self, painter):
        if not self.planet_data:
            return

        # Group by zodiac sign
        planets_by_sign = {}
        for p in self.planet_data:
            sign_name = ZODIAC_SIGNS_MM[p['sign']]
            if sign_name not in planets_by_sign:
                planets_by_sign[sign_name] = []
            planets_by_sign[sign_name].append(p)

        line_height = 20
        zodiac_positions = self.get_zodiac_positions()

        for sign_name, planets in planets_by_sign.items():
            if sign_name not in zodiac_positions:
                continue
            
            base_pos = zodiac_positions[sign_name]

            for i, p in enumerate(planets):
                # Symbol with symbol font
                painter.setFont(self._symbol_font)
                symbol_txt = f"{p['symbol']}"
                
                # Degree/minute with degree font (if applicable)
                deg_min_txt = ""
                if self.show_degrees and 'deg' in p and 'min' in p:
                    painter.setFont(self._degree_font)
                    deg_min_txt = f" {p['deg']}°{p['min']}'"
                
                # Retrograde indicator
                    # Retrograde indicator - "R" သင်္ကေတ
                retro_txt = ""
                if p.get('retro', False):
                    retro_txt = " R"  # R သင်္ကေတ ထည့်သွင်းခြင်း
                    painter.setPen(QColor(255, 0, 0))  # အနီရောင် (ရွေးချယ်ခွင့်ရှိ)
                else:
                    painter.setPen(Qt.black)
                
                # Combine text
                if deg_min_txt:
                    # Draw symbol
                    painter.setFont(self._symbol_font)
                    painter.drawText(QPointF(base_pos.x() - 60, base_pos.y() + i * line_height), symbol_txt)
                    
                    # Draw degree
                    text_width = painter.fontMetrics().horizontalAdvance(symbol_txt)
                    painter.setFont(self._degree_font)
                    painter.drawText(QPointF(base_pos.x() - 60 + text_width, base_pos.y() + i * line_height), deg_min_txt + retro_txt)
                else:
                    # Just symbol (for Navamsa)
                    painter.setFont(self._symbol_font)
                    painter.drawText(QPointF(base_pos.x() - 60, base_pos.y() + i * line_height), symbol_txt + retro_txt)
                
                painter.setPen(Qt.black)
# ----------------------------------------------------------------------
# End of BurmeseChartWidget
# ----------------------------------------------------------------------