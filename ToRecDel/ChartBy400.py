# ChartBy400.py
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics

class BurmeseChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.zodiac_names = [
            "မိဿ", "ပြိဿ", "မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်",
            "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုမ်", "မိန်"
        ]

        self.planet_symbols = {
            "Sun": "၁", "Moon": "၂", "Mars": "၃", "Mercury": "၄",
            "Jupiter": "၅", "Venus": "၆", "Saturn": "၀",
            "Uranus": "U", "Neptune": "N", "Pluto": "P", "Lagna": "လ"
        }

        # 🔴 main.py ကနေ ထည့်ပေးမယ့် data
        self.planet_data = {}

        self.setFixedSize(400, 400)

    # ==============================
    # REQUIRED CORE FUNCTIONS
    # ==============================

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        self.center_x = w // 2
        self.center_y = h // 2
        self.cell_size = min(w, h) // 6

        self.draw_grid(painter)
        positions = self.get_zodiac_positions()
        self.draw_planets(painter, positions)

    def draw_grid(self, painter):
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)

        c_x, c_y, cell = self.center_x, self.center_y, self.cell_size

        painter.drawLine(c_x - cell, c_y - 5*cell, c_x - cell, c_y + 5*cell)
        painter.drawLine(c_x + cell, c_y - 5*cell, c_x + cell, c_y + 5*cell)
        painter.drawLine(c_x - 5*cell, c_y - cell, c_x + 5*cell, c_y - cell)
        painter.drawLine(c_x - 5*cell, c_y + cell, c_x + 5*cell, c_y + cell)

        painter.drawLine(c_x - 5*cell, c_y - 5*cell, c_x - cell, c_y - cell)
        painter.drawLine(c_x + 5*cell, c_y - 5*cell, c_x + cell, c_y - cell)
        painter.drawLine(c_x - cell, c_y + cell, c_x - 5*cell, c_y + 5*cell)
        painter.drawLine(c_x + cell, c_y + cell, c_x + 5*cell, c_y + 5*cell)

        font = QFont("Pyidaungsu", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(c_x-40, c_y-16, 80, 32),
                         Qt.AlignCenter, "ရာသီ")

    def get_zodiac_positions(self):
        scale = 0.8
        base = {
            "မိဿ": (197, 5), "ပြိဿ": (105, 5), "မေထုန်": (7, 66),
            "ကရကဋ်": (7, 170), "သိဟ်": (12, 340), "ကန်": (105, 390),
            "တူ": (189, 349), "ဗြိစ္ဆာ": (340, 390), "ဓနု": (414, 335),
            "မကာရ": (414, 170), "ကုမ်": (434, 60), "မိန်": (338, 5)
        }

        pos = {}
        for k, (x, y) in base.items():
            pos[k] = QPointF(
                (x - 250) * scale + 200,
                (y - 250) * scale + 200
            )
        return pos

    def draw_planets(self, painter, positions):
        planet_counts = {z: 0 for z in self.zodiac_names}

        font_sym = QFont("Pyidaungsu", 9, QFont.Bold)
        font_deg = QFont("Arial", 7, QFont.Bold)

        painter.setFont(font_sym)
        fm = painter.fontMetrics()

        for planet, data in self.planet_data.items():
            zodiac = data["zodiac"]
            degree = data["degree"]
            symbol = self.planet_symbols.get(planet, planet[0])

            if zodiac not in positions:
                continue

            base = positions[zodiac]
            y = base.y() + 10 + planet_counts[zodiac] * 15
            x = base.x()

            painter.setPen(QColor("darkred"))
            painter.setFont(font_sym)
            painter.drawText(int(x), int(y), symbol)

            sw = fm.horizontalAdvance(symbol)
            painter.setPen(QColor("#0320C6"))
            painter.setFont(font_deg)
            painter.drawText(int(x + sw + 4), int(y), degree)

            planet_counts[zodiac] += 1
