# main.py

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox # pyright: ignore[reportMissingImports]
from PyQt5.QtCore import QDate, QTime, Qt # pyright: ignore[reportMissingImports]
from Ui_mainApp import Ui_MainWindow
from widgets.chart_widget import BurmeseChartWidget
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
from services.astrology_service import AstrologyService
from services.location_service import LocationService


class BharaniApp(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Services
        self.astro_service = AstrologyService()
        self.location_service = LocationService()

        # Load locations
        self.location_data = self.location_service.load_locations()

        # Setup UI
        self.init_ui()
        self.setup_connections()
        
        # Only populate location combo boxes if they exist in the UI
        if hasattr(self, 'cboStateRegion') and hasattr(self, 'cboCity'):
            self.populate_location_comboboxes()
        
        # Populate timezone list regardless of location combo boxes
        if hasattr(self, 'cboTimezone'):
            self.populate_timezone_list()

    # -----------------------------------------
    # UI Setup
    # -----------------------------------------

    def init_ui(self):
        self.cboDate.setDate(QDate.currentDate())
        self.cboTime.setTime(QTime.currentTime())

    def setup_connections(self):
        self.btnCalculate.clicked.connect(self.calculate_chart)
        
        # Only connect location signals if the UI elements exist
        if hasattr(self, 'cboStateRegion') and hasattr(self, 'cboCity'):
            self.cboStateRegion.currentTextChanged.connect(self.on_state_region_changed)
            self.cboCity.currentTextChanged.connect(self.on_city_changed)

    def populate_timezone_list(self):
        """
        Populate the timezone combo box with common timezones
        """
        if not hasattr(self, 'cboTimezone'):
            print("Timezone combo box not found in UI")
            return
            
        # Clear existing items
        self.cboTimezone.clear()
        
        # Common timezones for astrology applications (hardcoded)
        timezones = [
            ("(UTC+14:00) Samoa", "Pacific/Samoa"),
            ("(UTC+13:00) Tonga", "Pacific/Tongatapu"),
            ("(UTC+12:00) Fiji", "Pacific/Fiji"),
            ("(UTC+11:00) Solomon Islands", "Pacific/Guadalcanal"),
            ("(UTC+10:00) Australia (Brisbane)", "Australia/Brisbane"),
            ("(UTC+10:00) Australia (Sydney)", "Australia/Sydney"),
            ("(UTC+09:30) Australia (Darwin)", "Australia/Darwin"),
            ("(UTC+09:00) Japan", "Asia/Tokyo"),
            ("(UTC+08:00) China", "Asia/Shanghai"),
            ("(UTC+07:00) Thailand", "Asia/Bangkok"),
            ("(UTC+06:30) Myanmar", "Asia/Rangoon"),  # Myanmar timezone
            ("(UTC+05:30) India", "Asia/Kolkata"),     # Indian timezone
            ("(UTC+05:00) Pakistan", "Asia/Karachi"),
            ("(UTC+04:30) Afghanistan", "Asia/Kabul"),
            ("(UTC+03:00) Moscow", "Europe/Moscow"),
            ("(UTC+02:00) South Africa", "Africa/Johannesburg"),
            ("(UTC+01:00) London", "Europe/London"),
            ("(UTC+00:00) UTC", "UTC"),
            ("(UTC-01:00) Azores", "Atlantic/Azores"),
            ("(UTC-02:00) Brazil", "America/Noronha"),
            ("(UTC-03:00) Buenos Aires", "America/Argentina/Buenos_Aires"),
            ("(UTC-04:00) Atlantic Time", "America/Barbados"),
            ("(UTC-05:00) Eastern Time", "America/New_York"),
            ("(UTC-06:00) Central Time", "America/Chicago"),
            ("(UTC-07:00) Mountain Time", "America/Denver"),
            ("(UTC-08:00) Pacific Time", "America/Los_Angeles"),
            ("(UTC-09:00) Alaska", "America/Anchorage"),
            ("(UTC-10:00) Hawaii", "Pacific/Honolulu"),
            ("(UTC-11:00) Midway Island", "Pacific/Midway")
        ]
        
        # Add timezones to the combo box
        for display_name, timezone_value in timezones:
            self.cboTimezone.addItem(display_name, timezone_value)
        
        # Set a default timezone (e.g., Myanmar timezone)
        default_index = self.cboTimezone.findData("Asia/Rangoon")
        if default_index != -1:
            self.cboTimezone.setCurrentIndex(default_index)

    def populate_location_comboboxes(self):
        """
        Populate the location combo boxes with data from CSV
        """
        if not self.location_data:
            print("No location data available")
            return
            
        # Clear existing items
        self.cboStateRegion.clear()
        self.cboCity.clear()
        
        # Add state/region names to the combo box
        state_regions = self.location_service.get_all_states_regions()
        for sr in sorted(state_regions):
            self.cboStateRegion.addItem(sr)
        
        # Set placeholder text if method exists
        if hasattr(self.cboStateRegion, 'setPlaceholderText'):
            self.cboStateRegion.setPlaceholderText("Select State/Region")

    def on_state_region_changed(self, state_region):
        """
        Handle when a state/region is selected
        """
        if not state_region:
            return
            
        # Get cities for the selected state/region
        cities = self.location_service.get_cities_by_state_region(state_region)
        
        # Clear the city combo box
        self.cboCity.clear()
        
        # Add cities to the combo box
        for city, lat, lon in cities:
            self.cboCity.addItem(city, (lat, lon))  # Store lat/lon as item data
        
        # Set placeholder text if method exists
        if hasattr(self.cboCity, 'setPlaceholderText'):
            self.cboCity.setPlaceholderText("Select City")

    def on_city_changed(self, city):
        """
        Handle when a city is selected
        """
        if not city:
            return
            
        # Get the state/region currently selected
        state_region = self.cboStateRegion.currentText()
        
        # Get the city data (lat, lon) from the combo box item
        index = self.cboCity.currentIndex()
        if index >= 0:
            lat_lon = self.cboCity.itemData(index)
            if lat_lon:
                lat, lon = lat_lon
                # Update the latitude and longitude text fields if they exist
                if hasattr(self, 'txtLat') and hasattr(self, 'txtLon'):
                    self.txtLat.setText(str(lat))
                    self.txtLon.setText(str(lon))
                
                # Also update timezone if available and timezone combo box exists
                if hasattr(self, 'cboTimezone'):
                    timezone_info = self.location_service.get_timezone_for_location(state_region, city)
                    if timezone_info:
                        # Update timezone combo box if it exists
                        timezone_value = timezone_info.get('timezone', 'UTC')
                        # Find if timezone already exists in combo box, otherwise add it
                        tz_index = self.cboTimezone.findData(timezone_value)
                        if tz_index == -1:
                            # Add the new timezone if not found
                            display_name = f"(UTC) {timezone_value}"
                            self.cboTimezone.addItem(display_name, timezone_value)
                            tz_index = self.cboTimezone.findData(timezone_value)
                        
                        if tz_index != -1:
                            self.cboTimezone.setCurrentIndex(tz_index)

    # -----------------------------------------
    # Chart Calculation
    # -----------------------------------------

    def calculate_chart(self):

        name = self.txtName.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Name required")
            return

        # Use manual input if location combo boxes don't exist
        birth_data = {
            "year": self.cboDate.date().year(),
            "month": self.cboDate.date().month(),
            "day": self.cboDate.date().day(),
            "hour": self.cboTime.time().hour(),
            "minute": self.cboTime.time().minute(),
            "second": self.cboTime.time().second(),
            "latitude": float(self.txtLat.text()),
            "longitude": float(self.txtLon.text()),
            "timezone": self.cboTimezone.currentData() or self.cboTimezone.currentText(),  # Use currentData() to get stored timezone value
            "ayanamsa": self.cboAyana.currentText(),
            "house_system": self.cboHouseSys.currentText()
        }

        try:
            result = self.astro_service.calculate_full_chart(birth_data)

            self.rasi_chart_widget.set_planet_data(
                result["D1"], True, "D1 - Rāśi"
            )

            self.navamsa_chart_widget.set_planet_data(
                result["D9"], True, "D9 - Navāṁśa"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BharaniApp()
    window.show()
    sys.exit(app.exec_())