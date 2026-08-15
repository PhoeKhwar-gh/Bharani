from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

class PlanetInfoTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.label = QLabel("🪐 ဂြိုဟ်အချက်အလက်များ", self)
        self.label.setStyleSheet("""
            font-size: 14pt; font-weight: bold; padding: 8px; 
            color: #2c3e50; background-color: #3498db; border-radius: 5px;
        """)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.table = QTableWidget()
        self.table.setColumnCount(9)  # ၉ ကော်လံ
        self.table.setHorizontalHeaderLabels([
            "ဂြိုဟ်", "ရာသီ", "ဒီဂရီ", "အသွားနှုန်း", "နက္ခတ်", "ပါဒ်", 
            "ဂြိုဟ်အခြေအနေ", "RL", "NL"
        ])
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { 
                font-size: 10pt; background-color: #ffffff; alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6; border-radius: 5px;
            }
            QHeaderView::section { 
                background-color: #2c3e50; color: white; padding: 8px; 
                border: 1px solid #bdc3c7; font-weight: bold; font-size: 11pt;
            }
            QTableWidget::item { padding: 6px; border-bottom: 1px solid #ecf0f1; }
            QTableWidget::item:selected { background-color: #3498db; color: white; }
        """)
        layout.addWidget(self.table)

    def get_planet_status(self, p_name, lon_d1, lon_d9):
        """ဥုစ်၊ နိစ်၊ ကသစ်၊ မူလတြိဂုဏ်၊ ဝဂ္ဂုတ္တမ၊ နဝင်း စသည်တို့ကို ဒီဂရီကွာခြားချက်ဖြင့် တွက်ချက်ပေးသော Function"""
        classical_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
        if p_name not in classical_planets:
            return "-"

        sign_d1 = int(lon_d1 // 30)
        deg_d1 = lon_d1 % 30
        sign_d9 = int(lon_d9 // 30)

        statuses = []

        # 🔹 ဒီဂရီကွာခြားချက်ကို ဖော်မတ်လုပ်ရန် Helper
        def format_diff(current_deg, target_deg, status_name):
            diff = current_deg - target_deg
            if abs(diff) < 0.05:  # 0.05° အတွင်းဆို အတိအကျနီးပါးဟု သတ်မှတ်
                return f"{status_name} 0°"
            sign_char = "+" if diff < 0 else "-"
            return f"{status_name} {abs(diff):.1f}°{sign_char}"

        # 1️⃣ ဥုစ်အား (Exaltation)
        exalt_map = {
            'Sun': (0, 10), 'Moon': (1, 3), 'Mars': (9, 28), 'Mercury': (5, 15),
            'Jupiter': (3, 5), 'Venus': (11, 27), 'Saturn': (6, 20),
            'Rahu': (2, 20), 'Ketu': (8, 20)
        }
        if p_name in exalt_map:
            ex_sign, ex_deg = exalt_map[p_name]
            if sign_d1 == ex_sign:
                statuses.append(format_diff(deg_d1, ex_deg, "ဥုစ်"))

        # 2️⃣ နိစ်အား (Debilitation)
        deb_map = {
            'Sun': (6, 10), 'Moon': (7, 3), 'Mars': (3, 28), 'Mercury': (11, 15),
            'Jupiter': (9, 5), 'Venus': (5, 27), 'Saturn': (0, 20),
            'Rahu': (8, 20), 'Ketu': (2, 20)
        }
        if p_name in deb_map:
            db_sign, db_deg = deb_map[p_name]
            if sign_d1 == db_sign:
                statuses.append(format_diff(deg_d1, db_deg, "နိစ်"))

        # 3️⃣ ကသစ် (Own Sign)
        own_sign_map = {
            'Sun': 4, 'Moon': 3, 'Mars': (0, 7), 'Mercury': (2, 5),
            'Jupiter': (8, 11), 'Venus': (1, 6), 'Saturn': (9, 10),
            'Rahu': 10, 'Ketu': 7  # ဆရာအလိုက် ကွဲပြားနိုင်ပါသည်
        }
        if p_name in own_sign_map:
            owned_signs = own_sign_map[p_name]
            if isinstance(owned_signs, tuple):
                if sign_d1 in owned_signs:
                    statuses.append("ကသစ်")
            else:
                if sign_d1 == owned_signs:
                    statuses.append("ကသစ်")

        # 4️⃣ မူလတြိဂုဏ် (Moolatrikona) - ✅ BPHS စံနှုန်းအတိုင်း
        mt_map = {
            'Sun': (4, 0, 20), 'Moon': (1, 4, 30), 'Mars': (0, 0, 12),
            'Mercury': (5, 16, 20), 'Jupiter': (8, 0, 10), 'Venus': (6, 0, 15), 
            'Saturn': (10, 0, 20),
            # 👇 BPHS အရ ရာဟု/ကေတု မူလတြိဂုဏ်ရာသီများ
            'Rahu': (2, 0, 15),   # Gemini (မေထုန်) ရာသီ
            'Ketu': (8, 0, 15)    # Sagittarius (ဓနု) ရာသီ
        }
        if p_name in mt_map:
            mt_sign, mt_start, mt_end = mt_map[p_name]
            if sign_d1 == mt_sign and mt_start <= deg_d1 <= mt_end:
                statuses.append("မူလတြိဂုဏ်")

        # 5️⃣ ဝဂ္ဂုတ္တမ (Vargottama)
        if sign_d1 == sign_d9:
            statuses.append("ဝဂ္ဂုတ္တမ")

        # 6️⃣ ဝင်းဝင် (Own Sign in D9)
        own_signs_d9 = {
            'Sun': 4, 'Moon': 1, 'Mars': 0, 'Mercury': 2, 
            'Jupiter': 8, 'Venus': 1, 'Saturn': 10, 
            'Rahu': 10, 'Ketu': 7
        }
        if p_name in own_signs_d9 and sign_d9 == own_signs_d9[p_name]:
            statuses.append("နဝင်း")

        return " + ".join(statuses) if statuses else "သာမာန်"

    def update_data(self, planet_data):
        if not planet_data:
            self.table.setRowCount(0)
            return

        self.table.setRowCount(len(planet_data))

        # 📖 မြန်မာအမည်များ & ဗေဒင်မြေပုံများ
        rashis = ["မိဿ", "ပြိဿ", "မေထုန်", "ကရကဋ်", "သိဟ်", "ကန်", 
                  "တူ", "ဗြိစ္ဆာ", "ဓနု", "မကာရ", "ကုမ်", "မိန်"]
        
        rlords = ["♂", "♀", "☿", "", "☉", "", "♀", "♂", "♃", "♄", "♄", "♃"]
        
        # Nakshatras
        nakshatras = [
            "အဿဝဏီ", "ဘရဏီ", "ကြတ္တိကာ", "ရောဟဏီ", "မိဂသီ", "အဒြ", 
            "ပုဏ္ဏဖုသျှု", "ဖုသျှ", "အသလိဿ", "မာဃ", "ပြုဗ္ဗာဘရဂုဏ္ဏီ", 
            "ဥတ္တရာဘရဂုဏ္ဏီ", "ဟဿဒ", "စိတြ", "သွာတိ", "ဝိသာခါ", "အနုရာဓ",
            "ဇေဋ္ဌ", "မူလ", "ပြုဗ္ဗာသဠ်", "ဥတ္တရာသဠ်", "သရဝဏ်", "ဓနသိဒ္ဓ", 
            "သတ္တဘိသျှ", "ပြုဗ္ဗာပုရပိုက်", "ဥတ္တရာပုရပိုက်", "ရေဝတီ"
        ]

        nlords = ["☊", "♀", "☉", "", "♂", "", "♃", "", "☿"]

        planet_symbols_mm = {
            'Sun': '၁', 'Moon': '၂', 'Mars': '၃', 'Mercury': '၄',
            'Jupiter': '၅', 'Venus': '၆', 'Saturn': '၀',
            'Rahu': '၈', 'Ketu': '၉', 'Lagna': 'လ',
            'Uranus': 'U', 'Neptune': 'N', 'Pluto': 'P'
        }
        
        planet_names_mm = {
            'Sun': 'တနင်္ဂနွေ', 'Moon': 'တနင်္လာ', 'Mars': 'အင်္ဂါ', 
            'Mercury': 'ဗုဒ္ဓဟူး', 'Jupiter': 'ကြာသပတေး', 'Venus': 'သောကြာ', 
            'Saturn': 'စနေ', 'Rahu': 'ရာဟု', 'Ketu': 'ကေတု', 'Lagna': 'လဂ်',
            'Uranus': 'ယူရေးနပ်စ်', 'Neptune': 'နက်ပကျွန်း', 'Pluto': 'ပလူတို'
        }

        nak_len = 360.0 / 27.0   # 13°20'
        pada_len = nak_len / 4.0 # 3°20'

        for i, p in enumerate(planet_data):
            lon_d1 = p.get('longitude', 0)
            p_name = p.get('name', '')
            motion_info = p.get('motion_info', '-')  # ဂြိုဟ်သွားနှုန်း ရယူခြင်း

            # 🔹 ဒီဂရီ ဖော်ပြချက်
            deg_in_sign = lon_d1 % 30
            d = int(deg_in_sign)
            m = int((deg_in_sign * 60) % 60)
            s = int((deg_in_sign * 3600) % 60)
            deg_str = f"{d}° {m:02d}' {s:02d}\""

            # 🔹 ရာသီ & RL
            sign_d1 = int(lon_d1 // 30) % 12
            rashi = rashis[sign_d1]
            rl = rlords[sign_d1]

            # 🔹 နက္ခတ် & NL & ပဒါ
            nak_idx = int(lon_d1 // nak_len) % 27
            nak = nakshatras[nak_idx]
            nl = nlords[nak_idx % 9]
            nak_start = nak_idx * nak_len
            deg_in_nak = lon_d1 - nak_start
            pada = int(deg_in_nak // pada_len) + 1

            # 🔹 နဝင်း (D9) တွက်ချက်ခြင်း
            amsa_len = 30.0 / 9.0
            amsa_idx = int(deg_in_sign / amsa_len)
            
            # ဂန္ထဝင် D9 ပုံသေနည်း: (sign_d1 * 9 + amsa_idx) % 12
            d9_sign_idx = (sign_d1 * 9 + amsa_idx) % 12
            lon_d9 = d9_sign_idx * 30 + (deg_in_sign % amsa_len)

            # 🔹 ဂြိုဟ်အခြေအနေ စစ်ဆေးခြင်း
            status = self.get_planet_status(p_name, lon_d1, lon_d9)

            # 🔹 ဂြိုဟ်အမည် + သင်္ကေတ
            symbol = planet_symbols_mm.get(p_name, '?')
            name_mm = planet_names_mm.get(p_name, p_name)
            planet_text = f"{symbol} {name_mm}"

            # 📊 ဇယားထဲထည့်ခြင်း (၉ ကော်လံ)
            row_data = [planet_text, rashi, deg_str, motion_info, nak, str(pada), status, rl, nl]
            for j, text in enumerate(row_data): 
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if j == 0:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(i, j, item)

        # Column Widths ညှိခြင်း
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, 120)  # ဂြိုဟ်
        self.table.setColumnWidth(1, 80)   # ရာသီ
        self.table.setColumnWidth(2, 100)  # ဒီဂရီ
        self.table.setColumnWidth(3, 110)  # အသွားနှုန်း
        self.table.setColumnWidth(4, 100)  # နက္ခတ်
        self.table.setColumnWidth(5, 50)   # ပဒါ
        self.table.setColumnWidth(6, 130)  # ဂြိုဟ်အခြေအနေ
        self.table.setColumnWidth(7, 60)   # RL
        self.table.setColumnWidth(8, 60)   # NL
    
    def get_planet_relations(self, planet_name):
        # Vedic Naisargika (Natural) Relations အခြေခံ ဇယား
        relations = {
            'Sun':    {'Friend': ['Moon', 'Mars', 'Jupiter'], 'Enemy': ['Venus', 'Saturn']},
            'Moon':   {'Friend': ['Sun', 'Mercury'], 'Enemy': []},
            'Mars':   {'Friend': ['Sun', 'Moon', 'Jupiter'], 'Enemy': ['Mercury']},
            'Mercury':{'Friend': ['Sun', 'Venus'], 'Enemy': ['Moon']},
            'Jupiter':{'Friend': ['Sun', 'Moon', 'Mars'], 'Enemy': ['Mercury', 'Venus']},
            'Venus':  {'Friend': ['Mercury', 'Saturn'], 'Enemy': ['Sun', 'Moon']},
            'Saturn': {'Friend': ['Mercury', 'Venus'], 'Enemy': ['Sun', 'Moon', 'Mars']},
            'Rahu':   {'Friend': ['Mercury', 'Venus', 'Saturn'], 'Enemy': ['Sun', 'Moon']},
            'Ketu':   {'Friend': ['Mars', 'Jupiter', 'Saturn'], 'Enemy': ['Sun', 'Venus']}
        }
        rel = relations.get(planet_name, {'Friend': [], 'Enemy': []})
        return f"မိတ်ဖက်: {', '.join(rel['Friend'])} | ရန်ဘက်: {', '.join(rel['Enemy'])}"