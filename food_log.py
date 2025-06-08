import requests
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QLineEdit, QDateEdit, QPushButton, 
    QMessageBox, QLabel, QHBoxLayout, QScrollArea, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import QDate, Qt

API_URL = "http://127.0.0.1:8000"

class FoodLogWidget(QWidget):
    def __init__(self, user, back_callback):
        super().__init__()
        self.user = user
        self.back_callback = back_callback
        self.token = self.user.get("token", "")
        
        # Debug user info
        print(f"FoodLogWidget initialized with user: {json.dumps(self.user, indent=2, default=str)}")
        
        # Create main layout
        layout = QVBoxLayout()
        
        # Create tabs for Add Food and View Logs
        self.tabs = QTabWidget()
        self.add_food_tab = QWidget()
        self.view_logs_tab = QWidget()
        
        # Create tab content
        self.setup_add_food_tab()
        self.setup_view_logs_tab()
        
        # Add tabs to tab widget
        self.tabs.addTab(self.add_food_tab, "Add Food")
        self.tabs.addTab(self.view_logs_tab, "View Logs")
        
        # Add back button
        back_btn = QPushButton("Back to Dashboard")
        back_btn.clicked.connect(self.back_callback)
        
        # Add widgets to main layout
        layout.addWidget(self.tabs)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
        
        # Load foods after UI is set up
        self.load_foods()
        
    def setup_add_food_tab(self):
        layout = QVBoxLayout()
        
        # Create date picker at the top (shared for all entries)
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_picker)
        layout.addLayout(date_layout)
        
        # Create scroll area for the food log entries
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.foods_layout = QVBoxLayout(scroll_content)
        
        # Add button to add food entries
        add_btn = QPushButton("+ Add Food")
        add_btn.clicked.connect(self.add_food_entry)
        
        # Set up scroll area
        scroll_area.setWidget(scroll_content)
        
        # Add widgets to layout
        layout.addWidget(scroll_area)
        layout.addWidget(add_btn)
        
        # Set layout for the tab
        self.add_food_tab.setLayout(layout)
        
    def setup_view_logs_tab(self):
        layout = QVBoxLayout()
        
        # Create table for food logs
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(6)
        self.logs_table.setHorizontalHeaderLabels(["Date", "Food", "Quantity", "Calories", "Protein", "Fat"])
        
        # Set table properties
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh Logs")
        refresh_btn.clicked.connect(self.load_food_logs)
        
        # Add widgets to layout
        layout.addWidget(self.logs_table)
        layout.addWidget(refresh_btn)
        
        # Set layout for the tab
        self.view_logs_tab.setLayout(layout)
        
        # Load food logs when tab is created
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 1:  # View Logs tab
            self.load_food_logs()

    def load_food_logs(self):
        try:
            # Check if user_id exists
            user_id = self.user.get("user_id")
            if not user_id:
                QMessageBox.warning(self, "Error", "User ID not found. Please log out and log in again.")
                return
                
            # Set up headers with token
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Make request to get food logs
            url = f"{API_URL}/users/{user_id}/foodlogs"
            print(f"Fetching food logs from: {url}")
            r = requests.get(url, headers=headers)
            
            print(f"Food logs response status: {r.status_code}")
            
            if r.status_code == 200:
                food_logs = r.json()
                print(f"Received {len(food_logs)} food logs")
                
                # Clear table
                self.logs_table.setRowCount(0)
                
                # Add rows to table
                for log in food_logs:
                    row = self.logs_table.rowCount()
                    self.logs_table.insertRow(row)
                    
                    # Add data to cells
                    self.logs_table.setItem(row, 0, QTableWidgetItem(log.get("date", "")))
                    self.logs_table.setItem(row, 1, QTableWidgetItem(log.get("food_name", "")))
                    self.logs_table.setItem(row, 2, QTableWidgetItem(str(log.get("quantity", 0))))
                    self.logs_table.setItem(row, 3, QTableWidgetItem(str(log.get("calories", 0))))
                    self.logs_table.setItem(row, 4, QTableWidgetItem(str(log.get("protein", 0))))
                    self.logs_table.setItem(row, 5, QTableWidgetItem(str(log.get("fat", 0))))
                    
            elif r.status_code == 401:
                QMessageBox.warning(self, "Authentication Error", "Your session has expired. Please log out and log in again.")
            else:
                try:
                    error = r.json().get("detail", "Unknown error")
                except:
                    error = f"HTTP error {r.status_code}"
                    
                QMessageBox.warning(self, "Error", f"Failed to load food logs: {error}")
                
        except Exception as e:
            print(f"Exception loading food logs: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error loading food logs: {str(e)}")

    def add_food_entry(self):
        # Create a new food entry form
        entry_widget = QWidget()
        entry_layout = QVBoxLayout(entry_widget)
        
        # Food dropdown
        food_dropdown = QComboBox()
        food_dropdown.setEnabled(False)  # Initially disabled
        
        # Quantity input
        quantity_input = QLineEdit()
        
        # Submit button for this entry
        submit_btn = QPushButton("Submit")
        
        # Nutrition labels
        calories_label = QLabel("Calories: -")
        protein_label = QLabel("Protein: -")
        fat_label = QLabel("Fat: -")
        carb_label = QLabel("Carb: -")
        
        # Add widgets to entry layout
        entry_layout.addWidget(QLabel("Food:"))
        entry_layout.addWidget(food_dropdown)
        entry_layout.addWidget(QLabel("Quantity (units):"))
        entry_layout.addWidget(quantity_input)
        entry_layout.addWidget(calories_label)
        entry_layout.addWidget(protein_label)
        entry_layout.addWidget(fat_label)
        entry_layout.addWidget(carb_label)
        entry_layout.addWidget(submit_btn)
        
        # Add a separator
        separator = QLabel("-------------------------")
        separator.setStyleSheet("color: #888;")
        
        # Add the entry to the foods layout
        self.foods_layout.addWidget(entry_widget)
        self.foods_layout.addWidget(separator)
        
        # Store references to form elements
        entry = {
            'widget': entry_widget,
            'food_dropdown': food_dropdown,
            'quantity_input': quantity_input,
            'calories_label': calories_label,
            'protein_label': protein_label,
            'fat_label': fat_label,
            'carb_label': carb_label,
        }
        
        # Connect signals
        food_dropdown.currentIndexChanged.connect(lambda: self.update_nutrition_labels(entry))
        quantity_input.textChanged.connect(lambda: self.update_nutrition_labels(entry))
        submit_btn.clicked.connect(lambda: self.submit_log(entry))
        
        # If we already have foods loaded, populate the dropdown
        if hasattr(self, 'foods') and self.foods:
            self.populate_food_dropdown(entry['food_dropdown'])
            print("Populated food dropdown for new entry (foods already loaded)")
        else:
            print("Foods not loaded yet, dropdown will be populated when foods are loaded")
    
    def populate_food_dropdown(self, dropdown):
        dropdown.clear()
        for food in self.foods:
            dropdown.addItem(food["name"], food["food_id"])
        dropdown.setEnabled(True)

    def load_foods(self):
        try:
            # Set up headers with token
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
                
            r = requests.get(f"{API_URL}/foods", headers=headers)
            if r.status_code == 200:
                self.foods = r.json()
                
                # Check if foods_layout exists before trying to access it
                if hasattr(self, 'foods_layout'):
                    # Update all existing dropdowns
                    for i in range(self.foods_layout.count()):
                        widget = self.foods_layout.itemAt(i).widget()
                        if widget and hasattr(widget, 'findChild'):
                            dropdown = widget.findChild(QComboBox)
                            if dropdown:
                                self.populate_food_dropdown(dropdown)
                else:
                    print("Warning: foods_layout not available when loading foods")
            elif r.status_code == 401:
                QMessageBox.warning(self, "Authentication Error", "Not authenticated. Authentication token is missing. Please log out and log in again.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to load foods from server. Status: {r.status_code}")
        except Exception as e:
            print(f"Exception loading foods: {str(e)}")
            QMessageBox.critical(self, "Error", f"Exception loading foods: {str(e)}")

    def update_nutrition_labels(self, entry):
        dropdown = entry['food_dropdown']
        idx = dropdown.currentIndex()
        if idx < 0 or not self.foods:
            entry['calories_label'].setText("Calories: -")
            entry['protein_label'].setText("Protein: -")
            entry['fat_label'].setText("Fat: -")
            entry['carb_label'].setText("Carb: -")
            return
        
        food = self.foods[idx]
        try:
            quantity = float(entry['quantity_input'].text()) if entry['quantity_input'].text() else 1
        except ValueError:
            quantity = 1
            
        calories = food["calories"] * quantity
        protein = food["protein"] * quantity
        fat = food["fat"] * quantity
        carb = food["carbohydrates"] * quantity
        
        entry['calories_label'].setText(f"Calories: {calories}")
        entry['protein_label'].setText(f"Protein: {protein}")
        entry['fat_label'].setText(f"Fat: {fat}")
        entry['carb_label'].setText(f"Carb: {carb}")

    def submit_log(self, entry):
        food_id = entry['food_dropdown'].currentData()
        quantity = entry['quantity_input'].text()
        date = self.date_picker.date().toString("yyyy-MM-dd")
        
        if not food_id or not quantity:
            QMessageBox.warning(self, "Validation Error", "Please select a food and enter quantity")
            return
        
        # Check if user_id exists
        user_id = self.user.get("user_id")
        if not user_id:
            error_msg = "User ID not found in the user data. Please log out and log in again."
            print(f"Error: {error_msg}")
            print(f"Current user data: {json.dumps(self.user, indent=2, default=str)}")
            QMessageBox.critical(self, "Error", error_msg)
            return
            
        data = {
            "user_id": user_id,
            "food_id": food_id,
            "quantity": float(quantity),
            "date": date
        }
        
        print(f"Submitting food log: {json.dumps(data, indent=2)}")
        
        try:
            # Ensure we have a token
            if not self.token:
                error_msg = "Authentication token is missing. Please log out and log in again."
                print(f"Error: {error_msg}")
                QMessageBox.critical(self, "Authentication Error", error_msg)
                return
                
            # Set up headers with token
            headers = {"Authorization": f"Bearer {self.token}"}
            print(f"Using authorization token: {self.token[:10]}...")
                
            print(f"Making POST request to {API_URL}/foodlogs")
            r = requests.post(f"{API_URL}/foodlogs", json=data, headers=headers)
            
            print(f"Response status code: {r.status_code}")
            print(f"Response headers: {r.headers}")
            
            try:
                response_text = r.text
                print(f"Response text: {response_text}")
                
                if response_text:
                    try:
                        response_json = r.json()
                        print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                    except json.JSONDecodeError as json_err:
                        print(f"Invalid JSON in response: {json_err}")
                else:
                    print("Response text is empty")
            except Exception as parse_err:
                print(f"Error processing response: {parse_err}")
            
            if r.status_code == 201:
                QMessageBox.information(self, "Success", "Food log submitted!")
                # Clear the form for reuse
                entry['quantity_input'].clear()
                entry['food_dropdown'].setCurrentIndex(0)
                self.update_nutrition_labels(entry)
                
                # Switch to View Logs tab and refresh logs
                self.tabs.setCurrentIndex(1)
                self.load_food_logs()
            elif r.status_code == 401:
                error_msg = "Authentication failed. Please log out and log in again."
                QMessageBox.warning(self, "Authentication Error", error_msg)
            else:
                error_detail = "Failed to log food"
                try:
                    if r.text:
                        try:
                            error_detail = r.json().get("detail", error_detail)
                        except:
                            error_detail = f"Failed to log food: {r.text}"
                except:
                    pass
                QMessageBox.warning(self, "Error", f"Status: {r.status_code}, Detail: {error_detail}")
        except Exception as e:
            print(f"Exception in submit_log: {str(e)}")
            QMessageBox.critical(self, "Error", str(e)) 