import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class TriChakkaChart(QWidget):
    """တြိစက္ကဇာတာ Chart Widget"""
    
    def __init__(self, parent=None, width=300, height=300):
        """
        TriChakkaChart widget ဖန်တီးခြင်း
        """
        super().__init__(parent)
        self.width = width
        self.height = height
        self.ROWS = 3
        self.COLS = 3
        self.PADDING = 5
        
        self.initUI()
    
    def initUI(self):
        """UI components များ စီမံခြင်း"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Canvas widget for drawing
        self.canvas = QLabel()
        self.canvas.setFixedSize(self.width, self.height)
        self.canvas.setStyleSheet("background-color: white;")
        main_layout.addWidget(self.canvas, 0, Qt.AlignCenter)
        
        self.setLayout(main_layout)
        
        # Draw initial chart
        self.draw_chart()
    
    def draw_chart(self):
        """ဇာတာကားချပ်ကို ရေးဆွဲခြင်း"""
        # Create pixmap for drawing
        pixmap = QPixmap(self.width, self.height)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        cell_w = (self.width - 2 * self.PADDING) / self.COLS
        cell_h = (self.height - 2 * self.PADDING) / self.ROWS
        
        # Draw grid and content
        for r in range(self.ROWS):
            for c in range(self.COLS):
                x1 = self.PADDING + c * cell_w
                y1 = self.PADDING + r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                
                # Draw cell border
                painter.setPen(QPen(QColor("#333"), 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(int(x1), int(y1), int(cell_w), int(cell_h))
                
                # Corner triangles for specific positions
                if (r, c) == (0, 0):  # Top-left
                    # First triangle
                    painter.setBrush(QColor("#e8f4f8"))
                    painter.setPen(QPen(QColor("#333"), 1))
                    triangle1 = QPolygonF([
                        QPointF(x1, y1),
                        QPointF(x2, y1),
                        QPointF(x2, y2)
                    ])
                    painter.drawPolygon(triangle1)
                    
                    # Second triangle
                    painter.setBrush(QColor("#fff4e6"))
                    triangle2 = QPolygonF([
                        QPointF(x1, y1),
                        QPointF(x1, y2),
                        QPointF(x2, y2)
                    ])
                    painter.drawPolygon(triangle2)
                    
                elif (r, c) == (0, 2):  # Top-right
                    # First triangle
                    painter.setBrush(QColor("#f0f9f0"))
                    triangle1 = QPolygonF([
                        QPointF(x1, y1),
                        QPointF(x2, y1),
                        QPointF(x1, y2)
                    ])
                    painter.drawPolygon(triangle1)
                    
                    # Second triangle
                    painter.setBrush(QColor("#f5f0ff"))
                    triangle2 = QPolygonF([
                        QPointF(x2, y1),
                        QPointF(x2, y2),
                        QPointF(x1, y2)
                    ])
                    painter.drawPolygon(triangle2)
                    
                elif (r, c) == (2, 0):  # Bottom-left
                    # First triangle
                    painter.setBrush(QColor("#fff0f5"))
                    triangle1 = QPolygonF([
                        QPointF(x1, y1),
                        QPointF(x2, y1),
                        QPointF(x1, y2)
                    ])
                    painter.drawPolygon(triangle1)
                    
                    # Second triangle
                    painter.setBrush(QColor("#f0f8ff"))
                    triangle2 = QPolygonF([
                        QPointF(x2, y1),
                        QPointF(x2, y2),
                        QPointF(x1, y2)
                    ])
                    painter.drawPolygon(triangle2)
                    
                elif (r, c) == (2, 2):  # Bottom-right
                    # First triangle
                    painter.setBrush(QColor("#fffacd"))
                    triangle1 = QPolygonF([
                        QPointF(x1, y1),
                        QPointF(x2, y1),
                        QPointF(x2, y2)
                    ])
                    painter.drawPolygon(triangle1)
                    
                    # Second triangle
                    painter.setBrush(QColor("#f0fff0"))
                    triangle2 = QPolygonF([
                        QPointF(x1, y1),
                        QPointF(x1, y2),
                        QPointF(x2, y2)
                    ])
                    painter.drawPolygon(triangle2)
        
        painter.end()
        
        # Set the pixmap to canvas
        self.canvas.setPixmap(pixmap)
    
    def sizeHint(self):
        """Widget ၏ သဘာဝအရွယ်အစား"""
        return QSize(self.width, self.height)


class MainWindow(QMainWindow):
    """တြိစက္ကဇာတာ"""
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        """UI ကို စတင်စီမံခြင်း"""
        self.setWindowTitle("တြိစက္ကဇာတာ")
        self.setGeometry(100, 100, 1000, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
        # Charts container
        charts_container = QWidget()
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(20)
        
        # Create 3 chart widgets
        self.chart1 = TriChakkaChart(width=300, height=300)
        charts_layout.addWidget(self.chart1)
        
        self.chart2 = TriChakkaChart(width=300, height=300)
        charts_layout.addWidget(self.chart2)
        
        self.chart3 = TriChakkaChart(width=300, height=300)
        charts_layout.addWidget(self.chart3)
        
        main_layout.addWidget(charts_container, 1, Qt.AlignCenter)
        
        # Center window
        self.center()
    
    def center(self):
        """ပြတင်းပေါက်ကို ဗဟိုပြုခြင်း"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Myanmar Text", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()