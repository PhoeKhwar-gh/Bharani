# font_manager.py
from PyQt5.QtGui import QFont

class ChartFontManager:
    """ဇယားအားလုံးအတွက် font များကိုစနစ်တကျထိန်းချုပ်ရန်"""
    
    # Default font sizes
    DEFAULT_SIZES = {
        "rasi": {
            "symbol": 12,"degree": 10,"title": 14,"zodiac": 12
        },
        "bhava": {
            "symbol": 12,"degree": 0,"title": 14,"zodiac": 0
        },
        "navamsa": {
            "symbol": 12,"degree": 0,"title": 14,"zodiac": 0
        }
    }
    
    def __init__(self):
        self._current_sizes = self.DEFAULT_SIZES.copy()
        self.font_family = ["Pyidaungsu", "Noto Sans Myanmar", "Myanmar3",  "Masterpiece Uni Sans"]
        
    def get_font(self, chart_type, font_type):
        """chart type နဲ့ font type အလိုက် QFont ရယူခြင်း"""
        sizes = self._current_sizes.get(chart_type, self.DEFAULT_SIZES["rasi"])
        size = sizes.get(font_type, 12)
        
        font = QFont(self.font_family, size)
        
        if font_type == "title":
            font.setBold(True)
        elif font_type == "degree":
            font.setItalic(True)
            
        return font
    
    def set_font_size(self, chart_type, font_type, size):
        """Font size ပြောင်းလဲရန်"""
        if chart_type in self._current_sizes:
            if font_type in self._current_sizes[chart_type]:
                self._current_sizes[chart_type][font_type] = size
                
    def scale_all(self, scale_factor):
        """ဖောင့်အားလုံးကို တစ်ပြိုင်နက် scale လုပ်ရန်"""
        for chart_type in self._current_sizes:
            for font_type in self._current_sizes[chart_type]:
                original = self.DEFAULT_SIZES[chart_type][font_type]
                self._current_sizes[chart_type][font_type] = int(original * scale_factor)
    
    def reset_to_default(self):
        """Default size များသို့ပြန်ရန်"""
        self._current_sizes = self.DEFAULT_SIZES.copy()