import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from db import ContactDB


class ContactDialog(QDialog):
    def __init__(self, parent=None, contact=None):
        super().__init__(parent)
        self.contact = contact
        self.setWindowTitle("Edit Contact" if contact else "Add Contact")
        self.setMinimumWidth(360)

        layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(80)

        if contact:
            self.name_edit.setText(contact["name"])
            self.phone_edit.setText(contact["phone"])
            self.email_edit.setText(contact["email"])
            self.notes_edit.setPlainText(contact["notes"])

        layout.addRow("Name:", self.name_edit)
        layout.addRow("Phone:", self.phone_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Notes:", self.notes_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def data(self):
        return (
            self.name_edit.text().strip(),
            self.phone_edit.text().strip(),
            self.email_edit.text().strip(),
            self.notes_edit.toPlainText().strip(),
        )

    def accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Name is required.")
            return
        super().accept()


class MainWindow(QMainWindow):
    COLUMNS = ["ID", "Name", "Phone", "Email", "Notes"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contact Manager")
        self.resize(760, 520)
        self.db = ContactDB()

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        search_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search name, phone, email, notes...")
        self.search_edit.textChanged.connect(self.refresh_table)
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.refresh_table)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_search)
        search_row.addWidget(QLabel("Search:"))
        search_row.addWidget(self.search_edit, 1)
        search_row.addWidget(search_btn)
        search_row.addWidget(clear_btn)
        root.addLayout(search_row)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_contact)
        root.addWidget(self.table, 1)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        refresh_btn = QPushButton("Refresh")
        self.add_btn.clicked.connect(self.add_contact)
        self.edit_btn.clicked.connect(self.edit_contact)
        self.delete_btn.clicked.connect(self.delete_contact)
        refresh_btn.clicked.connect(self.refresh_table)
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch(1)
        root.addLayout(btn_row)

        self.statusBar().showMessage("Ready")
        self.refresh_table()

    def selected_contact_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return int(self.table.item(rows[0].row(), 0).text())

    def refresh_table(self):
        term = self.search_edit.text()
        contacts = self.db.search_contacts(term)
        self.table.setRowCount(0)
        for contact in contacts:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, key in enumerate(["id", "name", "phone", "email", "notes"]):
                item = QTableWidgetItem(str(contact[key]))
                if col == 0:
                    item.setData(Qt.UserRole, contact["id"])
                self.table.setItem(row, col, item)
        self.statusBar().showMessage(f"{len(contacts)} contact(s)")

    def clear_search(self):
        self.search_edit.clear()

    def add_contact(self):
        dialog = ContactDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, phone, email, notes = dialog.data()
            self.db.add_contact(name, phone, email, notes)
            self.refresh_table()

    def edit_contact(self):
        contact_id = self.selected_contact_id()
        if contact_id is None:
            QMessageBox.information(self, "No selection", "Select a contact to edit.")
            return
        contact = self.db.get_contact(contact_id)
        dialog = ContactDialog(self, contact)
        if dialog.exec_() == QDialog.Accepted:
            name, phone, email, notes = dialog.data()
            self.db.update_contact(contact_id, name, phone, email, notes)
            self.refresh_table()

    def delete_contact(self):
        contact_id = self.selected_contact_id()
        if contact_id is None:
            QMessageBox.information(self, "No selection", "Select a contact to delete.")
            return
        confirm = QMessageBox.question(
            self,
            "Confirm delete",
            f"Delete contact #{contact_id}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.db.delete_contact(contact_id)
            self.refresh_table()

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
