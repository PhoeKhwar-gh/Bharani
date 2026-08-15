# check_ui.py
import xml.etree.ElementTree as ET
import sys

def check_ui_file(filename):
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        print(f"✓ {filename} is valid XML")
        print(f"  Root element: {root.tag}")
        print(f"  Class attribute: {root.get('class', 'N/A')}")
        return True
    except ET.ParseError as e:
        print(f"✗ {filename} has XML error:")
        print(f"  Error: {e}")
        print(f"  Position: line {e.position[0]}, column {e.position[1]}")
        return False
    except Exception as e:
        print(f"✗ Error checking {filename}: {e}")
        return False

if __name__ == "__main__":
    files = ['mainui.ui', 'vada.ui']
    for file in files:
        import os
        if os.path.exists(file):
            check_ui_file(file)
        else:
            print(f"✗ {file} not found")