# brn_chart_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QFont, QPen, QColor, QFontMetrics
import math

class ChartWidget(QWidget):
    """ဇာတာဇယားပြဖို့ widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.chart_data = None
        self.division = 'D1'
        self.font = QFont("Pyidaungsu", 10)
        
    def set_chart_data(self, chart_data, division='D1'):
        """ဇာတာဒေတာကို သတ်မှတ်ပါတယ်"""
        self.chart_data = chart_data
        self.division = division
        self.update()
        
    def paintEvent(self, event):
        """Chart ကို ဆွဲပါတယ်"""
        if not self.chart_data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # အရောင်များ
        bg_color = QColor(255, 255, 240)
        line_color = QColor(0, 0, 0)
        text_color = QColor(0, 0, 0)
        
        # နောက်ခံအရောင်
        painter.fillRect(self.rect(), bg_color)
        
        # စာလုံးနဲ့ကဲ့ကို သတ်မှတ်ပါ
        painter.setFont(self.font)
        painter.setPen(QPen(line_color, 2))
        
        # ဇယားရဲ့ အလယ်ဗဟိုနဲ့ အရွယ်အစား
        center_x = self.width() / 2
        center_y = self.height() / 2
        size = min(self.width(), self.height()) * 0.8
        
        # ရာသီစကွားကို ဆွဲပါ
        self._draw_rasi_square(painter, center_x, center_y, size)
        
        # ဂြိုဟ်များကို ဆွဲပါ
        self._draw_planets(painter, center_x, center_y, size)
        
        # ဘာဝနံပါတ်များကို ဆွဲပါ
        self._draw_house_numbers(painter, center_x, center_y, size)
        
    def _draw_rasi_square(self, painter, cx, cy, size):
        """ရာသီစကွားကို ဆွဲပါတယ်"""
        # စကွားရဲ့ အစိတ်အပိုင်းများ
        cell_size = size / 3
        
        # ပြင်ပစကွား
        for i in range(3):
            for j in range(3):
                x = cx - size/2 + j * cell_size
                y = cy - size/2 + i * cell_size
                
                # စကွားကို ဆွဲပါ
                painter.drawRect(x, y, cell_size, cell_size)
                
                # ရာသီအမည်ကို ရေးပါ
                rasi_num = self._get_rasi_number(i, j)
                rasi_name = self._get_rasi_name(rasi_num)
                
                painter.drawText(x + 5, y + 20, rasi_name)
                
        # အတွင်းစကွား
        inner_size = size / 3
        for i in range(3):
            for j in range(3):
                x = cx - inner_size/2 + j * inner_size/3
                y = cy - inner_size/2 + i * inner_size/3
                painter.drawRect(x, y, inner_size/3, inner_size/3)
                
    def _draw_planets(self, painter, cx, cy, size):
        """ဂြိုဟ်များကို ဆွဲပါတယ်"""
        if not self.chart_data:
            return
            
        # ဂြိုဟ်များရဲ့ တည်နေရာများ
        planets = {
            'နေ': self.chart_data.get('sun', 0),
            'လ': self.chart_data.get('moon', 0),
            'အာယန': self.chart_data.get('planets', {}).get('အာယန', 0),
            'ကြာ': self.chart_data.get('planets', {}).get('ကြာ', 0),
            'သောကြာ': self.chart_data.get('planets', {}).get('သောကြာ', 0),
            'စနေ': self.chart_data.get('planets', {}).get('စနေ', 0),
            'ဂြိုဟ်ကြီး': self.chart_data.get('planets', {}).get('ဂြိုဟ်ကြီး', 0),
            'စန္ဒြီ': self.chart_data.get('planets', {}).get('စန္ဒြီ', 0),
            'ရာဟု': self.chart_data.get('planets', {}).get('ရာဟု', 0),
            'ကေတု': self.chart_data.get('planets', {}).get('ကေတု', 0),
        }
        
        # လက်္ခရာ
        asc_pos = self.chart_data.get('ascendant', 0)
        asc_x, asc_y = self._get_position_in_chart(asc_pos, cx, cy, size)
        painter.drawText(asc_x - 20, asc_y, "လက်္ခရာ")
        
        # ဂြိုဟ်များကို ဆွဲပါ
        for planet_name, degree in planets.items():
            x, y = self._get_position_in_chart(degree, cx, cy, size)
            painter.drawText(x - 15, y, planet_name)
            
    def _draw_house_numbers(self, painter, cx, cy, size):
        """ဘာဝနံပါတ်များကို ဆွဲပါတယ်"""
        if not self.chart_data or 'houses' not in self.chart_data:
            return
            
        houses = self.chart_data['houses']['houses']
        
        for i in range(12):
            # ဘာဝရဲ့ စုရပ်ကို ရယူပါ
            cusp_degree = houses[i]
            
            # ဘာဝနံပါတ်ကို ဆွဲပါ
            x, y = self._get_position_in_chart(cusp_degree, cx, cy, size)
            painter.drawText(x - 5, y - 10, str(i + 1))
            
    def _get_position_in_chart(self, degree, cx, cy, size):
        """ဒီဂရီမှာရှိတဲ့ နေရာကို chart ထဲမှာ ရယူပါတယ်"""
        # ရာသီနံပါတ်
        rasi_num = int(degree / 30)
        
        # ရာသီရဲ့ တည်နေရာ (3x3 grid)
        positions = [
            (1, 2), (0, 2), (0, 1),  # မိဿ, ပြိဿာဒိုး, သိဟ်
            (0, 0), (1, 0), (2, 0),  # ကြတိုး, သား, ကန်
            (2, 1), (2, 2), (1, 1),  # သိုး, မြောက်, သားကောင်း
            (1, 1), (1, 1), (1, 1)   # ထေရီ, မောင်း, ငါး (အတွင်းစကွား)
        ]
        
        row, col = positions[rasi_num]
        
        # စကွားအရွယ်အစား
        cell_size = size / 3
        
        # စကွားအတွင်းမှာ တည်နေရာ
        x = cx - size/2 + col * cell_size + cell_size/2
        y = cy - size/2 + row * cell_size + cell_size/2
        
        # ရာသီအတွင်းမှာ အနည်းငယ် shift
        offset_x = (degree % 30) / 30 * cell_size * 0.3
        offset_y = (degree % 30) / 30 * cell_size * 0.3
        
        return x + offset_x, y + offset_y
        
    def _get_rasi_number(self, row, col):
        """Grid position ကနေ ရာသီနံပါတ်ကို ရယူပါတယ်"""
        positions = [
            [3, 2, 1],
            [4, 5, 6],
            [9, 8, 7]
        ]
        return positions[row][col] - 1
        
    def _get_rasi_name(self, rasi_num):
        """ရာသီနံပါတ်ကနေ ရာသီအမည်ကို ရယူပါတယ်"""
        rasis = [
            'မိဿ', 'ပြိဿာဒိုး', 'သိဟ်', 'ကြတိုး', 'သား', 'ကန်',
            'သိုး', 'မြောက်', 'သားကောင်း', 'ထေရီ', 'မောင်း', 'ငါး'
        ]
        return rasis[rasi_num]