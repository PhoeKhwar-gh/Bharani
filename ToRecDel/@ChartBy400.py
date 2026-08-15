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
        self.setFixedSize(400, 400) 
        self.setWindowTitle("မြန်မာဗေဒင် Chart (400x400)")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        c_x = w // 2
        c_y = h // 2
        
        self.center_x = c_x
        self.center_y = c_y
        self.cell_size = min(w, h) // 6 

        self.draw_grid(painter, label_text="ရာသီ")
        self.zodiac_positions = self.get_zodiac_positions()
        self.draw_planets(painter, self.zodiac_positions)

    def draw_grid(self, painter, label_text="ရာသီ"):
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)

        c_x, c_y = self.center_x, self.center_y
        cell = self.cell_size

        painter.drawLine(int(c_x - cell), int(c_y - 5*cell), int(c_x - cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y - 5*cell), int(c_x + cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x - 5*cell), int(c_y - cell), int(c_x + 5*cell), int(c_y - cell))
        painter.drawLine(int(c_x - 5*cell), int(c_y + cell), int(c_x + 5*cell), int(c_y + cell))
        
        painter.drawLine(int(c_x - 5*cell), int(c_y - 5*cell), int(c_x - cell), int(c_y - cell))
        painter.drawLine(int(c_x + 5*cell), int(c_y - 5*cell), int(c_x + cell), int(c_y - cell))
        painter.drawLine(int(c_x - cell), int(c_y + cell), int(c_x - 5*cell), int(c_y + 5*cell))
        painter.drawLine(int(c_x + cell), int(c_y + cell), int(c_x + 5*cell), int(c_y + 5*cell))

        font = QFont("Myanmar Text", 10, QFont.Bold)
        if not font.exactMatch():
            font.setFamily("Pyidaungsu")
        painter.setFont(font)
        
        text_rect = QRectF(c_x - 40, c_y - 16, 80, 32) 
        painter.drawText(text_rect, Qt.AlignCenter, label_text)

    def get_zodiac_positions(self):
        """400x400 အတွက် အချိုးကျပြန်တွက်ထားသော နေရာများ (500 → 400 သို့ scale = 0.8)"""
        # Original scale (500x500 base) -> scale 0.8 for 400x400
        scale = 0.8
        offset = (500 - 400) / 2  # 500 အလယ်ကနေ 400 အလယ်ကို shift
        positions_500 = {
            "မိဿ": (197, 5),
            "ပြိဿ": (105, 5),
            "မေထုန်": (7, 66),
            "ကရကဋ်": (7, 170),
            "သိဟ်": (12, 340),
            "ကန်": (105, 390),
            "တူ": (189, 349),
            "ဗြိစ္ဆာ": (340, 390),
            "ဓနု": (414, 335),
            "မကာရ": (414, 170),
            "ကုမ်": (434, 60),
            "မိန်": (338, 5)
        }
        positions = {}
        for name, (x, y) in positions_500.items():
            # Scale အရ တွက်: (x - 250) * 0.8 + 200
            scaled_x = (x - 250) * scale + 200
            scaled_y = (y - 250) * scale + 200
            positions[name] = QPointF(scaled_x, scaled_y)
        return positions
 
    def draw_planets(self, painter, positions):
        planet_counts = {z: 0 for z in self.zodiac_names}
        
        font_symbol = QFont("Myanmar Text", 9, QFont.Bold)
        if not QFont("Myanmar Text").exactMatch():
            font_symbol.setFamily("Pyidaungsu")
        font_degree = QFont("Arial Narrow", 7, QFont.Bold)
        
        # FontMetrics ဖန်တီးပါ
        fm_symbol = QFontMetrics(font_symbol)
        
        for planet, data in self.planet_data.items():
            zodiac = data["zodiac"]
            degree = data["degree"]
            symbol = self.planet_symbols.get(planet, planet[0])
            
            if zodiac in positions:
                base_pos = positions[zodiac]
                count = planet_counts[zodiac]
                
                start_y = base_pos.y() + 10 
                new_y = start_y + (count * 15)
                x = base_pos.x()
                
                # ဂြိုလ်သင်္ကေတ ရေး
                painter.setFont(font_symbol)
                painter.setPen(QColor("darkred"))
                painter.drawText(int(x), int(new_y), symbol)
                
                # ဂြိုလ်စာလုံးရဲ့ အကျယ်ကို တွက်ပြီး ဒီဂရီကို ကွာပေးပါ
                symbol_width = fm_symbol.horizontalAdvance(symbol)
                deg_x = int(x) + symbol_width + 3  # ← 8px ကွာအောင် ဓြိုဟ် + ဒီဂရီ ခွာရေးရန်
                
                painter.setFont(font_degree)
                painter.setPen(QColor("#0320C6"))
                painter.drawText(deg_x, int(new_y), degree)
                
                planet_counts[zodiac] += 1

    def mousePressEvent(self, event):
        click_pos = event.pos()
        click_x, click_y = click_pos.x(), click_pos.y()
        
        found = False
        threshold = 20  # 25 → 20 (အနည်းငယ် သေးအောင်)
        
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