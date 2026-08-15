import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QPointF

class AshtakavargaChartWidget(QWidget):
    """
    ပေးထားသော ဗေဒင်ဇယား (3x3 Grid with Diagonal Corners) ကို 
    တိကျစွာ ဆွဲသားပြသပေးမည့် PyQt5 Custom Widget ဖြစ်သည်။
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300) # အနိမ့်ဆုံး Size သတ်မှတ်ချက်

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Widget ၏ ဗဟိုချက်နှင့် စတုရန်းကွက် အရွယ်အစားကို တွက်ချက်ခြင်း
        side = min(self.width(), self.height()) - 20
        if side < 100:
            return
            
        # စတုရန်းကွက်ကို အလယ်ဗဟိုကျအောင် တည်နေရာညှိခြင်း
        x_offset = (self.width() - side) / 2
        y_offset = (self.height() - side) / 2
        
        # 3x3 Grid အတွက် တစ်ကွက်စာ အကျယ်/အမြင့်
        cell_size = side / 3

        # ဘောင်လိုင်းများအတွက် Pen သတ်မှတ်ခြင်း
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)

        # ၁။ အပြင်ဘက် စတုရန်းဘောင်ကြီး ဆွဲခြင်း
        painter.drawRect(int(x_offset), int(y_offset), int(side), int(side))

        # ၂။ အတွင်းဘက် Grid လိုင်းများ (ဒေါင်လိုက်နှင့် အလျားလိုက်) ဆွဲခြင်း
        for i in range(1, 3):
            # ဒေါင်လိုက်လိုင်းများ
            vx = x_offset + i * cell_size
            painter.drawLine(QPointF(vx, y_offset), QPointF(vx, y_offset + side))
            # အလျားလိုက်လိုင်းများ
            vy = y_offset + i * cell_size
            painter.drawLine(QPointF(x_offset, vy), QPointF(x_offset + side, vy))

        # ၃။ ထောင့်ကွက် ၄ ကွက်ကို ထောင့်ဖြတ်မျဉ်း (Diagonal Lines) ဆွဲခြင်း
        # (Top-Left) ဘယ်ဘက်အပေါ်ထောင့်
        painter.drawLine(QPointF(x_offset, y_offset + cell_size), 
                         QPointF(x_offset + cell_size, y_offset))
        # (Top-Right) ညာဘက်အပေါ်ထောင့်
        painter.drawLine(QPointF(x_offset + 2 * cell_size, y_offset), 
                         QPointF(x_offset + side, y_offset + cell_size))
        # (Bottom-Left) ဘယ်ဘက်အောက်ထောင့်
        painter.drawLine(QPointF(x_offset, y_offset + 2 * cell_size), 
                         QPointF(x_offset + cell_size, y_offset + side))
        # (Bottom-Right) ညာဘက်အောက်ထောင့်
        painter.drawLine(QPointF(x_offset + 2 * cell_size, y_offset + side), 
                         QPointF(x_offset + side, y_offset + 2 * cell_size))

        # ၄။ စာလုံးနှင့် ဂဏန်းများ ထည့်သွင်းခြင်း
        font = QFont("Helvetica", int(cell_size * 0.25))
        painter.setFont(font)

        def draw_text_in_cell(rel_x, rel_y, text):
            """သတ်မှတ်ထားသော ကိုဩဒိနိတ်အချိုးအလိုက် စာသားများကို နေရာချရန် Function"""
            abs_x = x_offset + rel_x * cell_size
            abs_y = y_offset + rel_y * cell_size
            # စာလုံးဗဟိုချက်ညှိရန် Rect Boundary သတ်မှတ်ခြင်း
            rect_w, rect_h = 40, 40
            painter.drawText(int(abs_x - rect_w/2), int(abs_y - rect_h/2), 
                             rect_w, rect_h, Qt.AlignCenter, text)

        # --- Row 0 (အပေါ်ဆုံးတန်း) ---
        draw_text_in_cell(0.25, 0.70, "3") # Top-Left (အောက်ခြေတြိဂံ)
        draw_text_in_cell(0.70, 0.25, "5") # Top-Left (အပေါ်တြိဂံ)
        draw_text_in_cell(1.50, 0.50, "3") # Top-Middle
        draw_text_in_cell(2.30, 0.25, "5") # Top-Right (အပေါ်တြိဂံ)
        draw_text_in_cell(2.75, 0.70, "1") # Top-Right (အောက်ခြေတြိဂံ)

        # --- Row 1 (အလယ်တန်း) ---
        draw_text_in_cell(0.50, 1.50, "4") # Middle-Left
        
        # အလယ်ဗဟို လဂ်နေရာ (As) ကို စာလုံးအနည်းငယ် ပိုကြီးစေခြင်း
        as_font = QFont("Helvetica", int(cell_size * 0.3), QFont.Bold)
        painter.setFont(as_font)
        draw_text_in_cell(1.50, 1.50, "As") 
        painter.setFont(font) # မူလ Font ပြန်ပြောင်းခြင်း
        
        draw_text_in_cell(2.50, 1.50, "5") # Middle-Right

        # --- Row 2 (အောက်ဆုံးတန်း) ---
        draw_text_in_cell(0.25, 2.30, "6") # Bottom-Left (အပေါ်တြိဂံ)
        draw_text_in_cell(0.70, 2.75, "2") # Bottom-Left (အောက်ခြေတြိဂံ)
        draw_text_in_cell(1.50, 2.50, "4") # Bottom-Middle
        draw_text_in_cell(2.30, 2.75, "5") # Bottom-Right (အောက်ခြေတြိဂံ)
        draw_text_in_cell(2.75, 2.30, "6") # Bottom-Right (အပေါ်တြိဂံ)


# --- ကုဒ်ကို စမ်းသပ်မောင်းနှင်ရန် ပင်မပရိုဂရမ် အပိုင်း ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    main_win = QMainWindow()
    main_win.setWindowTitle("Ashtakavarga Chart Layout")
    main_win.resize(400, 450)
    
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # ဆွဲထားသော Custom Widget ကို ထည့်သွင်းခြင်း
    chart = AshtakavargaChartWidget()
    layout.addWidget(chart)
    
    main_win.setCentralWidget(central_widget)
    main_win.show()
    
    sys.exit(app.exec_())