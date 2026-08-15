# location_service.py
import csv
import os
from collections import defaultdict


class LocationService:
    def __init__(self, csv_path=None, timezone_csv_path=None):
        """
        Initialize the LocationService with optional CSV paths
        """
        if csv_path is None:
            # Look for the location CSV file in multiple possible locations
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataCSV.csv"),  # Parent directory
                os.path.join(os.path.dirname(__file__), "dataCSV.csv"),  # Same directory as this file
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "locations.csv"),  # Alternative name
                os.path.join(os.path.dirname(__file__), "locations.csv"),  # Alternative in services dir
            ]
            
            # Find the first path that exists
            for path in possible_paths:
                if os.path.exists(path):
                    csv_path = path
                    break
        
        # We'll skip looking for timezone CSV since we're using hardcoded timezones
        self.csv_path = csv_path
        self.timezone_csv_path = timezone_csv_path
        self.location_data = self.load_locations()
        self.timezone_data = self.create_default_timezones()
    
    def load_locations(self):
        """
        Load location data from CSV file
        Returns a dictionary with structured location data
        Expected CSV columns: SRName, TownName, Latitude, Longitude
        """
        if self.csv_path is None or not os.path.exists(self.csv_path):
            print(f"Warning: Location CSV file not found.")
            print(f"Expected locations: dataCSV.csv, locations.csv in project root or services directory")
            print(f"You can create a dataCSV.csv file with the following format:")
            print("SRName,TownName,Latitude,Longitude")
            print("ရန်ကုန်တိုင်း,ရန်ကုန်,16.8661,96.1951")
            print("မန္တလေးတိုင်း,မန္တလေး,21.975,96.0847")
            return {}
            
        location_data = defaultdict(list)

        try:
            # Open with utf-8-sig encoding to handle BOM (Byte Order Mark) for Unicode files
            with open(self.csv_path, encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sr = row["SRName"].strip()
                    town = row["TownName"].strip()
                    lat = row["Latitude"].strip()
                    lon = row["Longitude"].strip()
                    location_data[sr].append((town, lat, lon))
                    
            return dict(location_data)
        except FileNotFoundError:
            print(f"File {self.csv_path} not found.")
            return {}
        except KeyError as e:
            print(f"Missing expected column in CSV: {str(e)}. Ensure CSV has SRName, TownName, Latitude, Longitude columns.")
            print("Your CSV should have these exact column headers in English: SRName,TownName,Latitude,Longitude")
            return {}
        except UnicodeDecodeError:
            print(f"Encoding error reading {self.csv_path}. Trying alternative encodings...")
            # Try with different encoding
            try:
                with open(self.csv_path, encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sr = row["SRName"].strip()
                        town = row["TownName"].strip()
                        lat = row["Latitude"].strip()
                        lon = row["Longitude"].strip()
                        location_data[sr].append((town, lat, lon))
                        
                return dict(location_data)
            except Exception as e2:
                print(f"Error reading CSV with UTF-8 encoding: {str(e2)}")
                return {}
        except Exception as e:
            print(f"Error loading location data: {str(e)}")
            return {}
    
    def create_default_timezones(self):
        """
        Create default timezone mappings with hardcoded data
        """
        # Hardcoded timezone data directly in the code
        timezone_data = {
            "default": {"timezone": "UTC", "gmt_offset": "+00:00", "tz_name": "UTC"},
            "utc": {"timezone": "UTC", "gmt_offset": "+00:00", "tz_name": "UTC"},
            "Myanmar": {"timezone": "Asia/Yangon", "gmt_offset": "+06:30", "tz_name": "MMT"},
            "Myanmar_Yangon": {"timezone": "Asia/Yangon", "gmt_offset": "+06:30", "tz_name": "MMT"},
            "Myanmar_Mandalay": {"timezone": "Asia/Yangon", "gmt_offset": "+06:30", "tz_name": "MMT"},  # Same timezone as Yangon
            "Myanmar_Naypyidaw": {"timezone": "Asia/Yangon", "gmt_offset": "+06:30", "tz_name": "MMT"},  # Same timezone as Yangon
            "India": {"timezone": "Asia/Kolkata", "gmt_offset": "+05:30", "tz_name": "IST"},
            "India_NewDelhi": {"timezone": "Asia/Kolkata", "gmt_offset": "+05:30", "tz_name": "IST"},
            "India_Mumbai": {"timezone": "Asia/Kolkata", "gmt_offset": "+05:30", "tz_name": "IST"},
            "India_Chennai": {"timezone": "Asia/Kolkata", "gmt_offset": "+05:30", "tz_name": "IST"},
            "India_Kolkata": {"timezone": "Asia/Kolkata", "gmt_offset": "+05:30", "tz_name": "IST"},
            "USA": {"timezone": "America/New_York", "gmt_offset": "-05:00", "tz_name": "EST"},
            "US_NewYork": {"timezone": "America/New_York", "gmt_offset": "-05:00", "tz_name": "EST"},
            "US_LosAngeles": {"timezone": "America/Los_Angeles", "gmt_offset": "-08:00", "tz_name": "PST"},
            "United Kingdom": {"timezone": "Europe/London", "gmt_offset": "+00:00", "tz_name": "GMT"},
            "UK_London": {"timezone": "Europe/London", "gmt_offset": "+00:00", "tz_name": "GMT"},
            "England": {"timezone": "Europe/London", "gmt_offset": "+00:00", "tz_name": "GMT"},
            "UK": {"timezone": "Europe/London", "gmt_offset": "+00:00", "tz_name": "GMT"},
            "France_Paris": {"timezone": "Europe/Paris", "gmt_offset": "+01:00", "tz_name": "CET"},
            "Germany_Berlin": {"timezone": "Europe/Berlin", "gmt_offset": "+01:00", "tz_name": "CET"},
            "Australia_Sydney": {"timezone": "Australia/Sydney", "gmt_offset": "+10:00", "tz_name": "AEST"},
            "Australia_Melbourne": {"timezone": "Australia/Melbourne", "gmt_offset": "+10:00", "tz_name": "AEST"},
            "Australia_Brisbane": {"timezone": "Australia/Brisbane", "gmt_offset": "+10:00", "tz_name": "AEST"},
            "Japan": {"timezone": "Asia/Tokyo", "gmt_offset": "+09:00", "tz_name": "JST"},
            "Japan_Tokyo": {"timezone": "Asia/Tokyo", "gmt_offset": "+09:00", "tz_name": "JST"},
            "China": {"timezone": "Asia/Shanghai", "gmt_offset": "+08:00", "tz_name": "CST"},
            "China_Shanghai": {"timezone": "Asia/Shanghai", "gmt_offset": "+08:00", "tz_name": "CST"},
            "People's Republic of China": {"timezone": "Asia/Shanghai", "gmt_offset": "+08:00", "tz_name": "CST"},
            "Thailand": {"timezone": "Asia/Bangkok", "gmt_offset": "+07:00", "tz_name": "ICT"},
            "Thailand_Bangkok": {"timezone": "Asia/Bangkok", "gmt_offset": "+07:00", "tz_name": "ICT"},
            "Singapore_Singapore": {"timezone": "Asia/Singapore", "gmt_offset": "+08:00", "tz_name": "SGT"},
            "Malaysia_KualaLumpur": {"timezone": "Asia/Kuala_Lumpur", "gmt_offset": "+08:00", "tz_name": "MYT"},
            "Indonesia_Jakarta": {"timezone": "Asia/Jakarta", "gmt_offset": "+07:00", "tz_name": "WIB"},
            "Pakistan_Karachi": {"timezone": "Asia/Karachi", "gmt_offset": "+05:00", "tz_name": "PKT"},
            "Bangladesh_Dhaka": {"timezone": "Asia/Dhaka", "gmt_offset": "+06:00", "tz_name": "BDT"},
            "Afghanistan_Kabul": {"timezone": "Asia/Kabul", "gmt_offset": "+04:30", "tz_name": "AFT"},
            "Iran_Tehran": {"timezone": "Asia/Tehran", "gmt_offset": "+03:30", "tz_name": "IRST"},
            "Russia_Moscow": {"timezone": "Europe/Moscow", "gmt_offset": "+03:00", "tz_name": "MSK"},
            "SouthAfrica_Johannesburg": {"timezone": "Africa/Johannesburg", "gmt_offset": "+02:00", "tz_name": "SAST"},
            "Egypt_Cairo": {"timezone": "Africa/Cairo", "gmt_offset": "+02:00", "tz_name": "EET"},
            "Brazil_SaoPaulo": {"timezone": "America/Sao_Paulo", "gmt_offset": "-03:00", "tz_name": "BRT"},
            "Canada_Toronto": {"timezone": "America/Toronto", "gmt_offset": "-05:00", "tz_name": "EST"},
            "Canada_Vancouver": {"timezone": "America/Vancouver", "gmt_offset": "-08:00", "tz_name": "PST"},
            "Mexico_MexicoCity": {"timezone": "America/Mexico_City", "gmt_offset": "-06:00", "tz_name": "CST"},
            "Argentina_BuenosAires": {"timezone": "America/Argentina/Buenos_Aires", "gmt_offset": "-03:00", "tz_name": "ART"},
            "Alaska_Anchorage": {"timezone": "America/Anchorage", "gmt_offset": "-09:00", "tz_name": "AKST"},
            "Hawaii_Honolulu": {"timezone": "Pacific/Honolulu", "gmt_offset": "-10:00", "tz_name": "HST"},
            "NewZealand_Auckland": {"timezone": "Pacific/Auckland", "gmt_offset": "+12:00", "tz_name": "NZST"},
            "Fiji_Fiji": {"timezone": "Pacific/Fiji", "gmt_offset": "+12:00", "tz_name": "FJT"},
            "Samoa_Apia": {"timezone": "Pacific/Apia", "gmt_offset": "+13:00", "tz_name": "WST"},
            "America": {"timezone": "America/New_York", "gmt_offset": "-05:00", "tz_name": "EST"},
            "United States": {"timezone": "America/New_York", "gmt_offset": "-05:00", "tz_name": "EST"},
        }
        
        return timezone_data
    
    def get_timezone_for_location(self, country, city):
        """
        Get timezone information for a specific location
        """
        # Try to find the exact location first
        location_key = f"{country}_{city}" if country and city else city
        tz_info = self.timezone_data.get(location_key)
        
        if tz_info:
            return tz_info
        
        # Then try just the country
        if country in self.timezone_data:
            return self.timezone_data[country]
        
        # Finally, return the default
        return self.timezone_data.get("default")
    
    def get_all_timezones(self):
        """
        Get all available timezones
        """
        return self.timezone_data
    
    def get_cities_by_state_region(self, state_region):
        """
        Get all cities for a given state/region
        """
        return self.location_data.get(state_region, [])
    
    def get_all_states_regions(self):
        """
        Get all available states/regions
        """
        return list(self.location_data.keys())


def load_location_data(csv_path):
    """
    Legacy function for backward compatibility
    """
    if not os.path.exists(csv_path):
        print(f"Warning: Location CSV file not found at {csv_path}")
        return {}
        
    location_data = defaultdict(list)

    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sr = row["SRName"].strip()
                town = row["TownName"].strip()
                lat = row["Latitude"].strip()
                lon = row["Longitude"].strip()
                location_data[sr].append((town, lat, lon))
    except FileNotFoundError:
        print(f"File {csv_path} not found.")
    except KeyError as e:
        print(f"Missing expected column in CSV: {str(e)}")
    except Exception as e:
        print(f"Error loading location data: {str(e)}")

    return location_data