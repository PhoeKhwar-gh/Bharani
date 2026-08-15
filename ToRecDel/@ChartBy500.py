import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics

class BurmeseChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.zodiac_names = [
            "မိဿ", "ပြိဿ", "မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်",
            "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုမ်", "မိန်"
        ]
        
        self.planet_symbols = {
            "Sun": "၁", "Moon": "၂", "Mars": "၃", "Mercury": "၄",
            "Jupiter": "၅", "Venus": "၆", "Saturn": "၀",
            "Uranus": "U", "Neptune": "N", "Pluto": "P", "Lagna": "လ"
        }
        
        # နမူနာ Planet ဒေတာများ 
        self.planet_data = {
            "Lagna": {"zodiac": "ဓနု", "degree": "8°47'"},
            "Sun": {"zodiac": "မိန်", "degree": "7°24'"},
            "Moon": {"zodiac": "မိန်", "degree": "29°17'"},
            "Mercury": {"zodiac": "မိန်", "degree": "24°19'"},
            "Venus": {"zodiac": "မိန်", "degree": "5°47'"},
            "Mars": {"zodiac": "မိန်", "degree": "14°57'"},
            "Jupiter": {"zodiac": "ကုမ်", "degree": "17°36' R"},
            "Saturn": {"zodiac": "ကုမ်", "degree": "0°07' R"},
            "Uranus": {"zodiac": "ကုမ်", "degree": "1°26'"},
            "Neptune": {"zodiac": "ကုမ်", "degree": "1°23'"},
            "Pluto": {"zodiac": "ကုမ်", "degree": "1°48' R"}
        }
        
        self.zodiac_positions = {}
        
        # Window အရွယ်အစားကို 500x500 ပိတ်ထားသည်
        self.setFixedSize(500, 500) 
        self.setWindowTitle("မြန်မာဗေဒင် Chart (500x500)")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        c_x = w // 2
        c_y = h // 2
        
        # Grid အရွယ်အစားကို 500x500 ပေါ်မူတည်ပြီး ချိန်ညှိသည်
        self.center_x = c_x
        self.center_y = c_y
        self.cell_size = min(w, h) // 6 

        # Grid ရေးဆွဲခြင်း
        self.draw_grid(painter, label_text="ရာသီ")
        
        # ရာသီနေရာများ ရယူခြင်း
        self.zodiac_positions = self.get_zodiac_positions()
        
        # ရာသီအမည်များ မရေးပဲ Planets များကိုသာ ရေးဆွဲခြင်း
        # self.draw_zodiacs(painter, self.zodiac_positions)
        
        # Planets ရေးဆွဲခြင်း
        self.draw_planets(painter, self.zodiac_positions)

    def draw_grid(self, painter, label_text="ရာသီ"):
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)

        c_x, c_y = self.center_x, self.center_y
        cell = self.cell_size

        # Grid lines
        painter.drawLine(int(c_x - cell), int(c_y - 5*cell), int(c_x - cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y - 5*cell), int(c_x + cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x - 5*cell), int(c_y - cell), int(c_x + 5*cell), int(c_y - cell))
        painter.drawLine(int(c_x - 5*cell), int(c_y + cell), int(c_x + 5*cell), int(c_y + cell))
        
        painter.drawLine(int(c_x - 5*cell), int(c_y - 5*cell), int(c_x - cell), int(c_y - cell))
        painter.drawLine(int(c_x + 5*cell), int(c_y - 5*cell), int(c_x + cell), int(c_y - cell))
        painter.drawLine(int(c_x - cell), int(c_y + cell), int(c_x - 5*cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y + cell), int(c_x + 5*cell), int(c_y + 5*cell))

        # Center label
        font = QFont("Myanmar Text", 12, QFont.Bold)
        if not font.exactMatch():
            font.setFamily("Pyidaungsu")
        painter.setFont(font)
        
        text_rect = QRectF(c_x - 50, c_y - 20, 100, 40) 
        painter.drawText(text_rect, Qt.AlignCenter, label_text)

    def get_zodiac_positions(self):
        """500x500 အတွက် Scaled Coordinates များ (600x600 ၏ 0.833 ဆ)"""
        positions = {
            "မိဿ": QPointF(197, 5),
            "ပြိဿ": QPointF(105, 5),
            "မေထုန်": QPointF(7, 66),
            "ကရကဋ်": QPointF(7, 170),
            "သိဟ်": QPointF(12, 340),
            "ကန်": QPointF(105, 390),
            "တူ": QPointF(189, 349),
            "ဗြိစ္ဆာ": QPointF(340, 390),
            "ဓနု": QPointF(414, 335),
            "မကာရ": QPointF(414, 170),
            "ကုမ်": QPointF(434, 60),
            "မိန်": QPointF(338, 5)
        }
        return positions

    def draw_zodiacs(self, painter, positions):
        # ရာသီအမည်များ မဖော်ပြလိုသဖြင့် ဤနေရာကို ဗလာချန်ထားသည်
        pass 

 
    def draw_planets(self, painter, positions):
        planet_counts = {z: 0 for z in self.zodiac_names}
        
        # Font များ
        font_symbol = QFont("Pyidaungsu", 10, QFont.Bold)
        if not QFont("Dense").exactMatch():
            font_symbol.setFamily("Pyidaungsu")
        
        font_degree = QFont("Arial Narrow", 8, QFont.Bold)
        if not QFont("Dense").exactMatch():
            font_degree.setFamily("Pyidaungsu")
        
        # FontMetrics များ
        fm_symbol = QFontMetrics(font_symbol)
        fm_degree = QFontMetrics(font_degree)
        
        for planet, data in self.planet_data.items():
            zodiac = data["zodiac"]
            degree = data["degree"]
            symbol = self.planet_symbols.get(planet, planet[0])
            
            if zodiac in positions:
                base_pos = positions[zodiac]
                count = planet_counts[zodiac]
                
                # စာကြောင်းတစ်ကြောင်းလျှင် အမြင့် (ဥပမာ: 20px)
                line_height = 20  # နှစ်ခုပေါင်းစားရန် အလုံလောက် နေရာ
                current_line_y = base_pos.y() + 12 + (count * line_height)
                
                x = base_pos.x()
                
                # ဂြိုလ်သင်္ကေတ အမြင့်တွက်
                sym_height = fm_symbol.height()
                sym_ascent = fm_symbol.ascent()
                sym_center_y = current_line_y + (line_height - sym_height) // 2 + sym_ascent

                # ဒီဂရီ အမြင့်တွက်
                deg_height = fm_degree.height()
                deg_ascent = fm_degree.ascent()
                deg_center_y = current_line_y + (line_height - deg_height) // 2 + deg_ascent

                # ဂြိုလ်သင်္ကေတ ရေး
                painter.setFont(font_symbol)
                painter.setPen(QColor("darkred"))
                painter.drawText(int(x), int(sym_center_y), symbol)
                
                # ဒီဂရီကို ဂြိုလ်နဲ့ အနည်းငယ် ကွာပြီး ရေး
                symbol_width = fm_symbol.horizontalAdvance(symbol)
                deg_x = int(x) + symbol_width + 6
                
                painter.setFont(font_degree)
                painter.setPen(QColor("#444444"))
                painter.drawText(deg_x, int(deg_center_y), degree)
                
                planet_counts[zodiac] += 1
    def mousePressEvent(self, event):
        """Mouse Click Event"""
        click_pos = event.pos()
        click_x, click_y = click_pos.x(), click_pos.y()
        
        found = False
        threshold = 25 # 500x500 ဖြစ်သောကြောင့် threshold ကို ချိန်ညှိသည်
        
        for name, pos in self.zodiac_positions.items():
            distance = math.sqrt((click_x - pos.x())**2 + (click_y - pos.y())**2)
            
            if distance < threshold:
                print(f"Clicked: {name} (x: {int(pos.x())}, y: {int(pos.y())})")
                found = True
                break
        
        if not found:
            print(f"Clicked at Empty Space (x: {click_x}, y: {click_y})")

def main():
    app = QApplication(sys.argv)
    window = BurmeseChartWidget()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()