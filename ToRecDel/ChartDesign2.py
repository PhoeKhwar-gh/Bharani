import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                            QDesktopWidget, QScrollArea)
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF, QPoint, QSize  
from PyQt5.QtGui import QPixmap, QPainter, QPolygonF, QPen, QBrush, QColor, QFont


class TriChakkaChart(QWidget):
    """တြိစက္ကဇာတာ Chart Widget"""
    
    def __init__(self, parent=None, width=400, height=400, center_text=""):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.center_text = center_text
        self.ROWS = 3
        self.COLS = 3
        self.PADDING = 5
        
        # Base positions - normalized coordinates (0.0 to 1.0)
        self.base_normalized = {
            "မိဿ": (0.356, 0.033), "ပြိဿ": (0.200, 0.033), "မေထုန်": (0.033, 0.147),
            "ကရကဋ်": (0.033, 0.360), "သိဟ်": (0.033, 0.680), "ကန်": (0.205, 0.810),
            "တူ": (0.356, 0.680), "ဗြိစ္ဆာ": (0.678, 0.810), "ဓနု": (0.822, 0.680),
            "မကာရ": (0.822, 0.360), "ကုမ်": (0.865, 0.155), "မိန်": (0.678, 0.033)
        }
        
        self.scale_coordinates()
        self.initUI()
    
    def scale_coordinates(self):
        """Normalized coordinates များကို current chart size နဲ့ scale လုပ်ခြင်း"""
        self.scaled_base = {}
        for name, (norm_x, norm_y) in self.base_normalized.items():
            scaled_x = norm_x * self.width
            scaled_y = norm_y * self.height
            self.scaled_base[name] = (scaled_x, scaled_y)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.width = event.size().width()
        self.height = event.size().height()
        self.scale_coordinates()
        self.draw_chart()
    
    def setChartSize(self, width, height):
        self.width = width
        self.height = height
        self.scale_coordinates()
        self.canvas.setFixedSize(width, height)
        self.draw_chart()
        self.updateGeometry()
    
    def initUI(self):
        """UI components များ စီမံခြင်း"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.canvas = QLabel()
        self.canvas.setFixedSize(self.width, self.height)
        self.canvas.setStyleSheet("background-color: white;")
        main_layout.addWidget(self.canvas, 0, Qt.AlignLeft | Qt.AlignTop)
        
        self.setLayout(main_layout)
        self.draw_chart()
    
    def draw_chart(self):
        """ဇာတာကားချပ်ကို ရေးဆွဲခြင်း"""
        pixmap = QPixmap(self.width, self.height)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_font = QFont("Myanmar Text", 12, QFont.Bold)
        dot_font = QFont("Myanmar Text", 8)
        
        cell_w = (self.width - 2 * self.PADDING) / self.COLS
        cell_h = (self.height - 2 * self.PADDING) / self.ROWS
        
        for r in range(self.ROWS):
            for c in range(self.COLS):
                x1 = self.PADDING + c * cell_w
                y1 = self.PADDING + r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                
                painter.setPen(QPen(QColor("#333"), 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(int(x1), int(y1), int(cell_w), int(cell_h))
                
                if (r, c) == (0, 0):  # Top-left
                    painter.setBrush(QColor("#dff5fc"))
                    painter.setPen(QPen(QColor("#333"), 1))
                    triangle1 = QPolygonF([
                        QPointF(x1, y1), QPointF(x2, y1), QPointF(x2, y2)
                    ])
                    painter.drawPolygon(triangle1)
                    
                    painter.setBrush(QColor("#fcf2e4"))
                    triangle2 = QPolygonF([
                        QPointF(x1, y1), QPointF(x1, y2), QPointF(x2, y2)
                    ])
                    painter.drawPolygon(triangle2)
                
                elif (r, c) == (0, 2):  # Top-right
                    painter.setBrush(QColor("#e5fde5"))
                    triangle1 = QPolygonF([
                        QPointF(x1, y1), QPointF(x2, y1), QPointF(x1, y2)
                    ])
                    painter.drawPolygon(triangle1)
                    
                    painter.setBrush(QColor("#ebe1fe"))
                    triangle2 = QPolygonF([
                        QPointF(x2, y1), QPointF(x2, y2), QPointF(x1, y2)
                    ])
                    painter.drawPolygon(triangle2)
                
                elif (r, c) == (2, 0):  # Bottom-left
                    painter.setBrush(QColor("#fde5ed"))
                    triangle1 = QPolygonF([
                        QPointF(x1, y1), QPointF(x2, y1), QPointF(x1, y2)
                    ])
                    painter.drawPolygon(triangle1)
                    
                    painter.setBrush(QColor("#c4dbef"))
                    triangle2 = QPolygonF([
                        QPointF(x2, y1), QPointF(x2, y2), QPointF(x1, y2)
                    ])
                    painter.drawPolygon(triangle2)
                
                elif (r, c) == (2, 2):  # Bottom-right
                    painter.setBrush(QColor("#f3eec5"))
                    triangle1 = QPolygonF([
                        QPointF(x1, y1), QPointF(x2, y1), QPointF(x2, y2)
                    ])
                    painter.drawPolygon(triangle1)
                    
                    painter.setBrush(QColor("#ccf6cc"))
                    triangle2 = QPolygonF([
                        QPointF(x1, y1), QPointF(x1, y2), QPointF(x2, y2)
                    ])
                    painter.drawPolygon(triangle2)
                
                if (r, c) == (1, 1) and self.center_text:
                    painter.setFont(center_font)
                    painter.setPen(QColor("#0066cc"))
                    painter.drawText(QRectF(x1, y1, cell_w, cell_h), 
                                    Qt.AlignCenter, self.center_text)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#ff0000"))
        dot_radius = 3
        
        for name, (x, y) in self.scaled_base.items():
            painter.drawEllipse(QPointF(x, y), dot_radius, dot_radius)
            painter.setFont(dot_font)
            painter.setPen(QColor("#666666"))
            
            text_x = x + 8 if x < self.width * 0.5 else x - 25
            text_y = y + 15 if y < self.height * 0.5 else y - 5
            
            painter.drawText(int(text_x), int(text_y), name)
        
        painter.end()
        self.canvas.setPixmap(pixmap)
    
    def sizeHint(self):
        return QSize(self.width, self.height)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.charts = []
        self.charts_per_row = 3
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.initUI()
    
    def initUI(self):
        """UI components များ စီမံခြင်း"""
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Create container widget for charts
        self.charts_container = QWidget()
        self.charts_layout = QGridLayout(self.charts_container)
        self.charts_layout.setContentsMargins(10, 10, 10, 10)
        self.charts_layout.setSpacing(10)
        
        scroll.setWidget(self.charts_container)
        main_layout.addWidget(scroll)
        
        # Initialize first chart
        self.addRasiChart()
        
        self.setWindowTitle("တြိစက္ကဇာတာ")
        self.center()
    
    def addRasiChart(self):
        """ရာသီ Chart တစ်ခု ထည့်ခြင်း"""
        rasi_chart = TriChakkaChart(width=400, height=400, center_text="ရာသီ")
        
        row = len(self.charts) // self.charts_per_row
        col = len(self.charts) % self.charts_per_row
        
        self.charts_layout.addWidget(rasi_chart, row, col, Qt.AlignLeft | Qt.AlignTop)
        self.charts.append(rasi_chart)
        self.adjustWindowSize()
    
    def adjustWindowSize(self):
        chart_count = len(self.charts)
        rows = (chart_count + self.charts_per_row - 1) // self.charts_per_row
        new_width = 1300
        new_height = max(500, rows * 430 + 150)
        self.resize(new_width, new_height)
    
    def resizeCharts(self, width, height):
        for chart in self.charts:
            chart.setChartSize(width, height)
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    app = QApplication(sys.argv)
    font = QFont("Myanmar Text", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()