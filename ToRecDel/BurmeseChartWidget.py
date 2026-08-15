import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPolygon, QFont
from PyQt5.QtCore import Qt, QPoint

class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Drawing Example")
        self.resize(400, 400) # ဝင်းဒိုးအရွယ်အစား

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # မျဉ်းတွေကို ချောမွေ့အောင် ပြုလုပ်ပေးသည်

        # --- ၁. စတုဂံများ (Grid Layout) ရေးဆွဲခြင်း ---
        w = self.width()
        h = self.height()
        
        # ကွက်လပ် တစ်ခုချင်းစီရဲ့ အကျယ်/အမြင့်
        step_x = w / 3
        step_y = h / 3

        # မျဉ်းရောင်နဲ့ အထူ သတ်မှတ်ခြင်း
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        # ဒေါင်လိုက် မျဉ်းကြောင်းများ ဆွဲခြင်း (Vertical Lines)
        for i in range(1, 3):
            x = int(step_x * i)
            painter.drawLine(x, 0, x, h)

        # အလျားလိုက် မျဉ်းကြောင်းများ ဆွဲခြင်း (Horizontal Lines)
        for i in range(1, 3):
            y = int(step_y * i)
            painter.drawLine(0, y, w, y)
        
        # အပြင်ဘက် နယ်နိမိတ် (Border) ဆွဲခြင်း
        painter.drawRect(0, 0, w, h)


        # --- ၂. တြိဂံ (Triangle) ရေးဆွဲခြင်း ---
        # ဥပမာအားဖြင့် အလယ်ဗဟိုမှာ တြိဂံလေးတစ်ခု ဆွဲကြည့်ပါမယ်
        
        # တြိဂံရဲ့ ထောင့်သုံးခု သတ်မှတ်ခြင်း (Points)
        p1 = QPoint(w // 2, h // 2 - 50) # အပေါ်ထောင့်
        p2 = QPoint(w // 2 - 50, h // 2 + 50) # ဘယ်အောက်ထောင့်
        p3 = QPoint(w // 2 + 50, h // 2 + 50) # ညာအောက်ထောင့်

        # တြိဂံအတွက် အရောင်ဖြည့်စရာ (Brush)
        brush = QBrush(Qt.red) 
        painter.setBrush(brush)
        
        # မျဉ်းရောင်ကို ပြောင်းလိုက်သည် (မဖြစ်မနေ မဟုတ်ပါ)
        painter.setPen(QPen(Qt.darkRed, 2))

        # တြိဂံဆွဲခြင်း
        triangle = QPolygon([p1, p2, p3])
        painter.drawPolygon(triangle)


        # --- ၃. စာသား (Text) ရေးသားခြင်း ---
        painter.setPen(Qt.black)
        font = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font)
        
        # ပုံထဲက စာသား (ᠡᠳᡁᡭᡭ) ကို အောက်ခြေမှာ ထည့်ထားပါတယ်
        painter.drawText(int(step_x), int(step_y * 2) + 20, "ᠡᠳᡁᡭᡭ")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingWidget()
    window.show()
    sys.exit(app.exec_())