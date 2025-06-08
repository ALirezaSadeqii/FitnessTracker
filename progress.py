import requests
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, 
    QTableWidgetItem, QLabel, QPushButton, QDateEdit,
    QHBoxLayout, QComboBox, QMessageBox, QDialog, 
    QFormLayout, QLineEdit
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_URL = "http://127.0.0.1:8000"

class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.fig.tight_layout()

class ProgressWidget(QWidget):
    def __init__(self, user, back_callback):
        super().__init__()
        self.user = user
        self.back_callback = back_callback
        self.token = self.user.get("token", "")
        
        # Create main layout
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
        QTabBar::tab {
            color: navy;
        }
        """)
        
        # Create tabs
        self.progress_tab = QWidget()
        self.food_log_tab = QWidget()
        self.charts_tab = QWidget()
        
        # Set up tab layouts
        self.setup_progress_tab()
        self.setup_food_log_tab()
        self.setup_charts_tab()
        
        # Add tabs to tab widget
        self.tabs.addTab(self.progress_tab, "Progress")
        self.tabs.addTab(self.food_log_tab, "Food Log")
        self.tabs.addTab(self.charts_tab, "Charts")
        
        # Add header
        header = QLabel("Your Progress")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.back_callback)
        back_btn.setStyleSheet("""
        QPushButton {
            background-color: #4FC3F7;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
            margin: 5px;
        }
        QPushButton:hover {
            background-color: #29B6F6;
        }
        """)
        
        # Add widgets to main layout
        layout.addWidget(header, alignment=Qt.AlignCenter)
        layout.addWidget(self.tabs)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #181B2A; color: #fff;")
        
        # Load data
        self.load_progress()
        self.load_food_logs()

    def setup_progress_tab(self):
        layout = QVBoxLayout()
        
        # Progress table
        self.progress_table = QTableWidget()
        self.progress_table.setStyleSheet("""
        QTableWidget {
            background-color: #2D3250;
            color: white;
            gridline-color: #555;
        }
        QHeaderView::section {
            background-color: #424669;
            color: white;
            padding: 5px;
            border: 1px solid #555;
        }
        """)
        
        # Add controls for adding new progress entry
        controls_layout = QHBoxLayout()
        
        add_progress_btn = QPushButton("Add Progress Entry")
        add_progress_btn.clicked.connect(self.show_add_progress_dialog)
        add_progress_btn.setStyleSheet("""
        QPushButton {
            background-color: #4cc9f0;
            color: white;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #3bb8df;
        }
        """)
        
        controls_layout.addStretch()
        controls_layout.addWidget(add_progress_btn)
        
        # Add to layout
        layout.addWidget(QLabel("Your Progress Records"))
        layout.addWidget(self.progress_table)
        layout.addLayout(controls_layout)
        
        self.progress_tab.setLayout(layout)
    
    def setup_food_log_tab(self):
        layout = QVBoxLayout()
        
        # Date filter controls
        date_layout = QHBoxLayout()
        date_label = QLabel("Select date:")
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.dateChanged.connect(self.filter_food_logs)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_filter)
        date_layout.addStretch()
        
        # Food log table
        self.food_log_table = QTableWidget()
        self.food_log_table.setStyleSheet("""
        QTableWidget {
            background-color: #2D3250;
            color: white;
            gridline-color: #555;
        }
        QHeaderView::section {
            background-color: #424669;
            color: white;
            padding: 5px;
            border: 1px solid #555;
        }
        """)
        
        # Daily nutrition summary
        self.daily_summary = QLabel("Daily Summary: Select a date to view summary")
        self.daily_summary.setStyleSheet("font-size: 16px; margin: 10px 0;")
        
        # Add to layout
        layout.addLayout(date_layout)
        layout.addWidget(self.food_log_table)
        layout.addWidget(self.daily_summary)
        
        self.food_log_tab.setLayout(layout)
    
    def setup_charts_tab(self):
        layout = QVBoxLayout()
        
        # Chart type selector
        chart_layout = QHBoxLayout()
        chart_label = QLabel("Select chart:")
        self.chart_selector = QComboBox()
        self.chart_selector.addItems([
            "Weight Over Time", 
            "BMI Over Time", 
            "Calorie Intake Over Time",
            "Macronutrient Distribution"
        ])
        self.chart_selector.currentIndexChanged.connect(self.update_chart)
        chart_layout.addWidget(chart_label)
        chart_layout.addWidget(self.chart_selector)
        chart_layout.addStretch()
        
        # Canvas for matplotlib
        self.canvas = MplCanvas(width=8, height=4, dpi=100)
        
        # Add to layout
        layout.addLayout(chart_layout)
        layout.addWidget(self.canvas)
        
        self.charts_tab.setLayout(layout)

    def load_progress(self):
        try:
            headers = {}
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}"}
            else:
                QMessageBox.warning(self, "Authentication Error", "Authentication token is missing. Please log out and log in again.")
                return
                
            r = requests.get(f"{API_URL}/progress/{self.user.get('user_id')}", headers=headers)
            if r.status_code == 200:
                self.progress_data = r.json()
                # If no progress data exists, create initial sample data
                if not self.progress_data:
                    self.create_sample_progress_data()
                self.update_progress_table()
                self.update_chart()
            elif r.status_code == 401:
                QMessageBox.warning(self, "Authentication Error", "Not authenticated. Please log out and log in again.")
            else:
                QMessageBox.warning(self, "Error", r.json().get("detail", "Failed to load progress data"))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            # Create sample data for demonstration
            self.create_sample_progress_data()
    
    def create_sample_progress_data(self):
        # Create sample progress data for the last 7 days
        current_date = datetime.datetime.now()
        weight = float(self.user.get('weight', 70))
        height = float(self.user.get('height', 170))
        bmi = round(weight / ((height / 100) ** 2), 2)
        
        self.progress_data = []
        for i in range(7, 0, -1):
            date_str = (current_date - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            # Add some random variation to weight and calorie intake
            variation = (7 - i) * 0.1
            sample_weight = round(weight - variation, 1)
            sample_bmi = round(sample_weight / ((height / 100) ** 2), 2)
            sample_calories = 2000 - (i * 20)
            
            # Add to progress data
            entry = {
                "date": date_str,
                "weight": sample_weight,
                "bmi": sample_bmi,
                "calorie_intake": sample_calories,
                "user_id": self.user.get('user_id')
            }
            self.progress_data.append(entry)
            
            # Save to API
            self.save_progress_entry(entry)
        
        # Update with the actual latest values
        today_str = current_date.strftime("%Y-%m-%d")
        today_entry = {
            "date": today_str,
            "weight": weight,
            "bmi": bmi,
            "calorie_intake": 2000,
            "user_id": self.user.get('user_id')
        }
        self.progress_data.append(today_entry)
        self.save_progress_entry(today_entry)
    
    def save_progress_entry(self, entry):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            r = requests.post(f"{API_URL}/progress", json=entry, headers=headers)
            if r.status_code != 201:
                print(f"Error saving progress entry: {r.json().get('detail', 'Unknown error')}")
        except Exception as e:
            print(f"Error saving progress entry: {str(e)}")
    
    def show_add_progress_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Progress Entry")
        dialog.setFixedWidth(300)
        dialog.setStyleSheet("background-color: #2D3250; color: white;")
        
        layout = QFormLayout(dialog)
        
        # Date field
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setStyleSheet("background-color: #424669; color: white; padding: 5px;")
        
        # Weight field
        weight_edit = QLineEdit()
        weight_edit.setPlaceholderText("Enter weight in kg")
        weight_edit.setText(str(self.user.get('weight', '')))
        weight_edit.setStyleSheet("background-color: #424669; color: white; padding: 5px;")
        
        # BMI is calculated automatically
        bmi_label = QLabel("BMI will be calculated automatically")
        
        # Calorie intake field
        calorie_edit = QLineEdit()
        calorie_edit.setPlaceholderText("Enter daily calorie intake")
        calorie_edit.setText("2000")
        calorie_edit.setStyleSheet("background-color: #424669; color: white; padding: 5px;")
        
        # Add button
        add_btn = QPushButton("Add Entry")
        add_btn.setStyleSheet("""
        QPushButton {
            background-color: #4cc9f0;
            color: white;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #3bb8df;
        }
        """)
        
        # Add fields to layout
        layout.addRow("Date:", date_edit)
        layout.addRow("Weight (kg):", weight_edit)
        layout.addRow("", bmi_label)
        layout.addRow("Calories:", calorie_edit)
        layout.addRow("", add_btn)
        
        def add_entry():
            try:
                weight = float(weight_edit.text())
                calories = int(calorie_edit.text())
                date_str = date_edit.date().toString("yyyy-MM-dd")
                
                # Calculate BMI
                height = float(self.user.get('height', 170))
                bmi = round(weight / ((height / 100) ** 2), 2)
                
                new_entry = {
                    "date": date_str,
                    "weight": weight,
                    "bmi": bmi,
                    "calorie_intake": calories,
                    "user_id": self.user.get('user_id')
                }
                
                # Save to API
                headers = {"Authorization": f"Bearer {self.token}"}
                r = requests.post(f"{API_URL}/progress", json=new_entry, headers=headers)
                
                if r.status_code == 201:
                    # Add to local data and update table
                    self.progress_data.append(r.json())
                    self.update_progress_table()
                    self.update_chart()
                    dialog.accept()
                    QMessageBox.information(self, "Success", "Progress entry added successfully!")
                else:
                    QMessageBox.warning(self, "Error", r.json().get("detail", "Failed to add progress entry"))
            except ValueError:
                QMessageBox.warning(self, "Error", "Please enter valid numbers for weight and calories")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        
        add_btn.clicked.connect(add_entry)
        dialog.exec_()
    
    def load_food_logs(self):
        try:
            # We need to get all food logs for the user
            headers = {}
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}"}
            else:
                QMessageBox.warning(self, "Authentication Error", "Authentication token is missing. Please log out and log in again.")
                return
                
            # For simplicity, we assume there's an endpoint to get all food logs for a user
            r = requests.get(f"{API_URL}/users/{self.user.get('user_id')}/foodlogs", headers=headers)
            if r.status_code == 200:
                self.food_logs = r.json()
                self.filter_food_logs()  # Apply initial filter
            elif r.status_code == 401:
                QMessageBox.warning(self, "Authentication Error", "Not authenticated. Please log out and log in again.")
            else:
                QMessageBox.warning(self, "Error", r.json().get("detail", "Failed to load food log data"))
        except Exception as e:
            # For demo purposes, create some sample data
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            self.food_logs = [
                {
                    "foodlog_id": 1,
                    "food_name": "Egg",
                    "quantity": 2,
                    "date": current_date,
                    "calories": 156,
                    "protein": 12.6,
                    "fat": 10.6,
                    "carbohydrates": 1.2
                },
                {
                    "foodlog_id": 2,
                    "food_name": "Chicken Breast",
                    "quantity": 1,
                    "date": current_date,
                    "calories": 165,
                    "protein": 31,
                    "fat": 3.6,
                    "carbohydrates": 0
                }
            ]
            self.filter_food_logs()  # Apply initial filter
    
    def update_progress_table(self):
        if not hasattr(self, 'progress_data'):
            return
            
        self.progress_table.setRowCount(len(self.progress_data))
        self.progress_table.setColumnCount(4)
        self.progress_table.setHorizontalHeaderLabels(["Date", "Weight (kg)", "BMI", "Calorie Intake"])
        
        for i, entry in enumerate(self.progress_data):
            self.progress_table.setItem(i, 0, QTableWidgetItem(entry.get("date", "")))
            self.progress_table.setItem(i, 1, QTableWidgetItem(str(entry.get("weight", 0))))
            self.progress_table.setItem(i, 2, QTableWidgetItem(str(entry.get("bmi", 0))))
            self.progress_table.setItem(i, 3, QTableWidgetItem(str(entry.get("calorie_intake", 0))))
        
        self.progress_table.resizeColumnsToContents()
    
    def filter_food_logs(self):
        if not hasattr(self, 'food_logs'):
            return
            
        selected_date = self.date_filter.date().toString("yyyy-MM-dd")
        
        # Filter logs for the selected date
        filtered_logs = [log for log in self.food_logs if log.get("date") == selected_date]
        
        # Update table
        self.food_log_table.setRowCount(len(filtered_logs))
        self.food_log_table.setColumnCount(6)
        self.food_log_table.setHorizontalHeaderLabels([
            "Food", "Quantity", "Calories", "Protein (g)", "Fat (g)", "Carbs (g)"
        ])
        
        # Calculate daily totals
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        
        for i, log in enumerate(filtered_logs):
            self.food_log_table.setItem(i, 0, QTableWidgetItem(log.get("food_name", "")))
            self.food_log_table.setItem(i, 1, QTableWidgetItem(str(log.get("quantity", 0))))
            self.food_log_table.setItem(i, 2, QTableWidgetItem(str(log.get("calories", 0))))
            self.food_log_table.setItem(i, 3, QTableWidgetItem(str(log.get("protein", 0))))
            self.food_log_table.setItem(i, 4, QTableWidgetItem(str(log.get("fat", 0))))
            self.food_log_table.setItem(i, 5, QTableWidgetItem(str(log.get("carbohydrates", 0))))
            
            # Add to totals
            total_calories += log.get("calories", 0)
            total_protein += log.get("protein", 0)
            total_fat += log.get("fat", 0)
            total_carbs += log.get("carbohydrates", 0)
        
        self.food_log_table.resizeColumnsToContents()
        
        # Update daily summary
        if filtered_logs:
            self.daily_summary.setText(
                f"Daily Summary for {selected_date}: "
                f"Calories: {total_calories} | "
                f"Protein: {total_protein:.1f}g | "
                f"Fat: {total_fat:.1f}g | "
                f"Carbs: {total_carbs:.1f}g"
            )
        else:
            self.daily_summary.setText(f"No food logs for {selected_date}")
    
    def update_chart(self):
        if not hasattr(self, 'progress_data') or not self.progress_data:
            # Create sample data for demonstration
            self.progress_data = [
                {"date": "2023-05-20", "weight": 75, "bmi": 24.5, "calorie_intake": 2100},
                {"date": "2023-05-21", "weight": 74.8, "bmi": 24.4, "calorie_intake": 2050},
                {"date": "2023-05-22", "weight": 74.5, "bmi": 24.3, "calorie_intake": 2000},
            ]
        
        # Clear the axes
        self.canvas.axes.clear()
        
        # Get selected chart type
        chart_type = self.chart_selector.currentText()
        
        # Sort data by date
        sorted_data = sorted(self.progress_data, key=lambda x: x.get("date", ""))
        
        dates = [entry.get("date", "") for entry in sorted_data]
        
        if chart_type == "Weight Over Time":
            weights = [entry.get("weight", 0) for entry in sorted_data]
            self.canvas.axes.plot(dates, weights, 'b-o')
            self.canvas.axes.set_ylabel('Weight (kg)')
            self.canvas.axes.set_title('Weight Progress Over Time')
        
        elif chart_type == "BMI Over Time":
            bmis = [entry.get("bmi", 0) for entry in sorted_data]
            self.canvas.axes.plot(dates, bmis, 'g-o')
            self.canvas.axes.set_ylabel('BMI')
            self.canvas.axes.set_title('BMI Progress Over Time')
            
            # Add BMI category lines
            self.canvas.axes.axhline(y=18.5, color='r', linestyle='--', alpha=0.5)
            self.canvas.axes.axhline(y=25, color='r', linestyle='--', alpha=0.5)
            self.canvas.axes.axhline(y=30, color='r', linestyle='--', alpha=0.5)
            
            # Add labels for BMI categories
            self.canvas.axes.text(dates[0], 16.5, "Underweight", color='r', alpha=0.7)
            self.canvas.axes.text(dates[0], 21.5, "Normal", color='g', alpha=0.7)
            self.canvas.axes.text(dates[0], 27.5, "Overweight", color='r', alpha=0.7)
            self.canvas.axes.text(dates[0], 32.5, "Obese", color='r', alpha=0.7)
        
        elif chart_type == "Calorie Intake Over Time":
            calories = [entry.get("calorie_intake", 0) for entry in sorted_data]
            self.canvas.axes.plot(dates, calories, 'r-o')
            self.canvas.axes.set_ylabel('Calories')
            self.canvas.axes.set_title('Daily Calorie Intake Over Time')
        
        elif chart_type == "Macronutrient Distribution":
            # For this chart, we'll use the food log data from the current date
            if hasattr(self, 'food_logs') and self.food_logs:
                selected_date = self.date_filter.date().toString("yyyy-MM-dd")
                filtered_logs = [log for log in self.food_logs if log.get("date") == selected_date]
                
                # Calculate total macros
                total_protein = sum(log.get("protein", 0) for log in filtered_logs)
                total_fat = sum(log.get("fat", 0) for log in filtered_logs)
                total_carbs = sum(log.get("carbohydrates", 0) for log in filtered_logs)
                
                # Convert to calories (4 cal/g for protein and carbs, 9 cal/g for fat)
                protein_cals = total_protein * 4
                fat_cals = total_fat * 9
                carb_cals = total_carbs * 4
                
                labels = ['Protein', 'Fat', 'Carbs']
                sizes = [protein_cals, fat_cals, carb_cals]
                colors = ['#4FC3F7', '#F06292', '#FFD54F']
                
                if sum(sizes) > 0:  # Check if we have data
                    self.canvas.axes.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                    self.canvas.axes.set_title(f'Macronutrient Distribution for {selected_date}')
                else:
                    self.canvas.axes.text(0.5, 0.5, f'No food data for {selected_date}', 
                                         horizontalalignment='center', verticalalignment='center',
                                         transform=self.canvas.axes.transAxes)
            else:
                self.canvas.axes.text(0.5, 0.5, 'No food log data available', 
                                     horizontalalignment='center', verticalalignment='center',
                                     transform=self.canvas.axes.transAxes)
        
        # Rotate x-axis labels for better readability
        self.canvas.axes.tick_params(axis='x', rotation=45)
        
        # Adjust layout
        self.canvas.fig.tight_layout()
        
        # Draw the canvas
        self.canvas.draw() 