import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout, QMainWindow
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QPointF, QRectF

class AshtakavargaChartWidget(QWidget):
    """
    Ashtakavarga ဇယားတစ်ခုချင်းစီကို မူရင်းမျဉ်းကြောင်းအတိုင်း
    တိကျစွာ ဆွဲသားပေးမည့် Single Chart Component ဖြစ်သည်။
    """
    def __init__(self, center_text="As", parent=None):
        super().__init__(parent)
        self.center_text = center_text
        self.setMinimumSize(180, 180)
        # ရာသီခွင် ၂ ကွက်စာအတွက် အမှတ်များ (Key အမည်များကို လုံးဝတစ်ပြေးညီ သတ်မှတ်ထားသည်)
        self.points = {
             "TL_top":  "0",  "TL_left":  "0",
             "TM":  "0",
             "TR_top":  "0",  "TR_right":  "0",
             "ML":  "0",  "MR":  "0",
             "BL_left":  "0",  "BL_bottom":  "0",
             "BM":  "0",
             "BR_right":  "0",  "BR_bottom":  "0"
        }

    def set_chart_data(self, data_dict):
         """ ဤဇယားကွက်တစ်ခုတည်းအတွက် အမှတ်အသစ်များ ထည့်ရန်  """
        if data_dict and isinstance(data_dict, dict):
            self.points.update(data_dict)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height()) - 15
        if side  < 50: return
            
        x_offset = (self.width() - side) / 2
        y_offset = (self.height() - side) / 2
        cell_size = side / 3

        # မျဉ်းကြောင်းအတွက် Pen
        pen = QPen(Qt.black, 1.5, Qt.SolidLine)
        painter.setPen(pen)

        # ၁။ အပြင်ဘက် စတုရန်းဘောင်ကြီး
        painter.drawRect(int(x_offset), int(y_offset), int(side), int(side))

        # ၂။ အတွင်းဘက် Grid  လိုင်းများ
        for i in range(1, 3):
            vx = x_offset + i * cell_size
            painter.drawLine(QPointF(vx, y_offset), QPointF(vx, y_offset + side))
            vy = y_offset + i  * cell_size
            painter.drawLine(QPointF(x_offset, vy), QPointF(x_offset + side, vy))

        # ၃။ မူရင်းပုံစံအတိုင်း အတည်ပြုပြီးသား ထောင့်ဖြတ်မျဉ်း (Diagonal Lines) များ
        painter.drawLine(QPointF(x_offset, y_offset), QPointF(x_offset + cell_size, y_offset + cell_size))
        painter.drawLine(QPointF(x_offset + side, y_offset), QPointF(x_offset + side - cell_size, y_offset + cell_size))
        painter.drawLine(QPointF(x_offset, y_offset + side), QPointF(x_offset + cell_size, y_offset + side - cell_size))
        painter.drawLine(QPointF(x_offset + side, y_offset + side), QPointF(x_offset + side - cell_size, y_offset + side - cell_size))

        # ၄။ စာလုံးနှင့် ဂဏန်းများ ထည့်သွင်းခြင်း
        font = QFont("Helvetica", int(cell_size * 0.24))
        painter.setFont(font)

        def draw_text_in_cell(rel_x, rel_y, key_name):
             """ KeyError မတက်စေရန် .get() စနစ်သုံး၍ တြိဂံကွက်ဗဟိုတွင် စာသားရေးသားခြင်း  """
            abs_x = x_offset + rel_x * cell_size
            abs_y = y_offset + rel_y * cell_size
            box_size = cell_size * 0.45
            rect = QRectF(abs_x - box_size/2, abs_y - box_size/2, box_size, box_size)
            
            # ဒေတာထဲတွင် သော့ချက်မပါလာခဲ့လျှင်  "0" ဟု အလိုအလျောက် ပြသမည်
            text_val = self.points.get(key_name,  "0")
            painter.drawText(rect, Qt.AlignCenter, str(text_val))

        # --- စာသားများ နေရာချခြင်း (Key Error အားလုံး ကာကွယ်ပြီး) ---
        # Top Left Cell (Taurus / Gemini)
        draw_text_in_cell(0.65, 0.35,  "TL_top")     # Taurus (Upper Right of cell)
        draw_text_in_cell(0.35, 0.65,  "TL_left")    # Gemini (Lower Left of cell)
        
        # Top Middle (Aries)
        draw_text_in_cell(1.50, 0.50,  "TM")         
        
        # Top Right Cell (Pisces / Aquarius)
        draw_text_in_cell(2.35, 0.35,  "TR_top")     # Pisces (Upper Left of cell)
        draw_text_in_cell(2.65, 0.65,  "TR_right")   # Aquarius (Lower Right of cell)

        # Middle Left (Cancer)
        draw_text_in_cell(0.50, 1.50,  "ML")         
        
        # Middle Right (Capricorn)
        draw_text_in_cell(2.50, 1.50,  "MR")         

        # Bottom Left Cell (Leo / Virgo)
        draw_text_in_cell(0.35, 2.35,  "BL_left")    # Leo (Upper Left of cell)
        draw_text_in_cell(0.65, 2.65,  "BL_bottom")  # Virgo (Lower Right of cell)
        
        # Bottom Middle (Libra)
        draw_text_in_cell(1.50, 2.50,  "BM")         
        
        # Bottom Right Cell (Sagittarius / Scorpio)
        draw_text_in_cell(2.65, 2.35,  "BR_right")   # Sagittarius (Upper Right of cell)
        draw_text_in_cell(2.35, 2.65,  "BR_bottom")  # Scorpio (Lower Left of cell)

        # အလယ်ဗဟိုစာသား (SAV, As, Su စသဖြင့်)
        center_font = QFont("Pyidaungsu", int(cell_size * 0.28), QFont.Bold)
        painter.setFont(center_font)
        
        abs_cx = x_offset + 1.50 * cell_size
        abs_cy = y_offset + 1.50 * cell_size
        c_box = cell_size  * 0.45
        c_rect = QRectF(abs_cx - c_box/2, abs_cy - c_box/2, c_box, c_box)
        painter.drawText(c_rect, Qt.AlignCenter, self.center_text)

class AshtakavargaMatrixWidget(QWidget):
    """
    ဇယား ၉ ခုလုံးကို ပုံပါအတိုင်း ၃ x ၃ စီစဉ်ပြသပေးမည့် ပင်မ Matrix Widget ဖြစ်သည်။
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.matrix_layout_info = [
            ("SAV", 0, 0), ("လဂ်", 0, 1),  ("", 0, 2),  
            ("", 1, 0),  ("♂", 1, 1),  ("☿", 1, 2),  
            ("♃", 2, 0),  ("♀", 2, 1),  ("♄", 2, 2)   
        ]
        
        self.charts = {}
        self.init_ui()

    def init_ui(self):
        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(15) 

        for name, row, col in self.matrix_layout_info:
            chart_widget = AshtakavargaChartWidget(center_text=name)
            grid_layout.addWidget(chart_widget, row, col)
            self.charts[name] = chart_widget 

    def update_all_matrix_data(self, all_data_dict):
        if not all_data_dict: return
        for name, chart_obj in self.charts.items():
            if name in all_data_dict:
                chart_obj.set_chart_data(all_data_dict[name])