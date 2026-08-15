import swisseph as swe
import datetime
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                             QGridLayout, QVBoxLayout, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("မြန်မာ ဇာတာတွက်စက်")
        self.setGeometry(100, 100, 600, 400)
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create input section
        layout = QGridLayout()
        
        layout.addWidget(QLabel("မွေးနေ့ (YYYY-MM-DD)"), 0, 0)
        self.date_input = QLineEdit("2025-03-23")
        layout.addWidget(self.date_input, 0, 1)
        
        layout.addWidget(QLabel("အချိန် (HH:MM:SS)"), 1, 0)
        self.time_input = QLineEdit("06:30:00")
        layout.addWidget(self.time_input, 1, 1)
        
        layout.addWidget(QLabel("လတ္တီတွဒ်"), 2, 0)
        self.lat_input = QLineEdit("16.7967")  # Default: Yangon latitude
        layout.addWidget(self.lat_input, 2, 1)
        
        layout.addWidget(QLabel("လောင်ဂျီတွဒ်"), 3, 0)
        self.lon_input = QLineEdit("96.1608")  # Default: Yangon longitude
        layout.addWidget(self.lon_input, 3, 1)
        
        self.calc_btn = QPushButton("ဇာတာတွက်မယ်")
        self.calc_btn.clicked.connect(self.calculate_chart)
        layout.addWidget(self.calc_btn, 4, 0, 1, 2)
        
        # Create result display
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        
        # Add Burmese font support if available
        try:
            font = QFont("Pyidaungsu", 10)
            self.result_text.setFont(font)
        except:
            pass
        
        # Add layouts to main layout
        main_layout.addLayout(layout)
        main_layout.addWidget(QLabel("ရလဒ်များ:"))
        main_layout.addWidget(self.result_text)
        
        self.setLayout(main_layout)
        
        # Initialize ephemeris path
        self.set_ephe_path()
    
    def set_ephe_path(self):
        """Set the ephemeris file path"""
        # Try different possible paths
        possible_paths = [
            '/usr/share/swisseph',
            '/usr/local/share/swisseph',
            'C:/sweph/ephe',
            './ephe',
            os.path.expanduser('~/swisseph/ephe')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                swe.set_ephe_path(path)
                print(f"Ephemeris path set to: {path}")
                return
        
        # If no path found, use current directory
        swe.set_ephe_path('')
        print("Using default ephemeris path")
    
    def calculate_chart(self):
        """Calculate planetary positions"""
        try:
            # Get input values
            date_str = self.date_input.text()
            time_str = self.time_input.text()
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
            
            # Calculate planetary positions
            results = self.calculate_planets(date_str, time_str, lat, lon)
            
            # Display results
            self.display_results(results)
            
        except ValueError as e:
            self.result_text.setText(f"Error: Invalid input format\n{str(e)}")
        except Exception as e:
            self.result_text.setText(f"Error: {str(e)}")
    
    def calculate_planets(self, date_str, time_str, lat, lon):
        """Calculate planetary positions for given date, time, and location"""
        # Parse datetime
        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        
        # Convert to Julian Day
        jd = swe.julday(dt.year, dt.month, dt.day, 
                        dt.hour + dt.minute/60.0 + dt.second/3600.0)
        
        # Set geographic location for house calculation
        swe.set_topo(lon, lat, 0)
        
        # Calculate houses first
        houses = swe.houses(jd, lat, lon, b'P')  # 'P' for Placidus house system
        
        results = {
            'date': dt,
            'jd': jd,
            'houses': houses[0],  # House cusps
            'planets': {}
        }
        
        # Planet names in Burmese and English
        planet_names = {
            swe.SUN: ("နေဂြိုဟ်", "Sun"),
            swe.MOON: ("လ", "Moon"),
            swe.MERCURY: ("ဗုဒ္ဓဟူးဂြိုဟ်", "Mercury"),
            swe.VENUS: ("သောကြာဂြိုဟ်", "Venus"),
            swe.MARS: ("အင်္ဂါဂြိုဟ်", "Mars"),
            swe.JUPITER: ("ကြာသပတေးဂြိုဟ်", "Jupiter"),
            swe.SATURN: ("စနေဂြိုဟ်", "Saturn"),
            swe.URANUS: ("ယူရေးနပ်စ်ဂြိုဟ်", "Uranus"),
            swe.NEPTUNE: ("နက်ပ်ကျွန်းဂြိုဟ်", "Neptune"),
            swe.PLUTO: ("ပလူတိုဂြိုဟ်", "Pluto"),
            swe.MEAN_NODE: ("ရာဟုဂြိုဟ်", "North Node")  # Rahu
        }
        
        # Calculate positions for each planet
        for planet_id, (burmese_name, eng_name) in planet_names.items():
            # Calculate planet position
            pos, flags = swe.calc_ut(jd, planet_id)
            
            # Convert longitude to zodiac sign
            longitude = pos[0]
            sign_num = int(longitude // 30)
            sign_degree = longitude % 30
            
            # Get zodiac sign names
            zodiac_signs = [
                ("မိဿ", "Aries"),
                ("ပြိဿ", "Taurus"),
                ("မေထုန်", "Gemini"),
                ("ကရကဋ်", "Cancer"),
                ("သိဟ်", "Leo"),
                ("ကန်", "Virgo"),
                ("တူ", "Libra"),
                ("ဗြိစ္ဆာ", "Scorpio"),
                ("ဓနု", "Sagittarius"),
                ("မကရ", "Capricorn"),
                ("ကုံ", "Aquarius"),
                ("မိန်", "Pisces")
            ]
            
            sign_burmese, sign_english = zodiac_signs[sign_num]
            
            results['planets'][planet_id] = {
                'burmese_name': burmese_name,
                'english_name': eng_name,
                'longitude': longitude,
                'sign_num': sign_num,
                'sign_burmese': sign_burmese,
                'sign_english': sign_english,
                'position_in_sign': sign_degree,
                'full_position': f"{sign_burmese} {sign_degree:.2f}°"
            }
        
        return results
    
    def display_results(self, results):
        """Display calculation results"""
        output = []
        output.append("=" * 50)
        output.append(f"ဇာတာတွက်ခြင်း ရလဒ်များ")
        output.append("=" * 50)
        output.append(f"ရက်စွဲ: {results['date'].strftime('%Y-%m-%d')}")
        output.append(f"အချိန်: {results['date'].strftime('%H:%M:%S')}")
        output.append(f"ဂျူလီယန် ရက်စွဲ: {results['jd']:.6f}")
        output.append("")
        output.append("ဂြိုဟ်များ၏ တည်နေရာ:")
        output.append("-" * 30)
        
        for planet_id, data in results['planets'].items():
            output.append(f"{data['burmese_name']} ({data['english_name']}):")
            output.append(f"  - {data['full_position']}")
            output.append(f"  - {data['sign_english']} {data['position_in_sign']:.2f}°")
            output.append("")
        
        # Display house cusps
        output.append("အိမ်ထောင်စု အကွေ့များ:")
        output.append("-" * 30)
        for i, cusp in enumerate(results['houses'][:12], 1):
            sign_num = int(cusp // 30)
            sign_deg = cusp % 30
            zodiac_signs = ["မိဿ", "ပြိဿ", "မေထုန်", "ကရကဋ်", "သိဟ်", 
                          "ကန်", "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုံ", "မိန်"]
            output.append(f"အိမ် {i}: {zodiac_signs[sign_num]} {sign_deg:.2f}°")
        
        self.result_text.setText("\n".join(output))


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())