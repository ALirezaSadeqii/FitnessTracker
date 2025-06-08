import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QMessageBox, QHBoxLayout, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from edit_profile import EditProfileWidget
from food_log import FoodLogWidget
from progress import ProgressWidget
from styles import get_all_styles, COLORS

API_URL = "http://127.0.0.1:8000"

# Create icon paths
ICON_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'icons')

class LoginWidget(QWidget):
    def __init__(self, switch_to_register, login_success):
        super().__init__()
        self.setObjectName("authWidget")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create content container with centered alignment
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 60, 30, 60)
        content_layout.setAlignment(Qt.AlignCenter)
        
        # Logo and title
        title_label = QLabel("Fitness Tracker")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Track your fitness journey with ease")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Form card
        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_card.setFrameShape(QFrame.StyledPanel)
        form_card.setFrameShadow(QFrame.Raised)
        form_card.setFixedWidth(380)
        
        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(25, 25, 25, 25)
        
        # Login header
        login_label = QLabel("Log In")
        login_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['primary']};")
        login_label.setAlignment(Qt.AlignCenter)
        
        # Email field
        email_label = QLabel("Email")
        email_label.setObjectName("fieldLabel")
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("Enter your email")
        
        # Password field
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter your password")
        self.password.setEchoMode(QLineEdit.Password)
        
        # Forgot password link
        forgot_password = QPushButton("Forgot Password?")
        forgot_password.setObjectName("linkButton")
        forgot_password.setFlat(True)
        
        # Container for forgot password link alignment
        forgot_container = QHBoxLayout()
        forgot_container.addStretch()
        forgot_container.addWidget(forgot_password)
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setObjectName("primaryButton")
        self.login_btn.clicked.connect(self.login)
        
        # Register link
        register_container = QHBoxLayout()
        register_label = QLabel("Don't have an account?")
        register_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        
        register_link = QPushButton("Sign up")
        register_link.setObjectName("linkButton")
        register_link.clicked.connect(switch_to_register)
        
        register_container.addStretch()
        register_container.addWidget(register_label)
        register_container.addWidget(register_link)
        register_container.addStretch()
        
        # Add widgets to form layout
        form_layout.addWidget(login_label)
        form_layout.addSpacing(10)
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password)
        form_layout.addLayout(forgot_container)
        form_layout.addWidget(self.login_btn)
        form_layout.addSpacing(10)
        form_layout.addLayout(register_container)
        
        # Add widgets to content layout
        content_layout.addWidget(title_label)
        content_layout.addWidget(subtitle_label)
        content_layout.addSpacing(40)
        content_layout.addWidget(form_card, 0, Qt.AlignCenter)
        
        main_layout.addWidget(content)
        self.setLayout(main_layout)
        
        self.switch_to_register = switch_to_register
        self.login_success = login_success

    def login(self):
        if not self.email.text() or not self.password.text():
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        data = {
            "username": self.email.text(),
            "password": self.password.text()
        }
        try:
            r = requests.post(f"{API_URL}/login", data=data)
            if r.status_code == 200:
                response_data = r.json()
                token = response_data.get("access_token")
                
                # Store token for subsequent API calls
                if token:
                    # Fetch user info with the token
                    user = self.fetch_user(token)
                    if user:
                        # Add token to user data
                        user['token'] = token
                        QMessageBox.information(self, "Success", "Login successful!")
                        self.login_success(user)
                    else:
                        QMessageBox.warning(self, "Error", "Could not fetch user info.")
                else:
                    QMessageBox.warning(self, "Error", "Login successful, but no authentication token received.")
            else:
                QMessageBox.warning(self, "Error", r.json().get("detail", "Login failed"))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def fetch_user(self, token=None):
        # This assumes you have a /users endpoint to get user info by email
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
                
            r = requests.get(f"{API_URL}/users", params={"email": self.email.text()}, headers=headers)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"Error fetching user: {e}")
        
        # Fallback to basic user info
        return {"email": self.email.text()}

class RegisterWidget(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.setObjectName("authWidget")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create content container with centered alignment
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 40, 30, 40)
        content_layout.setAlignment(Qt.AlignCenter)
        
        # Logo and title
        title_label = QLabel("Fitness Tracker")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Create an account to start your fitness journey")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Form card
        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_card.setFrameShape(QFrame.StyledPanel)
        form_card.setFrameShadow(QFrame.Raised)
        form_card.setFixedWidth(400)
        
        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(25, 25, 25, 25)
        
        # Register header
        register_label = QLabel("Create Account")
        register_label.setObjectName("formHeader")
        register_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(register_label)
        
        # Form fields grid layout
        form_grid = QGridLayout()
        form_grid.setVerticalSpacing(10)
        form_grid.setHorizontalSpacing(10)
        form_grid.setColumnStretch(1, 1)  # Make the second column (input fields) stretch
        
        # Name field
        name_label = QLabel("Name")
        name_label.setObjectName("fieldLabel")
        self.name = QLineEdit()
        self.name.setObjectName("registerField")
        self.name.setPlaceholderText("Enter your full name")
        
        # Email field
        email_label = QLabel("Email")
        email_label.setObjectName("fieldLabel")
        self.email = QLineEdit()
        self.email.setObjectName("registerField")
        self.email.setPlaceholderText("Enter your email")
        
        # Password field
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")
        self.password = QLineEdit()
        self.password.setObjectName("registerField")
        self.password.setPlaceholderText("Create a password")
        self.password.setEchoMode(QLineEdit.Password)
        
        # Height field
        height_label = QLabel("Height (cm)")
        height_label.setObjectName("fieldLabel")
        self.height = QLineEdit()
        self.height.setObjectName("registerField")
        self.height.setPlaceholderText("Height in cm")
        
        # Weight field
        weight_label = QLabel("Weight (kg)")
        weight_label.setObjectName("fieldLabel")
        self.weight = QLineEdit()
        self.weight.setObjectName("registerField")
        self.weight.setPlaceholderText("Weight in kg")
        
        # Goal field
        goal_label = QLabel("Goal")
        goal_label.setObjectName("fieldLabel")
        self.goal = QComboBox()
        self.goal.setObjectName("registerField")
        self.goal.addItems(["Lose Weight", "Maintain Weight", "Gain Weight"])
        
        # Add fields to form grid
        form_grid.addWidget(name_label, 0, 0, Qt.AlignLeft)
        form_grid.addWidget(self.name, 0, 1)
        
        form_grid.addWidget(email_label, 1, 0, Qt.AlignLeft)
        form_grid.addWidget(self.email, 1, 1)
        
        form_grid.addWidget(password_label, 2, 0, Qt.AlignLeft)
        form_grid.addWidget(self.password, 2, 1)
        
        form_grid.addWidget(height_label, 3, 0, Qt.AlignLeft)
        form_grid.addWidget(self.height, 3, 1)
        
        form_grid.addWidget(weight_label, 4, 0, Qt.AlignLeft)
        form_grid.addWidget(self.weight, 4, 1)
        
        form_grid.addWidget(goal_label, 5, 0, Qt.AlignLeft)
        form_grid.addWidget(self.goal, 5, 1)
        
        # Add grid to form layout
        form_layout.addLayout(form_grid)
        form_layout.addSpacing(10)
        
        # Register button
        self.register_btn = QPushButton("Create Account")
        self.register_btn.setObjectName("primaryButton")
        self.register_btn.clicked.connect(self.register)
        form_layout.addWidget(self.register_btn)
        
        # Login link
        login_container = QHBoxLayout()
        login_label = QLabel("Already have an account?")
        login_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        
        login_link = QPushButton("Log in")
        login_link.setObjectName("linkButton")
        login_link.clicked.connect(switch_to_login)
        
        login_container.addStretch()
        login_container.addWidget(login_label)
        login_container.addWidget(login_link)
        login_container.addStretch()
        
        form_layout.addLayout(login_container)
        
        # Add form to content layout
        content_layout.addWidget(title_label)
        content_layout.addWidget(subtitle_label)
        content_layout.addSpacing(20)
        content_layout.addWidget(form_card, 0, Qt.AlignCenter)
        
        main_layout.addWidget(content)
        self.setLayout(main_layout)
        
        # Connect field validations
        self.name.textChanged.connect(self.validate_field)
        self.email.textChanged.connect(self.validate_field)
        self.password.textChanged.connect(self.validate_field)
        self.height.textChanged.connect(self.validate_numeric_field)
        self.weight.textChanged.connect(self.validate_numeric_field)

    def validate_field(self):
        sender = self.sender()
        if not sender.text():
            sender.setStyleSheet("border: 1px solid #ef476f;")
        else:
            sender.setStyleSheet("")
    
    def validate_numeric_field(self):
        sender = self.sender()
        try:
            if sender.text():
                float(sender.text())
                sender.setStyleSheet("")
            else:
                sender.setStyleSheet("border: 1px solid #ef476f;")
        except ValueError:
            sender.setStyleSheet("border: 1px solid #ef476f;")

    def register(self):
        # Validate input fields
        if not self.name.text() or not self.email.text() or not self.password.text() or not self.height.text() or not self.weight.text():
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        try:
            float(self.height.text())
            float(self.weight.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Height and weight must be numbers")
            return
            
        data = {
            "name": self.name.text(),
            "email": self.email.text(),
            "password": self.password.text(),
            "height": float(self.height.text()),
            "weight": float(self.weight.text()),
            "goal": self.goal.currentText()
        }
        try:
            r = requests.post(f"{API_URL}/register", json=data)
            if r.status_code == 201:
                QMessageBox.information(self, "Success", "Registration successful! Please login.")
                # Clear the form and switch to login
                self.name.clear()
                self.email.clear()
                self.password.clear()
                self.height.clear()
                self.weight.clear()
                self.goal.setCurrentIndex(0)
                self.switch_to_login()
            else:
                QMessageBox.warning(self, "Error", r.json().get("detail", "Registration failed"))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class DashboardWidget(QWidget):
    def __init__(self, user, edit_profile_callback, food_log_callback, progress_callback, logout_callback):
        super().__init__()
        self.setObjectName("dashboardWidget")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        
        # Top section with welcome message and user info
        top_section = QHBoxLayout()
        top_section.setContentsMargins(10, 10, 10, 20)
        
        # Welcome message
        welcome_container = QVBoxLayout()
        self.welcome = QLabel(f"Welcome, {user.get('name', user.get('email', 'User'))}!")
        self.welcome.setObjectName("welcomeLabel")
        
        # Today's date and motivation
        today_label = QLabel("Today is your day to get stronger!")
        today_label.setStyleSheet("color: #edf2f4; font-size: 16px;")
        
        welcome_container.addWidget(self.welcome)
        welcome_container.addWidget(today_label)
        welcome_container.addStretch()
        
        # User profile image placeholder
        profile_container = QVBoxLayout()
        profile_container.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        profile_pic = QLabel()
        profile_pixmap = QPixmap(os.path.join(ICON_PATH, "user.png"))
        if not profile_pixmap.isNull():
            profile_pic.setPixmap(profile_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            profile_pic.setText("👤")
            profile_pic.setStyleSheet("font-size: 40px; color: white;")
        
        profile_container.addWidget(profile_pic)
        
        top_section.addLayout(welcome_container)
        top_section.addLayout(profile_container)
        
        # Main content layout - divide into left and right sections
        main_content = QHBoxLayout()
        main_content.setSpacing(25)
        
        # Left section (stats cards)
        left_section = QVBoxLayout()
        
        # Stats section title
        stats_title = QLabel("Your Statistics")
        stats_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        left_section.addWidget(stats_title)
        
        # Stats cards layout - using a grid for better alignment
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Weight card with shadow
        weight_card = QFrame()
        weight_card.setObjectName("statsCard")
        weight_card.setFrameShape(QFrame.StyledPanel)
        weight_card.setFrameShadow(QFrame.Raised)
        
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(15)
        shadow1.setColor(QColor(0, 0, 0, 80))
        shadow1.setOffset(0, 2)
        weight_card.setGraphicsEffect(shadow1)
        
        weight_layout = QVBoxLayout(weight_card)
        weight_layout.setContentsMargins(20, 20, 20, 20)
        
        # Weight icon
        weight_header = QHBoxLayout()
        weight_icon = QLabel("⚖️")
        weight_icon.setStyleSheet("font-size: 20px;")
        
        weight_label = QLabel("Weight")
        weight_label.setObjectName("statLabel")
        
        weight_header.addWidget(weight_icon)
        weight_header.addWidget(weight_label)
        weight_header.addStretch()
        
        weight = user.get('weight', None)
        if weight is not None:
            weight_value = QLabel(f"{weight} kg")
        else:
            weight_value = QLabel("N/A")
        weight_value.setObjectName("statValue")
        
        weight_layout.addLayout(weight_header)
        weight_layout.addWidget(weight_value)
        
        # Height card with shadow
        height_card = QFrame()
        height_card.setObjectName("statsCard")
        height_card.setFrameShape(QFrame.StyledPanel)
        height_card.setFrameShadow(QFrame.Raised)
        
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(15)
        shadow2.setColor(QColor(0, 0, 0, 80))
        shadow2.setOffset(0, 2)
        height_card.setGraphicsEffect(shadow2)
        
        height_layout = QVBoxLayout(height_card)
        height_layout.setContentsMargins(20, 20, 20, 20)
        
        # Height icon
        height_header = QHBoxLayout()
        height_icon = QLabel("📏")
        height_icon.setStyleSheet("font-size: 20px;")
        
        height_label = QLabel("Height")
        height_label.setObjectName("statLabel")
        
        height_header.addWidget(height_icon)
        height_header.addWidget(height_label)
        height_header.addStretch()
        
        height = user.get('height', None)
        if height is not None:
            height_value = QLabel(f"{height} cm")
        else:
            height_value = QLabel("N/A")
        height_value.setObjectName("statValue")
        
        height_layout.addLayout(height_header)
        height_layout.addWidget(height_value)
        
        # BMI card with shadow
        bmi_card = QFrame()
        bmi_card.setObjectName("statsCard")
        bmi_card.setFrameShape(QFrame.StyledPanel)
        bmi_card.setFrameShadow(QFrame.Raised)
        
        shadow3 = QGraphicsDropShadowEffect()
        shadow3.setBlurRadius(15)
        shadow3.setColor(QColor(0, 0, 0, 80))
        shadow3.setOffset(0, 2)
        bmi_card.setGraphicsEffect(shadow3)
        
        bmi_layout = QVBoxLayout(bmi_card)
        bmi_layout.setContentsMargins(20, 20, 20, 20)
        
        # BMI icon
        bmi_header = QHBoxLayout()
        bmi_icon = QLabel("📊")
        bmi_icon.setStyleSheet("font-size: 20px;")
        
        bmi_label = QLabel("BMI")
        bmi_label.setObjectName("statLabel")
        
        bmi_header.addWidget(bmi_icon)
        bmi_header.addWidget(bmi_label)
        bmi_header.addStretch()
        
        if weight is not None and height is not None and height > 0:
            bmi = round(weight / ((height / 100) ** 2), 2)
            bmi_value = QLabel(f"{bmi}")
            
            # Add BMI category
            bmi_category = ""
            if bmi < 18.5:
                bmi_category = "Underweight"
            elif bmi < 24.9:
                bmi_category = "Normal weight"
            elif bmi < 29.9:
                bmi_category = "Overweight"
            else:
                bmi_category = "Obese"
                
            bmi_info = QLabel(bmi_category)
            bmi_info.setStyleSheet("color: #4cc9f0; font-size: 14px;")
            bmi_layout.addLayout(bmi_header)
            bmi_layout.addWidget(bmi_value)
            bmi_layout.addWidget(bmi_info)
        else:
            bmi_value = QLabel("N/A")
            bmi_value.setObjectName("statValue")
            bmi_layout.addLayout(bmi_header)
            bmi_layout.addWidget(bmi_value)
        
        # Add cards to stats grid
        stats_grid.addWidget(weight_card, 0, 0)
        stats_grid.addWidget(height_card, 0, 1)
        stats_grid.addWidget(bmi_card, 1, 0, 1, 2)  # BMI card spans two columns
        
        left_section.addLayout(stats_grid)
        left_section.addStretch(1)
        
        # Right section (navigation buttons)
        right_section = QVBoxLayout()
        
        # Navigation title
        nav_title = QLabel("Quick Actions")
        nav_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        right_section.addWidget(nav_title)
        
        # Create styled buttons with icons
        self.edit_profile_btn = QPushButton("  Edit Profile")
        self.edit_profile_btn.setObjectName("dashboardButton")
        profile_icon = QIcon(os.path.join(ICON_PATH, "user.png"))
        if not profile_icon.isNull():
            self.edit_profile_btn.setIcon(profile_icon)
            self.edit_profile_btn.setIconSize(QSize(24, 24))
        else:
            self.edit_profile_btn.setText("👤  Edit Profile")
        
        self.food_log_btn = QPushButton("  Log Food")
        self.food_log_btn.setObjectName("dashboardButton")
        food_icon = QIcon(os.path.join(ICON_PATH, "food.png"))
        if not food_icon.isNull():
            self.food_log_btn.setIcon(food_icon)
            self.food_log_btn.setIconSize(QSize(24, 24))
        else:
            self.food_log_btn.setText("🍎  Log Food")
        
        self.progress_btn = QPushButton("  View Progress")
        self.progress_btn.setObjectName("dashboardButton")
        progress_icon = QIcon(os.path.join(ICON_PATH, "progress.png"))
        if not progress_icon.isNull():
            self.progress_btn.setIcon(progress_icon)
            self.progress_btn.setIconSize(QSize(24, 24))
        else:
            self.progress_btn.setText("📈  View Progress")
        
        self.logout_btn = QPushButton("  Logout")
        self.logout_btn.setObjectName("logoutButton")
        logout_icon = QIcon(os.path.join(ICON_PATH, "logout.png"))
        if not logout_icon.isNull():
            self.logout_btn.setIcon(logout_icon)
            self.logout_btn.setIconSize(QSize(24, 24))
        else:
            self.logout_btn.setText("🚪  Logout")
        
        # Connect buttons
        self.edit_profile_btn.clicked.connect(edit_profile_callback)
        self.food_log_btn.clicked.connect(food_log_callback)
        self.progress_btn.clicked.connect(progress_callback)
        self.logout_btn.clicked.connect(logout_callback)
        
        # Add buttons to layout
        right_section.addWidget(self.edit_profile_btn)
        right_section.addWidget(self.food_log_btn)
        right_section.addWidget(self.progress_btn)
        right_section.addStretch(1)
        right_section.addWidget(self.logout_btn)
        
        # Add sections to main content layout
        main_content.addLayout(left_section, 3)  # 60% of width
        main_content.addLayout(right_section, 2)  # 40% of width
        
        # Add all components to main layout
        main_layout.addLayout(top_section)
        main_layout.addLayout(main_content)
        
        self.setLayout(main_layout)

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fitness Tracker")
        self.setMinimumSize(800, 650)
        
        # Set app icon if available
        app_icon = QIcon(os.path.join(ICON_PATH, "app_logo.png"))
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        # Apply application style
        self.setStyleSheet(get_all_styles())
        
        # Create central widget
        central_widget = QWidget()
        
        # Setup layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create stacked widget for page navigation
        self.stack = QStackedWidget()
        
        # Create page widgets
        self.login_widget = LoginWidget(self.show_register, self.login_success)
        self.register_widget = RegisterWidget(self.show_login)
        
        # Add pages to stack
        self.stack.addWidget(self.login_widget)
        self.stack.addWidget(self.register_widget)
        
        # Add stack to layout
        main_layout.addWidget(self.stack)
        
        self.setCentralWidget(central_widget)
        self.show_login()
        self.user = None
        
        # Center window on screen
        self.center_on_screen()
    
    def show_login(self):
        self.stack.setCurrentWidget(self.login_widget)

    def show_register(self):
        self.stack.setCurrentWidget(self.register_widget)

    def login_success(self, user):
        self.user = user
        self.dashboard_widget = DashboardWidget(
            user,
            self.show_edit_profile,
            self.show_food_log,
            self.show_progress,
            self.logout
        )
        if self.stack.count() < 3:
            self.stack.addWidget(self.dashboard_widget)
        else:
            self.stack.removeWidget(self.stack.widget(2))
            self.stack.addWidget(self.dashboard_widget)
        self.stack.setCurrentWidget(self.dashboard_widget)

    def show_edit_profile(self):
        self.edit_profile_widget = EditProfileWidget(self.user, self.back_to_dashboard)
        if self.stack.count() < 4:
            self.stack.addWidget(self.edit_profile_widget)
        else:
            self.stack.removeWidget(self.stack.widget(3))
            self.stack.addWidget(self.edit_profile_widget)
        self.stack.setCurrentWidget(self.edit_profile_widget)

    def show_food_log(self):
        self.food_log_widget = FoodLogWidget(self.user, self.back_to_dashboard)
        if self.stack.count() < 5:
            self.stack.addWidget(self.food_log_widget)
        else:
            self.stack.removeWidget(self.stack.widget(4))
            self.stack.addWidget(self.food_log_widget)
        self.stack.setCurrentWidget(self.food_log_widget)

    def show_progress(self):
        self.progress_widget = ProgressWidget(self.user, self.back_to_dashboard)
        if self.stack.count() < 6:
            self.stack.addWidget(self.progress_widget)
        else:
            self.stack.removeWidget(self.stack.widget(5))
            self.stack.addWidget(self.progress_widget)
        self.stack.setCurrentWidget(self.progress_widget)

    def back_to_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard_widget)

    def logout(self):
        self.user = None
        self.show_login()
        
    def center_on_screen(self):
        """Center the window on the screen."""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_()) 