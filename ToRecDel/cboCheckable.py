from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox, QListView, QApplication, QStyledItemDelegate, QLineEdit
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class CheckableComboBox(QComboBox):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self._checked_items = []
        self._items_dict = {}  # Store key: description mapping
        self._initial_placeholder = "ဇာတာတွဲများ ရွေးချယ်ပါ..."
        
        # Setup the view and model
        self.setView(QListView())
        self.view().setAlternatingRowColors(True)
        self.setModel(QStandardItemModel())
        
        # Make it editable to show custom text
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        
        # Set default items or custom items
        if items is None:
            items = self._get_default_items()
        
        self.setItems(items)
        
        # Connect signals
        self.model().itemChanged.connect(self._on_item_changed)
        self.lineEdit().installEventFilter(self)
        
        # Initial update
        self._update_display()
    
    def setup_ui(self):
        # Create the combobox properly
        self.cboCheckable = CheckableComboBox()
        # Add it to your layout...
    
    def setup_connections(self):
        # Connect to the itemChanged signal from the model
        self.cboCheckable.model().itemChanged.connect(self.on_combobox_selection_changed)
    
    def _get_default_items(self):
        """Return default items list"""
        return [
            ("D2", "ငွေ/ဓနဇာတာ"),
            ("D4", "အိုးအိမ်ဇာတာ"),
            ("D7", "သားသမီးဇာတာ"),
            ("D10", "အလုပ်အကိုင်ဇာတာ"),
            ("D30", "ဒုက္ခ/အပြစ်ဇာတာ"),
            ("D60", "အတိတ်ဘဝကံဇာတာ"),
        ]
    
    def setItems(self, items):
        """Set items in the combobox"""
        self.model().clear()
        self._items_dict.clear()
        self._checked_items.clear()
        
        for key, desc in items:
            self._items_dict[key] = desc
            item = QStandardItem(f"{key} - {desc}")
            item.setCheckable(True)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(key, Qt.UserRole)
            self.model().appendRow(item)
        
        self._update_display()
    
    def _on_item_changed(self, item):
        """Handle item check state changes"""
        # Temporarily disconnect to prevent recursion
        self.model().itemChanged.disconnect(self._on_item_changed)
        
        # If checking an item, uncheck others? (Optional - remove if you want multi-select)
        # if item.checkState() == Qt.Checked:
        #     for i in range(self.model().rowCount()):
        #         other_item = self.model().item(i)
        #         if other_item != item:
        #             other_item.setCheckState(Qt.Unchecked)
        
        self.model().itemChanged.connect(self._on_item_changed)
        self._update_display()
    
    def _update_display(self):
        """Update the displayed text and internal state"""
        checked_keys = []
        checked_descriptions = []
        
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState() == Qt.Checked:
                key = item.data(Qt.UserRole)
                checked_keys.append(key)
                if key in self._items_dict:
                    checked_descriptions.append(f"{key} - {self._items_dict[key]}")
        
        self._checked_items = checked_keys
        
        if checked_keys:
            # Show first item's full description, then count for others
            if len(checked_keys) == 1:
                display_text = checked_descriptions[0]
            else:
                display_text = f"{checked_descriptions[0]} + {len(checked_keys)-1} အခြား"
        else:
            display_text = self._initial_placeholder
        
        self.setEditText(display_text)
        
        # Emit custom signal if needed (define in class)
        # self.checkedItemsChanged.emit(self._checked_items)
    
    def eventFilter(self, obj, event):
        """Keep dropdown open when clicking on items"""
        if obj == self.lineEdit() and event.type() == QEvent.MouseButtonPress:
            self.showPopup()
            return True
        return super().eventFilter(obj, event)
    
    def getCheckedItems(self):
        """Get list of checked item keys"""
        return self._checked_items[:]
    
    def getCheckedItemsWithDesc(self):
        """Get list of checked items as (key, description) tuples"""
        return [(key, self._items_dict.get(key, "")) for key in self._checked_items]
    
    def setCheckedItems(self, keys):
        """Programmatically check items by their keys"""
        # Disconnect signal temporarily
        self.model().itemChanged.disconnect(self._on_item_changed)
        
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            key = item.data(Qt.UserRole)
            item.setCheckState(Qt.Checked if key in keys else Qt.Unchecked)
        
        # Reconnect signal
        self.model().itemChanged.connect(self._on_item_changed)
        self._update_display()
    
    def clearCheckedItems(self):
        """Clear all checked items"""
        self.setCheckedItems([])
    
    def setPlaceholderText(self, text):
        """Set placeholder text when no items are selected"""
        self._initial_placeholder = text
        if not self._checked_items:
            self.setEditText(text)
    
    def showPopup(self):
        """Override to ensure proper width"""
        super().showPopup()
        # Adjust dropdown width if needed
        self.view().setMinimumWidth(self.width())
    
    def wheelEvent(self, event):
        """Disable mouse wheel scrolling to prevent accidental changes"""
        event.ignore()


# Example usage
if __name__ == "__main__":
    app = QApplication([])
    
    # Create the combobox
    combo = CheckableComboBox()
    combo.setPlaceholderText("ဇာတာများ ရွေးချယ်ပါ...")
    combo.setGeometry(100, 100, 300, 30)
    combo.show()
    
    # Example: Programmatically check some items
    # combo.setCheckedItems(["D1", "D4"])
    
    # Example: Get checked items
    # checked = combo.getCheckedItems()
    # print(f"Checked: {checked}")
    
    app.exec_()