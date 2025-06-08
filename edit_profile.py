import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QPushButton, QMessageBox, QLabel, QFrame, QGridLayout, 
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from styles import COLORS

API_URL = "http://127.0.0.1:8000"

class EditProfileWidget(QWidget):
    def __init__(self, user, back_callback):
        super().__init__()
        self.setObjectName("profileWidget")
        self.user = user
        self.back_callback = back_callback
        self.token = self.user.get("token", "")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Page title
        title_label = QLabel("Edit Profile")
        title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['primary']};")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Form card
        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_card.setFrameShape(QFrame.StyledPanel)
        form_card.setFrameShadow(QFrame.Raised)
        
        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(15)
        
        # Personal info section
        personal_section = QLabel("Personal Information")
        personal_section.setObjectName("sectionLabel")
        
        # Grid for form fields
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setContentsMargins(0, 10, 0, 10)
        
        # Form fields
        self.name = QLineEdit(user.get('name', ''))
        self.name.setPlaceholderText("Your full name")
        
        self.email = QLineEdit(user.get('email', ''))
        self.email.setPlaceholderText("Your email address")
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("New password (leave blank to keep current)")
        self.password.setEchoMode(QLineEdit.Password)
        
        # Physical details section
        physical_section = QLabel("Physical Details")
        physical_section.setObjectName("sectionLabel")
        
        self.height = QLineEdit(str(user.get('height', '')))
        self.height.setPlaceholderText("Height in cm")
        
        self.weight = QLineEdit(str(user.get('weight', '')))
        self.weight.setPlaceholderText("Weight in kg")
        
        self.goal = QComboBox()
        self.goal.addItems(["Lose Weight", "Maintain Weight", "Gain Weight"])
        current_goal = user.get('goal', 'Maintain Weight')
        index = self.goal.findText(current_goal)
        if index >= 0:
            self.goal.setCurrentIndex(index)
        
        # Add fields to grid
        grid.addWidget(QLabel("Name:"), 0, 0)
        grid.addWidget(self.name, 0, 1)
        
        grid.addWidget(QLabel("Email:"), 1, 0)
        grid.addWidget(self.email, 1, 1)
        
        grid.addWidget(QLabel("New Password:"), 2, 0)
        grid.addWidget(self.password, 2, 1)
        
        # Physical details grid
        physical_grid = QGridLayout()
        physical_grid.setSpacing(12)
        physical_grid.setContentsMargins(0, 10, 0, 10)
        
        physical_grid.addWidget(QLabel("Height (cm):"), 0, 0)
        physical_grid.addWidget(self.height, 0, 1)
        
        physical_grid.addWidget(QLabel("Weight (kg):"), 1, 0)
        physical_grid.addWidget(self.weight, 1, 1)
        
        physical_grid.addWidget(QLabel("Goal:"), 2, 0)
        physical_grid.addWidget(self.goal, 2, 1)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(self.save_profile)
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.clicked.connect(self.back_callback)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(back_btn)
        
        # Add all sections to form layout
        form_layout.addWidget(personal_section)
        form_layout.addLayout(grid)
        form_layout.addWidget(physical_section)
        form_layout.addLayout(physical_grid)
        form_layout.addLayout(button_layout)
        
        # Add all widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(form_card)
        
        self.setLayout(main_layout)

    def save_profile(self):
        # Validate input fields
        if not self.name.text() or not self.email.text():
            QMessageBox.warning(self, "Error", "Name and email are required")
            return
            
        try:
            if self.height.text():
                float(self.height.text())
            if self.weight.text():
                float(self.weight.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Height and weight must be numbers")
            return
        
        # Check if we have a token
        if not self.token:
            QMessageBox.warning(self, "Authentication Error", "Not authenticated. Authentication token is missing. Please log out and log in again.")
            return
            
        data = {
            "name": self.name.text(),
            "email": self.email.text(),
            "height": float(self.height.text()) if self.height.text() else self.user.get('height', 0),
            "weight": float(self.weight.text()) if self.weight.text() else self.user.get('weight', 0),
            "goal": self.goal.currentText()
        }
        
        # Only include password if provided
        if self.password.text():
            data["password"] = self.password.text()
            
        try:
            # Add authorization header with token
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Send update request
            r = requests.put(f"{API_URL}/users/{self.user['user_id']}", json=data, headers=headers)
            
            if r.status_code == 200:
                QMessageBox.information(self, "Success", "Profile updated successfully!")
                # Update the user object with new values
                self.user.update(data)
                # Keep the token in the updated user object
                self.user['token'] = self.token
            elif r.status_code == 401:
                QMessageBox.warning(self, "Authentication Error", "Not authenticated. Please log out and log in again.")
            else:
                QMessageBox.warning(self, "Error", r.json().get("detail", "Update failed"))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e)) 