# divisionClass.py
# ---------------------------------------------
# Vedic Divisional Chart Calculator (D1–D60)
# Compatible with pyswisseph longitude output
# Author: ChatGPT (Jhoro-style logic)
# ---------------------------------------------

import math

class DivisionalChart:
    """
    Vedic Divisional Chart Calculator
    Input  : Planet longitude (0° – 360°)
    Output : Divisional sign (0 – 11)
    """

    ZODIAC_SIGNS = [
        "မိဿ", "ပြိဿ", "မေထုန်", "ကာရကဋ်",
        "သိဟ်", "ကန်", "တူ", "ဗြိစ္ဆာ",
        "ဓနု", "မကာရ", "ကုမ်", "မိန်"
    ]

    def __init__(self):
        pass

    # -------------------------------------------------
    # Core utility functions
    # -------------------------------------------------

    @staticmethod
    def normalize_degree(deg):
        """Normalize degree to 0–360"""
        return deg % 360

    @staticmethod
    def get_rasi(deg):
        """Return Rasi index (0–11)"""
        return int(deg // 30)

    @staticmethod
    def get_rasi_degree(deg):
        """Degree inside sign (0–30)"""
        return deg % 30

    # -------------------------------------------------
    # Generic Divisional Formula (Parāśara system)
    # -------------------------------------------------

    def get_divisional_sign(self, longitude, division):
        """
        Generic formula for D1–D60
        longitude : planet longitude (0–360)
        division  : D number (1–60)
        """

        longitude = self.normalize_degree(longitude)

        rasi = self.get_rasi(longitude)
        rasi_deg = self.get_rasi_degree(longitude)

        part_size = 30 / division
        part_index = int(rasi_deg // part_size)

        # Parashara rule
        div_sign = (rasi * division + part_index) % 12
        return div_sign

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def get_chart(self, longitude, D):
        """
        Main interface
        Returns dict with sign index & name
        """

        sign_index = self.get_divisional_sign(longitude, D)
        return {
            "D": D,
            "sign_index": sign_index,
            "sign_name": self.ZODIAC_SIGNS[sign_index]
        }

    # -------------------------------------------------
    # Convenience methods (commonly used charts)
    # -------------------------------------------------

    def D1(self, longitude):
        return self.get_chart(longitude, 1)

    def D2(self, longitude):
        return self.get_chart(longitude, 2)

    def D3(self, longitude):
        return self.get_chart(longitude, 3)

    def D7(self, longitude):
        return self.get_chart(longitude, 7)

    def D9(self, longitude):
        return self.get_chart(longitude, 9)

    def D10(self, longitude):
        return self.get_chart(longitude, 10)

    def D12(self, longitude):
        return self.get_chart(longitude, 12)

    def D16(self, longitude):
        return self.get_chart(longitude, 16)

    def D20(self, longitude):
        return self.get_chart(longitude, 20)

    def D24(self, longitude):
        return self.get_chart(longitude, 24)

    def D27(self, longitude):
        return self.get_chart(longitude, 27)

    def D30(self, longitude):
        return self.get_chart(longitude, 30)

    def D40(self, longitude):
        return self.get_chart(longitude, 40)

    def D45(self, longitude):
        return self.get_chart(longitude, 45)

    def D60(self, longitude):
        return self.get_chart(longitude, 60)
