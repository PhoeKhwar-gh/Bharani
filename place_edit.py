# -*- coding: utf-8 -*-
import sys, os, csv, time, requests, pandas as pd, io
import folium
from timezonefinder import TimezoneFinder
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, pyqtSlot, QObject
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from Ui_latlon import Ui_Dialog

# === Configuration ===
CSV_FILE = "dataCSV.csv"
CSV_COLUMNS = ["Country", "SRName", "TownName", "Latitude", "Longitude", "timezone"]
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org"
USER_AGENT = "AstrologyLocator/1.0 (phoekhwarjune@gmail.com)"

def clean_state_name(state_text):
    """
    Remove 'တိုင်းဒေသကြီး', 'ပြည်နယ်' suffixes and return clean name
    """
    if not state_text:
        return ""
    
    suffixes = [
        "တိုင်းဒေသကြီး",
        "ပြည်နယ်",
        "ဒေသ",
        "တိုင်း"
    ]
    
    clean_name = state_text.strip()
    for suffix in suffixes:
        if clean_name.endswith(suffix):
            clean_name = clean_name[:-len(suffix)]
            break
    
    return clean_name.strip()

class MapBridge(QObject):
    map_clicked = pyqtSignal(float, float)
    
    @pyqtSlot(str, str)
    def onMapClick(self, lat_str, lon_str):
        try:
            lat = float(lat_str)
            lon = float(lon_str)
            self.map_clicked.emit(lat, lon)
        except ValueError:
            pass

class SearchThread(QThread):
    finished = pyqtSignal(list, bool)
    
    def __init__(self, query, myanmar_only=False):
        super().__init__()
        self.query = query
        self.myanmar_only = myanmar_only

    def run(self):
        params = {"q": self.query, "format": "json", "limit": 20, "addressdetails": 1}
        if self.myanmar_only:
            params["countrycodes"] = "mm"
        headers = {"User-Agent": USER_AGENT}
        try:
            time.sleep(0.5)
            r = requests.get(f"{NOMINATIM_API_URL}/search", params=params, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.json()
            self.finished.emit(data, True)
        except Exception:
            self.finished.emit([], False)

class ReverseGeocodeThread(QThread):
    result_ready = pyqtSignal(str, str, str, float, float)
    
    def __init__(self, lat, lon):
        super().__init__()
        self.lat = lat
        self.lon = lon

    def run(self):
        params = {"lat": self.lat, "lon": self.lon, "format": "json", "addressdetails": 1, "zoom": 10}
        headers = {"User-Agent": USER_AGENT}
        try:
            time.sleep(0.5)
            r = requests.get(f"{NOMINATIM_API_URL}/reverse", params=params, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            address = data.get("address", {})
            city = (address.get("village") or address.get("town") or address.get("city") or
                    address.get("state") or data.get("display_name", "").split(",")[0].strip())
            country = address.get("country", "Myanmar")
            display_name = data.get("display_name", "")
            self.result_ready.emit(city, country, display_name, self.lat, self.lon)
        except Exception:
            self.result_ready.emit("", "Myanmar", "", self.lat, self.lon)

class AstroLocatorApp(QtWidgets.QDialog, Ui_Dialog):
    # Signal to send data back to parent
    location_saved = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("နေရာဒေသအသစ် ရှာဖွေရေးကိရိယာ 🌏")
        
        self.locations = []
        self.map_ready = False
        self._map_controller_injected = False   # ✅ 
        self.tf = TimezoneFinder()
        self.reverse_thread = None
        
        # Set window icon
        self.setWindowIcon(QtGui.QIcon("res/search.png"))
        
        # Bridge and web view
        self.bridge = MapBridge()
        self.bridge.map_clicked.connect(self.on_map_click)
        self.setup_webview()

        # Connect signals
        self.btnSearch.clicked.connect(self.start_search)
        self.txtSearch.returnPressed.connect(self.start_search)
        self.btnSave.clicked.connect(self.save_location)
        self.listResults.itemClicked.connect(self.on_result_selected)

        # Load CSV data
        self.load_csv_data()

    def show_status_message(self, message):
        """Show status on parent main window if available (QDialog has no status bar)."""
        parent = self.parent()
        if parent is not None and hasattr(parent, 'statusbar') and parent.statusbar is not None:
            parent.statusbar.showMessage(message)
        else:
            print(message)

    def setup_webview(self):
        layout = QtWidgets.QVBoxLayout(self.frmWeb)
        layout.setContentsMargins(0, 0, 0, 0)
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        self.web_view.loadFinished.connect(self.on_map_loaded)
        self.create_map_html()

    def create_map_html(self):
        """Create a plain Folium map without embedded JavaScript."""
        m = folium.Map(location=[16.8, 96.15], zoom_start=6, tiles="CartoDB positron")
        self.map_var_name = m.get_name()
        data = io.BytesIO()
        m.save(data, close_file=False)
        html = data.getvalue().decode()
        self.web_view.setHtml(html)

    def on_map_loaded(self):
        """Inject the JavaScript controller after the map HTML is loaded."""

        if self._map_controller_injected:
            return

        self._map_controller_injected = True
        self.map_ready = True

        print("Map loaded, injecting controller...")

        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        js_code = f"""
        (function() {{
            console.log("Injecting qwebchannel.js...");
            var script = document.createElement('script');
            script.src = 'qrc:///qtwebchannel/qwebchannel.js';
            script.onload = function() {{
                console.log("qwebchannel.js loaded, setting up channel...");
                if (typeof qt === 'undefined' || typeof qt.webChannelTransport === 'undefined') {{
                    console.error("qt.webChannelTransport missing");
                    return;
                }}
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    window.bridge = channel.objects.bridge;
                    console.log("Bridge received: ", window.bridge);
                    setupMap();
                }});
            }};
            document.head.appendChild(script);

            function setupMap() {{
                var mapVarName = "{self.map_var_name}";
                if (window[mapVarName] && window[mapVarName] instanceof L.Map) {{
                    window.map = window[mapVarName];
                    window.map.on('click', function(e) {{
                        var lat = e.latlng.lat.toFixed(6);
                        var lng = e.latlng.lng.toFixed(6);
                        console.log("Map clicked: ", lat, lng);
                        if (window.bridge) window.bridge.onMapClick(lat, lng);
                    }});

                    window.addMarker = function(lat, lon, popup, zoom) {{
                        if (!window.map) return;
                        if (window.currentMarker) window.map.removeLayer(window.currentMarker);
                        window.currentMarker = L.marker([lat, lon]).addTo(window.map);
                        if (popup) window.currentMarker.bindPopup(popup).openPopup();
                        if (zoom) window.map.setView([lat, lon], zoom, {{animate:true, duration:1.0}});
                        console.log("Marker added at ", lat, lon);
                    }};
                }} else {{
                    setTimeout(setupMap, 100);
                }}
            }}
        }})();
        """

        self.web_view.page().runJavaScript(js_code)

    def add_marker(self, lat, lon, popup_text=None, zoom_level=15):
        """Add a marker on the map, retrying if the map is not ready."""
        if not self.map_ready:
            QTimer.singleShot(200, lambda: self.add_marker(lat, lon, popup_text, zoom_level))
            return

        if popup_text is None:
            popup_text = f"({lat:.4f}, {lon:.4f})"
        popup_text = popup_text.replace("'", "\\'").replace('"', '\\"')
        js = f"if (window.addMarker) window.addMarker({lat}, {lon}, '{popup_text}', {zoom_level}); else console.error('addMarker not defined');"
        self.web_view.page().runJavaScript(js)

    def load_csv_data(self):
        if not os.path.exists(CSV_FILE):
            self.create_empty_csv()
            return

        try:
            df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            
            # Column mapping for new CSV structure
            column_mapping = {
                'Country': ['Country', 'country', 'Nation'],
                'SRName': ['SRName', 'state', 'State', 'Region'],
                'TownName': ['TownName', 'city', 'City', 'Town'],
                'Latitude': ['Latitude', 'latitude', 'lat'],
                'Longitude': ['Longitude', 'longitude', 'lon'],
                'timezone': ['timezone', 'Timezone', 'TZ']
            }
            
            for target, possible_names in column_mapping.items():
                for name in possible_names:
                    if name in df.columns:
                        df.rename(columns={name: target}, inplace=True)
                        break
            
            # Ensure all required columns exist
            for col in CSV_COLUMNS:
                if col not in df.columns:
                    if col == 'timezone':
                        df[col] = "Asia/Rangoon"
                    else:
                        df[col] = ""
            
            required = ['Country', 'SRName', 'TownName', 'Latitude', 'Longitude', 'timezone']
            missing = [c for c in required if c not in df.columns]
            if missing:
                QtWidgets.QMessageBox.warning(self, "CSV Format Warning",
                    f"Missing columns: {missing}\nFound: {list(df.columns)}")
                return

            self.locations = df.to_dict("records")
            print(f"[Info] Loaded {len(self.locations)} rows.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "အမှား", f"CSV ဖိုင်ကို ဖတ်၍မရပါ:\n{e}")

    def create_empty_csv(self):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()

    def on_map_click(self, lat, lon):
        self.txtLat.setText(f"{lat:.6f}")
        self.txtLon.setText(f"{lon:.6f}")
        self.lblCache.setText(f"📍 {lat:.6f}, {lon:.6f}\n(နေရာအမည်ရှာနေဆဲ...)")
        self.add_marker(lat, lon, zoom_level=15)

        tz = self.tf.timezone_at(lat=lat, lng=lon)
        self.txtTimezone.setText(tz if tz else "Asia/Rangoon")

        if self.reverse_thread and self.reverse_thread.isRunning():
            self.reverse_thread.quit()
            self.reverse_thread.wait()
        self.reverse_thread = ReverseGeocodeThread(lat, lon)
        self.reverse_thread.result_ready.connect(self.on_reverse_geocode_result)
        self.reverse_thread.finished.connect(self.reverse_thread.deleteLater)
        self.reverse_thread.finished.connect(lambda: setattr(self, 'reverse_thread', None))
        self.reverse_thread.start()
        self.statusBar().setText("မြို့အမည်ရှာနေသည်...")

    def on_reverse_geocode_result(self, city_name, country_name, display_name, lat, lon):
        if city_name and city_name.strip():
            self.txtCity.setText(city_name)
            
            if country_name:
                self.txtCountry.setText(country_name)
                
            self.statusBar().setText(f"📍{city_name}, {country_name}, ({lat:.4f}, {lon:.4f})")
            self.lblCache.setText(f"📍 {city_name}\n{lat:.6f}, {lon:.6f}")
        else:
            self.statusBar().setText(f"🗺️ မြို့မတွေ့ရှိပါ ({lat:.4f}, {lon:.4f})")
            self.lblCache.setText(f"🗺️ မြို့မတွေ့ရှိပါ\n{lat:.6f}, {lon:.6f}")

    def start_search(self):
        query = self.txtSearch.text().strip()
        if not query:
            QtWidgets.QMessageBox.warning(self, "သတိပေးချက်", "ရှာဖွေရန် စာသားထည့်ပါ။")
            return
        self.btnSearch.setEnabled(False)
        self.btnSearch.setText("🔍 ရှာနေသည်...")
        self.listResults.clear()
        self.listResults.setVisible(True)
        self.listResults.addItem("🔍 ရှာဖွေနေသည်...")
        self.search_thread = SearchThread(query, False)
        self.search_thread.finished.connect(self.handle_search_result)
        self.search_thread.start()

    def handle_search_result(self, results, success):
        self.btnSearch.setEnabled(True)
        self.btnSearch.setText("ရှာပါ")
        self.listResults.clear()
        if success and results:
            for item in results:
                address = item.get("address", {})
                name = (address.get("village") or address.get("town") or address.get("city") or
                        address.get("state") or item.get("display_name", "").split(",")[0].strip())
                
                admin_parts = []
                if address.get("state"):
                    admin_parts.append(address["state"])
                if address.get("district"):
                    admin_parts.append(address["district"])
                elif address.get("county"):
                    admin_parts.append(address["county"])
                if address.get("city") and address["city"] != name:
                    admin_parts.append(address["city"])
                elif address.get("town") and address["town"] != name:
                    admin_parts.append(address["town"])
                admin_str = ", ".join(admin_parts) if admin_parts else ""
                
                country = address.get("country", "")
                if admin_str:
                    display = f"{name} ({admin_str})"
                else:
                    display = name
                if country and country not in display:
                    display += f" [{country}]"
                    
                self.listResults.addItem(display)
                self.listResults.item(self.listResults.count() - 1).setData(QtCore.Qt.UserRole, item)
            self.listResults.setVisible(True)
        else:
            self.listResults.addItem("❌ ရလဒ်မတွေ့ရှိပါ")
            self.listResults.setVisible(True)

    def on_result_selected(self, item):
        data = item.data(QtCore.Qt.UserRole)
        if not data:
            return
        lat = float(data.get("lat", 0))
        lon = float(data.get("lon", 0))
        addr = data.get("address", {})
        
        # Get city/village name
        city = addr.get("village") or addr.get("town") or addr.get("city") or ""
        if city:
            self.txtCity.setText(city)
        
        # Get and clean state/region name
        state_raw = addr.get("state", "")
        if state_raw:
            state_clean = clean_state_name(state_raw)
            self.txtState.setText(state_clean)
        
        # Get country
        country = addr.get("country", "Myanmar")
        self.txtCountry.setText(country)
        
        # Fill coordinates
        self.txtLat.setText(f"{lat:.6f}")
        self.txtLon.setText(f"{lon:.6f}")
        
        QTimer.singleShot(300, lambda: self.add_marker(lat, lon, zoom_level=15))
        
        # Timezone
        tz = self.tf.timezone_at(lat=lat, lng=lon)
        self.txtTimezone.setText(tz if tz else "Asia/Rangoon")
        
        self.lblCache.setText(f"📍 {city}\n{lat:.6f}, {lon:.6f}")
        self.show_status_message(f"Selected: {city} [{state_clean if state_raw else 'N/A'}]")

    def closeEvent(self, event):
        if self.reverse_thread and self.reverse_thread.isRunning():
            self.reverse_thread.quit()
            self.reverse_thread.wait()
        super().closeEvent(event)

    def save_location(self):
        country = self.txtCountry.text().strip()
        state = self.txtState.text().strip()
        city = self.txtCity.text().strip()
        lat = self.txtLat.text().strip()
        lon = self.txtLon.text().strip()
        timezone = self.txtTimezone.text().strip()

        if not city:
            QtWidgets.QMessageBox.warning(self, "သတိပေးချက်", "မြို့/ကျေးရွာ အမည်ထည့်ပါ။")
            return
        if not country:
            country = "Myanmar"
        if not lat or not lon:
            QtWidgets.QMessageBox.warning(self, "သတိပေးချက်", "Lat/Lon ထည့်ပါ။")
            return

        try:
            lat_val = float(lat)
            lon_val = float(lon)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "သတိပေးချက်", "Lat/Lon သည် ဒသမကိန်းဂဏန်းဖြစ်ရပါမည်။")
            return

        if not timezone or timezone == "(unknown)":
            timezone = "Asia/Rangoon"

        file_exists = os.path.exists(CSV_FILE)
        try:
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                if not file_exists:
                    writer.writeheader()
                writer.writerow({
                    "Country": country,
                    "SRName": state,
                    "TownName": city,
                    "Latitude": f"{lat_val:.6f}",
                    "Longitude": f"{lon_val:.6f}",
                    "timezone": timezone
                })
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "အမှား", f"ဖိုင်သိမ်းဆည်း၍မရပါ:\n{e}")
            return

        self.locations.append({
            "Country": country,
            "SRName": state,
            "TownName": city,
            "Latitude": f"{lat_val:.6f}",
            "Longitude": f"{lon_val:.6f}",
            "timezone": timezone
        })
        
        # Emit signal with saved data
        location_data = {
            "Country": country,
            "SRName": state,
            "TownName": city,
            "Latitude": f"{lat_val:.6f}",
            "Longitude": f"{lon_val:.6f}",
            "timezone": timezone
        }
        self.location_saved.emit(location_data)
        
        QtWidgets.QMessageBox.information(self, "အောင်မြင်ပါသည်", f"✅ '{city}' ကို သိမ်းဆည်းပြီးပါပြီ။")
        self.statusBar().setText(f"✅ Saved: {city}")
        self.accept()

    def statusBar(self):
        """Create a simple status bar for QDialog"""
        if not hasattr(self, '_status_bar'):
            self._status_bar = QtWidgets.QLabel(" ")
            self._status_bar.setStyleSheet("color: gray; padding: 5px;")
            self.leftLayout.addWidget(self._status_bar)
        return self._status_bar

# For standalone testing
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QtGui.QFont("Pyidaungsu", 10)
    app.setFont(font)
    win = AstroLocatorApp()
    win.show()
    sys.exit(app.exec_())