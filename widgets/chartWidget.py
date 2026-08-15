# --------------------------------------------------------------
#  BurmeseChartWidget – 400×400 အရွယ်အစား chart widget
# --------------------------------------------------------------
import math
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtWidgets import QWidget


# font_manager import ထည့်ပါ
try:
    from ToRecDel.font_manager import ChartFontManager
except ImportError:
    # fallback အနေနဲ့
    class ChartFontManager:
        def get_font(self, chart_type, font_type):
            return QFont("Pyidaungsu", 12)
# မြန်မာ ဇာတာအမည်
ZODIAC_SIGNS_MM = [
    "မိဿ", "ပြိဿ", "မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်",
    "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုမ်", "မိန်"
]

class BurmeseChartWidget(QWidget):
    """
    • 400×400 အရွယ်အစား chart widget
    • Rasi (D1) / Bhava (D2‑3) / Navamsa (D9) တို့ကို
      အလိုအပျေ့သတ်မှတ်ထားသော font‑size များဖြင့် ပုံဆွဲနိုင်သည်
    """
    # -----------------------------------------------------------------
    #   1️⃣  Font‑size mapping (symbol / degree‑minute / chart‑title)
    # -----------------------------------------------------------------
    _font_sizes = {
        #  symbol = ဂြိုဟ်သင်္ကေတ  (၁‑၀‑…)
        #  degree =  23°45′  (အကြီးမားသော စာသား)
        #  title  =  ရာသီ / ဘာဝ / နဝင်း
        "Rasi":   {"symbol": 14, "degree": 11, "title": 14},
        "Bhava":  {"symbol": 14, "degree": 0,  "title": 14},   # degree = 0 → မပြသ
        "Navamsa":{"symbol": 14, "degree": 0,  "title": 14}
    }

    # -----------------------------------------------------------------
    # 2️⃣  fallback fonts – widget တစ်ခုတည်းဖွင့်သေးသေးအခါအသုံးပြု
    # -----------------------------------------------------------------
    _fallback_fonts = {
        "symbol": QFont("Pyidaungsu", 14),
        "degree": QFont("Pyidaungsu", 11),
        "title" : QFont("Pyidaungsu", 14, QFont.Bold)
    }

    def __init__(self, parent=None,font_manager=None):
        super().__init__(parent)

        # Font manager ကို လက်ခံခြင်း
        if font_manager is None:
            self.font_manager = ChartFontManager()
        else:
            self.font_manager = font_manager
        

        # data & UI flag
        self.planet_data   = []          # list of dicts (id, symbol, sign, …)
        self.show_degrees  = True       # Rasi / Bhava အတွက် ★   (Navamsa မှာ False)
        self.chart_type    = "Rasi (D1)" # displayed title ကို သုံးသပ်ရန်

        # widget size
        self.setFixedSize(400, 400)

        # grid‑drawing helpers
        self.center_x   = 200
        self.center_y   = 200
        self.cell_size  = 60
        #self.scale_factor = 0.7           # zodiac‑position scaling

    # ==============================================================
    # 3️⃣  PUBLIC API – data ထည့်သွင်း + chart_type သတ်မှတ်
    # ==============================================================    
    def set_planet_data(self,
                       planet_data,
                       show_degrees: bool = True,
                       chart_type: str  = "Rasi (D1)"):
        """
        Parameters
        ----------
        planet_data : list[dict]
            each dict must contain at least: id, symbol, sign, deg, min,
            retro (bool) and optionally 'longitude'.
        show_degrees : bool
            True → show °′ (Rasi / Bhava) ; False → Navamsa (symbols only)
        chart_type : str
            Accepts either the short key (Rasi, Bhava, Navamsa) *or*
            the UI‑friendly string (e.g. "Rasi (D1)", "ရာသီ", …)
        """
        self.planet_data   = planet_data
        self.show_degrees  = show_degrees
        self.chart_type    = chart_type

        

        # repaint
        self.update()

    # ==============================================================
    # 4️⃣  paintEvent – drawing routine
    # ==============================================================    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # ---- Background -------------------------------------------------
        p.fillRect(self.rect(), QColor(255, 255, 255))

        # ---- Grid -------------------------------------------------------
        self.draw_grid(p)

        # ---- Chart Title (use _title_font) -------------------------------
        title_font = self.font_manager.get_font(self.chart_type, "title")
        if title_font:
            p.setFont(title_font)
            p.setPen
            title_map = {"ရာသီ": "ရာသီ", "Rasi": "ရာသီ",
                         "ဘာဝ": "ဘာဝ", "Bhava": "ဘာဝ",
                         "နဝင်း": "နဝင်း", "Navamsa": "နဝင်း"}
            
            short_key = self.chart_type.split()[0]
            title_txt = title_map.get(short_key, short_key)

            p.drawText(QRectF(160, 184, 80, 32), Qt.AlignCenter, title_txt)
            
        # ---- Zodiac signs -----------------------------------------------
        zodiac_font = self.font_manager.get_font(self.chart_type, "zodiac")
        if zodiac_font:
            p.setFont(zodiac_font)
            self.draw_zodiac_names(p)

        # ---- Planets ----------------------------------------------------
        self.draw_planets(p)
    
    def draw_zodiac_names(self, painter):
        """ရာသီအမည်များရေးဆွဲခြင်း"""
        zodiac_pos = self.get_zodiac_positions()
        
        for sign_name, pos in zodiac_pos.items():
            painter.drawText(QRectF(pos.x() - 30, pos.y() - 10, 60, 20), 
                           Qt.AlignCenter, sign_name)

    # -----------------------------------------------------------------
    # 5️⃣  Grid drawing (unchanged from your original code)
    # -----------------------------------------------------------------
    def draw_grid(self, painter):
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        c_x, c_y, cell = self.center_x, self.center_y, self.cell_size

        # vertical
        painter.drawLine(int(c_x - cell), int(c_y - 5*cell),
                         int(c_x - cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y - 5*cell),
                         int(c_x + cell), int(c_y + 5*cell))
        # horizontal
        painter.drawLine(int(c_x - 5*cell), int(c_y - cell),
                         int(c_x + 5*cell), int(c_y - cell))
        painter.drawLine(int(c_x - 5*cell), int(c_y + cell),
                         int(c_x + 5*cell), int(c_y + cell))
        # diagonal (diamond)
        painter.drawLine(int(c_x - 5*cell), int(c_y - 5*cell),
                         int(c_x - cell), int(c_y - cell))
        painter.drawLine(int(c_x + 5*cell), int(c_y - 5*cell),
                         int(c_x + cell), int(c_y - cell))
        painter.drawLine(int(c_x - cell), int(c_y + cell),
                         int(c_x - 5*cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y + cell),
                         int(c_x + 5*cell), int(c_y + 5*cell))

    # -----------------------------------------------------------------
    # 6️⃣  Zodiac positions – still the same geometry as before
    # -----------------------------------------------------------------
    def get_zodiac_positions(self):
        """Return a dict {zodiac_name: QPointF(x, y)}."""
        base_coords = [
            ("မိဿ", 260, 20), ("ပြိဿ", 155, 20), ("မေထုန်", 75, 80),
            ("ကရကဋ်", 75, 195), ("သိဟ်", 75, 345), ("ကန်", 165, 415),
            ("တူ", 260, 345), ("ဗြိစ္ဆာ", 405, 405), ("ဓနု", 485, 345),
            ("မကာရ", 405, 195), ("ကုမ်", 485, 101), ("မိန်", 405, 20)
        ]

        pos = {}
        scale = 0.8
        for name, bx, by in base_coords:
            x = (bx - 250) * scale + self.center_x
            y = (by - 250) * scale + self.center_y
            pos[name] = QPointF(x, y)
        return pos

    # -----------------------------------------------------------------
    # 7️⃣  Draw planets (symbol + optional degree + retro‑mark)
    # -----------------------------------------------------------------
    def draw_planets(self, painter):
        if not self.planet_data:
            return

        # Group planets by zodiac sign (so they are stacked)
        planets_by_sign = {}
        for p in self.planet_data:
            sign_name = ZODIAC_SIGNS_MM[p["sign"]]
            planets_by_sign.setdefault(sign_name, []).append(p)

        line_height = 20
        zodiac_pos = self.get_zodiac_positions()
        
        # Font manager ကနေ font များရယူခြင်း
        symbol_font = self.font_manager.get_font(self.chart_type, "symbol")
        degree_font = self.font_manager.get_font(self.chart_type, "degree")

        for sign_name, planets in planets_by_sign.items():
            if sign_name not in zodiac_pos:
                continue

            base = zodiac_pos[sign_name]

            for i, pl in enumerate(planets):
                # -------- Retrograde flag --------
                retro_txt = " R" if pl.get("retro", False) else ""

                # -------- Symbol (always drawn) --------
                if symbol_font:
                    painter.setFont(symbol_font)
                text = f"{pl['symbol']}"

                # -------- Degree / minute (if requested) --------
                if self.show_degrees and "deg" in pl and "min" in pl:
                    painter.setFont(degree_font)    
                    text += f" {pl['deg']}°{pl['min']}'"
                else:
                    #degree မပြချင်ရင် Symbol font  eနဲ့ ဆက်ရေးမယ်
                    if symbol_font: 
                        painter.setFont(symbol_font)    
                
                
                # -------- Retrograde flag --------
                if pl.get("retro", False):
                    if symbol_font:
                        painter.setFont(symbol_font)
                    text += " R"

                # -------- Position (left‑aligned under the zodiac name) --------
                x = base.x() - 60               # a bit left of the zodiac label
                y = base.y() + i * line_height   # stacked vertically

                painter.drawText(QPointF(x, y), text)

                # (Optional) you can also draw a small “R” with a separate font
                # if you want it to appear in a different colour/size.

# ----------------------------------------------------------------------
# End of BurmeseChartWidget
# ----------------------------------------------------------------------
