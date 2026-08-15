#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fortune_chart_widget.py - ကံကြမ္မာ အနိမ့်အမြင့် ဇယား (Line Chart with QPainter)
မွေးသက္ကရာဇ်မှ စတင်၍  ရက်တစ်ကြိမ် တွက်ချက်ပြီး လက်ရှိမှ နောက် ၃ နှစ်အထိ ဖော်ပြပေးသည်။
"""

import sys
import math
import swisseph as swe
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QProgressBar, 
                             QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush

class FortuneChartWidget(QWidget):
    """ကံကြမ္မာ အနိမ့်အမြင့် ဇယားအတွက် Widget"""
    
    def __init__(self, parent_app=None):
        super().__init__()
        self.parent_app = parent_app
        self.fortune_data = []
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel(" ကံကြမ္မာ အနိမ့်အမြင့် ဇယား (PyQt5 Chart)")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(header)
        
        # Chart Area (Custom Painting)
        self.chart_view = ChartViewWidget()
        main_layout.addWidget(self.chart_view)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_calc = QPushButton(" ကံအနိမ့်အမြင့် စတင်တွက်ချက်မည်")
        self.btn_calc.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        self.btn_calc.clicked.connect(self.start_calculation)
        btn_layout.addWidget(self.btn_calc)
        
        main_layout.addLayout(btn_layout)

    def calculate_fortune_score(self, jd, lat, lon):
        """ ြိုဟ်တည်နေရာများကို အသုံးပြု၍ ကံအဆင့် (Fortune Score) တွက်ချက်ခြင်း """
        try:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            planets = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN]
            benefic_planets = [swe.JUPITER, swe.VENUS, swe.MERCURY, swe.MOON]
            malefic_planets = [swe.SUN, swe.MARS, swe.SATURN]
            
            total_benefic = 0
            total_malefic = 0
            
            for planet in planets:
                xx, flg = swe.calc_ut(jd, planet, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
                longitude = xx[0] % 360
                sign_index = int(longitude / 30)
                
                exalted = False
                debilitated = False
                if (planet == swe.SUN and sign_index == 0) or \
                   (planet == swe.MOON and sign_index == 1) or \
                   (planet == swe.MARS and sign_index == 9) or \
                   (planet == swe.MERCURY and sign_index == 5) or \
                   (planet == swe.JUPITER and sign_index == 3) or \
                   (planet == swe.VENUS and sign_index == 11) or \
                   (planet == swe.SATURN and sign_index == 6):
                    exalted = True
                
                elif (planet == swe.SUN and sign_index == 6) or \
                     (planet == swe.MOON and sign_index == 7) or \
                     (planet == swe.MARS and sign_index == 3) or \
                     (planet == swe.MERCURY and sign_index == 11) or \
                     (planet == swe.JUPITER and sign_index == 9) or \
                     (planet == swe.VENUS and sign_index == 5) or \
                     (planet == swe.SATURN and sign_index == 0):
                    debilitated = True
                
                if exalted:
                    if planet in benefic_planets: total_benefic += 50
                    else: total_malefic -= 50
                elif debilitated:
                    if planet in benefic_planets: total_benefic -= 50
                    else: total_malefic += 50
                else:
                    if planet in benefic_planets: total_benefic += 20
                    else: total_malefic += 10
            
            net_strength = total_benefic - total_malefic
            score = max(0, min(100, 50 + net_strength))
            return score
            
        except Exception:
            return 50

    def start_calculation(self):
        if not self.parent_app or not hasattr(self.parent_app, 'current_planet_data'):
            QMessageBox.warning(self, "သတိပေးချက်", "ပထမဦးစွာ ဇာတာကို တွက်ချက်ပေးပါ။")
            return

        try:
            birth_date = self.parent_app.cboDate.date()
            lat = float(self.parent_app.txtLat.text())
            lon = float(self.parent_app.txtLon.text())
            
            # Range: Birth date to Current date + 3 years
            start_date = datetime(birth_date.year(), birth_date.month(), birth_date.day())
            end_date = datetime.now() + timedelta(days=3*365)
            current_date = start_date
            
            dates = []
            scores = []
            
            while current_date <= end_date:
                jd = swe.julday(current_date.year, current_date.month, current_date.day, 12.0)
                score = self.calculate_fortune_score(jd, lat, lon)
                
                dates.append(current_date)
                scores.append(score)
                current_date += timedelta(days=7)
            
            # Update Custom Chart Widget
            self.chart_view.set_data(dates, scores)
            
        except Exception as e:
            QMessageBox.critical(self, "အမှား", str(e))

# ==========================================
# Custom Chart Widget using QPainter
# ==========================================
class ChartViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(400)
        self.dates = []
        self.scores = []
        
        # Colors
        self.bg_color = QColor("#ffffff")
        self.grid_color = QColor("#ecf0f1")
        self.line_color = QColor("#3498db")
        self.fill_color = QColor(52, 152, 219, 50) # Transparent Blue
        self.text_color = QColor("#2c3e50")

    def set_data(self, dates, scores):
        self.dates = dates
        self.scores = scores
        self.update() # Repaint

    def paintEvent(self, event):
        if not self.dates:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), self.bg_color)
        
        # Margins
        margin_left = 60
        margin_right = 20
        margin_top = 30
        margin_bottom = 50
        
        chart_width = self.width() - margin_left - margin_right
        chart_height = self.height() - margin_top - margin_bottom
        
        # X and Y Ranges
        min_date = self.dates[0]
        max_date = self.dates[-1]
        max_score = 100
        
        # Helper to map value to pixel (✅ FIX: return int)
        def get_x(date):
            total_seconds = (max_date - min_date).total_seconds()
            if total_seconds == 0: return margin_left
            current_seconds = (date - min_date).total_seconds()
            ratio = current_seconds / total_seconds
            return int(margin_left + (ratio * chart_width))  # ← ပြင်ဆင်ထားသည်
            
        def get_y(score):
            ratio = score / max_score
            return int(margin_top + chart_height - (ratio * chart_height))  # ← ပြင်ဆင်ထားသည်
            
        # Draw Grid and Labels
        painter.setPen(QPen(self.grid_color, 1))
        painter.setFont(QFont("Arial", 10))
        
        # Y-Axis Labels (0%, 20%, ... 100%)
        for i in range(0, 101, 20):
            y = get_y(i)
            painter.drawLine(margin_left, y, self.width() - margin_right, y)
            painter.setPen(self.text_color)
            painter.drawText(10, y + 5, f"{i}%")
            painter.setPen(QPen(self.grid_color, 1))
            
        # Draw Filled Area
        if len(self.dates) > 1:
            path_points = []
            for i in range(len(self.dates)):
                x = get_x(self.dates[i])
                y = get_y(self.scores[i])
                path_points.append(QPointF(x, y))
            
            # Create polygon for filling
            polygon = [QPointF(path_points[0].x(), get_y(0))] + path_points + [QPointF(path_points[-1].x(), get_y(0))]
            painter.setBrush(QBrush(self.fill_color))
            painter.setPen(Qt.NoPen)
            painter.drawPolygon(polygon)
            
            # Draw Line
            painter.setPen(QPen(self.line_color, 2))
            for i in range(len(path_points) - 1):
                painter.drawLine(path_points[i], path_points[i+1])
                
            # Draw Points
            painter.setBrush(self.line_color)
            for pt in path_points:
                painter.drawEllipse(pt, 2, 2) 
                
        # Draw X-Axis Labels (Show every 6 months)
        painter.setPen(self.text_color)
        step = max(1, len(self.dates) // 6)
        
        for i in range(0, len(self.dates), step):
            date = self.dates[i]
            x = get_x(date)
            label = f"{date.year}-{date.month:02d}"
            painter.drawText(x - 20, self.height() - 10, 40, 20, Qt.AlignCenter, label)
