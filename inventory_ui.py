import sys
import requests
import functools
import json
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

API_URL = "http://127.0.0.1:8000"

# Thread for fetching inventory data (so the UI doesn’t freeze)
class InventoryFetcher(QThread):
    dataFetched = pyqtSignal(list)

    def run(self):
        try:
            response = requests.get(f"{API_URL}/get-inventory")
            if response.status_code == 200:
                inventory = response.json()
                self.dataFetched.emit(inventory)
            else:
                self.dataFetched.emit([])
        except Exception as e:
            print("Error fetching inventory:", e)
            self.dataFetched.emit([])

class InventoryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Manager")
        self.setGeometry(100, 100, 800, 500)
        
        self.layout = QVBoxLayout()
        
        # Create Table
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        
        # Input Fields for Adding Items
        input_layout = QHBoxLayout()
        self.item_name_input = QLineEdit()
        self.item_name_input.setPlaceholderText("Enter item name")
        self.item_quantity_input = QLineEdit()
        self.item_quantity_input.setPlaceholderText("Enter quantity")

        self.add_button = QPushButton("Add Item")
        self.add_button.clicked.connect(self.add_item)

        self.remove_button = QPushButton("Remove Item")
        self.remove_button.setStyleSheet("background-color: #f44336; color: white;")
        self.remove_button.clicked.connect(self.remove_item)

        # ✅ New Update Button
        self.update_button = QPushButton("Update Item")
        self.update_button.setStyleSheet("background-color: orange; color: white;")
        self.update_button.clicked.connect(self.update_item)

        input_layout.addWidget(QLabel("Item:"))
        input_layout.addWidget(self.item_name_input)
        input_layout.addWidget(QLabel("Qty:"))
        input_layout.addWidget(self.item_quantity_input)
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.remove_button)
        input_layout.addWidget(self.update_button)  # ✅ Added Update Button

        self.layout.addLayout(input_layout)
        self.setLayout(self.layout)

        self.apply_styles()
        self.load_inventory()

    def apply_styles(self):
        self.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
        """)

    def load_inventory(self):
        self.thread = InventoryFetcher()
        self.thread.dataFetched.connect(self.populate_table)
        self.thread.start()

    def populate_table(self, inventory):
        self.table.setRowCount(len(inventory))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Item Name", "Quantity", "Purchase", "Return"])
        
        for row, item in enumerate(inventory):
            self.table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(item["quantity"])))
            
            purchase_button = QPushButton("+ Purchase")
            purchase_button.setStyleSheet("background-color: blue; color: white;")
            purchase_button.clicked.connect(functools.partial(self.modify_quantity, item["name"], 1))
            self.table.setCellWidget(row, 2, purchase_button)
            
            return_button = QPushButton("- Return")
            return_button.setStyleSheet("background-color: red; color: white;")
            return_button.clicked.connect(functools.partial(self.modify_quantity, item["name"], -1))
            self.table.setCellWidget(row, 3, return_button)

    def modify_quantity(self, item_name, change):
        try:
            response = requests.post(f"{API_URL}/update-quantity", json={"name": item_name, "quantity": change})
            if response.status_code == 200:
                QMessageBox.information(self, "Success", f"{item_name} updated successfully.")
                self.load_inventory()
            else:
                QMessageBox.warning(self, "Error", response.json().get("detail", "Failed to update item."))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_item(self):
        item_name = self.item_name_input.text().strip()
        item_quantity = self.item_quantity_input.text().strip()
        
        if not item_name or not item_quantity.isdigit():
            QMessageBox.warning(self, "Input Error", "Enter valid item name and quantity.")
            return
        
        try:
            response = requests.post(f"{API_URL}/add-item", json={"name": item_name, "quantity": int(item_quantity)})
            if response.status_code == 200:
                QMessageBox.information(self, "Success", f"{item_name} added successfully.")
                self.item_name_input.clear()
                self.item_quantity_input.clear()
                self.load_inventory()
            else:
                QMessageBox.warning(self, "Error", response.json().get("detail", "Failed to add item."))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def remove_item(self):
        item_name, ok = QInputDialog.getText(self, "Remove Item", "Enter the item name to remove:")
        
        if ok and item_name.strip():
            payload = {"name": item_name.strip()}
            print("Sending JSON payload:", json.dumps(payload))  # Debugging line

            try:
                response = requests.post(f"{API_URL}/remove-item", json=payload)
                
                print("Response status:", response.status_code)
                print("Response content:", response.text)

                if response.status_code == 200:
                    QMessageBox.information(self, "Success", f"{item_name} removed successfully.")
                    self.load_inventory()
                else:
                    QMessageBox.warning(self, "Error", response.json().get("detail", "Failed to remove item."))
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # ✅ New Update Function
    def update_item(self):
        item_name, ok = QInputDialog.getText(self, "Update Item", "Enter the item name to update:")
        
        if ok and item_name.strip():
            new_quantity, ok2 = QInputDialog.getInt(self, "Update Quantity", f"Enter new quantity for {item_name}:", min=1)
            
            if ok2:
                try:
                    response = requests.post(f"{API_URL}/update-quantity", json={"name": item_name.strip(), "quantity": new_quantity})
                    
                    if response.status_code == 200:
                        QMessageBox.information(self, "Success", f"{item_name} updated successfully.")
                        self.load_inventory()
                    else:
                        QMessageBox.warning(self, "Error", response.json().get("detail", "Failed to update item."))
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec())
