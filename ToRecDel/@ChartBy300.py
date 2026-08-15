import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

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
            "Lagna": {"zodiac": "သိဟ်", "degree": "8°47'"},
            "Sun": {"zodiac": "ကန်", "degree": "7°24'"},
            "Moon": {"zodiac": "သိဟ်", "degree": "29°17'"},
            "Mercury": {"zodiac": "သိဟ်", "degree": "24°19'"},
            "Venus": {"zodiac": "သိဟ်", "degree": "5°47'"},
            "Mars": {"zodiac": "သိဟ်", "degree": "14°57'"},
            "Jupiter": {"zodiac": "ကရကဋ်", "degree": "17°36' R"},
            "Saturn": {"zodiac": "မိဿ", "degree": "0°07' R"},
            "Uranus": {"zodiac": "မိဿ", "degree": "1°26'"},
            "Neptune": {"zodiac": "ပြိဿ", "degree": "1°23'"},
            "Pluto": {"zodiac": "မကာရ", "degree": "1°48' R"}
        }
        
        self.zodiac_positions = {}
        
        # Window အရွယ်အစားကို 300x300 ပိတ်ထားသည်
        self.setFixedSize(300, 300) 
        self.setWindowTitle("မြန်မာဗေဒင် Chart (300x300)")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        c_x = w // 2
        c_y = h // 2
        #self.cell = min(w, h) // 140
        
        # Grid အရွယ်အစားကို 300x300 ပေါ်မူတည်ပြီး ချိန်ညှိသည်
        self.center_x = c_x
        self.center_y = c_y
        self.cell_size = min(w, h) // 6 #11  # အရွယ်အစားကို သေးသွားအောင် ချိန်ညှိ

        # Grid ရေးဆွဲခြင်း
        self.draw_grid(painter, label_text="ရာသီ")
        
        # ရာသီနေရာများ ရယူခြင်း
        self.zodiac_positions = self.get_zodiac_positions()
        
        # ရာသီအမည်များ မရေးပဲ Planets များကိုသာ ရေးဆွဲခြင်း
        # self.draw_zodiacs(painter, self.zodiac_positions) # ဤကြောင့် ရာသီအမည်များ မပေါ်ပါ
        
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

        # Center label (ဖောင့်အရွယ်အစားလည်း သေးသွားစေသည်)
        font = QFont("Myanmar Text", 10, QFont.Bold)
        if not font.exactMatch():
            font.setFamily("Pyidaungsu")
        painter.setFont(font)
        
        text_rect = QRectF(c_x - 40, c_y - 15, 80, 30) 
        painter.drawText(text_rect, Qt.AlignCenter, label_text)

    def get_zodiac_positions(self):
        """300x300 အတွက် Scaled Coordinates များ (600x600 ၏ တစ်ဝက်)"""
        positions = {
            "မိဿ": QPointF(118, 6),
            "ပြိဿ": QPointF(44, 3),
            "မေထုန်": QPointF(5, 40),
            "ကရကဋ်": QPointF(8, 102),
            "သိဟ်": QPointF(8, 202),
            "ကန်": QPointF(52, 254),
            "တူ": QPointF(114, 210),
            "ဗြိစ္ဆာ": QPointF(210, 248),
            "ဓနု": QPointF(248, 202),
            "မကာရ": QPointF(212, 101),
            "ကုမ်": QPointF(260, 46),
            "မိန်": QPointF(214, 3)
        }
        return positions

    # ဤနေရာတွင် ရာသီအမည်များ ရေးသားခြင်းကို ပယ်ဖျက်ထားပါသည်
    def draw_zodiacs(self, painter, positions):
        pass 

    def draw_planets(self, painter, positions):
        planet_counts = {z: 0 for z in self.zodiac_names}
        
        # Planet ဖောင့်အရွယ်အစားကို လည်း သေးသွားစေသည်
        font_symbol = QFont("Myanmar Text", 8, QFont.Bold)
        font_symbol.setFamily("Pyidaungsu") 
        
        font_degree = QFont("Arial Narrow", 7, QFont.Bold)
        
        for planet, data in self.planet_data.items():
            zodiac = data["zodiac"]
            degree = data["degree"]
            symbol = self.planet_symbols.get(planet, planet[0])
            
            if zodiac in positions:
                base_pos = positions[zodiac]
                count = planet_counts[zodiac]
                
                # အကွာအဝေးကိုလည်း ချိန်ညှိသည်
                start_y = base_pos.y() + 10
                new_y = start_y + (count * 14)#14
                
                x = base_pos.x()
                
                painter.setFont(font_symbol)
                painter.setPen(QColor("darkred"))
                painter.drawText(int(x), int(new_y), symbol)
                
                painter.setFont(font_degree)
                painter.setPen(QColor("#0320C6"))
                painter.drawText(int(x) + 12, int(new_y), degree)
                
                planet_counts[zodiac] += 1

    def mousePressEvent(self, event):
        """Mouse Click Event"""
        click_pos = event.pos()
        click_x, click_y = click_pos.x(), click_pos.y()
        
        found = False
        threshold = 20 # 300x300 ဖြစ်သောကြောင့် threshold ကိုလည်း လျှော့သည်
        
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