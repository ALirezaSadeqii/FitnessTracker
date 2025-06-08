"""
Centralized stylesheet definitions for the Fitness Tracker application.
This file contains all common styles used across the application to ensure 
a consistent look and feel.
"""

# Color palette - simplified with higher contrast
COLORS = {
    'primary': '#4361ee',           # Blue primary
    'primary_dark': '#3a56d4',      # Darker blue
    'secondary': '#06d6a0',         # Green secondary
    'accent': '#ef476f',            # Pink accent
    'background': '#0a1128',        # Navy background
    'card': '#ffffff',              # White card background
    'text_primary': '#333333',      # Dark text for light backgrounds
    'text_secondary': '#6c757d',    # Medium gray text
    'border': '#dee2e6',            # Light gray border
    'success': '#06d6a0',           # Green success
    'warning': '#ffc107',           # Yellow warning
    'error': '#ef476f',             # Pink-red error
}

# Main application style
MAIN_STYLE = f"""
QMainWindow, QDialog {{
    background-color: {COLORS['background']};
}}

QLabel {{
    color: {COLORS['text_primary']};
    font-size: 14px;
    font-family: Arial, sans-serif;
}}

QLineEdit, QComboBox, QDateEdit {{
    padding: 10px 12px;
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    background-color: {COLORS['card']};
    color: {COLORS['text_primary']};
    font-size: 14px;
    min-height: 20px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border: 2px solid {COLORS['primary']};
}}

QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 15px;
    font-weight: bold;
    font-size: 14px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary']};
}}

QComboBox {{
    padding-right: 20px;
}}

QComboBox::drop-down {{
    border: 0px;
    width: 20px;
}}

QTableWidget {{
    background-color: {COLORS['card']};
    alternate-background-color: #f8f9fa;
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    gridline-color: #e9ecef;
}}

QTableWidget::item {{
    padding: 6px;
    border-bottom: 1px solid #f2f2f2;
}}

QHeaderView::section {{
    background-color: {COLORS['primary']};
    color: white;
    padding: 8px;
    border: none;
    font-weight: bold;
}}

QMessageBox {{
    background-color: {COLORS['card']};
    color: {COLORS['text_primary']};
}}

QMessageBox QPushButton {{
    min-width: 80px;
    margin: 0 5px;
}}
"""

# Dashboard-specific style
DASHBOARD_STYLE = f"""
QWidget#dashboardWidget {{
    background-color: {COLORS['background']};
}}

QLabel#welcomeLabel {{
    color: white;
    font-size: 24px;
    font-weight: bold;
}}

QFrame#statsCard {{
    background-color: white;
    border-radius: 10px;
    padding: 15px;
}}

QLabel#statLabel {{
    color: {COLORS['text_secondary']};
    font-size: 14px;
}}

QLabel#statValue {{
    color: {COLORS['text_primary']};
    font-size: 22px;
    font-weight: bold;
}}

QPushButton#dashboardButton {{
    background-color: {COLORS['primary']};
    color: white;
    border-radius: 6px;
    padding: 12px;
    font-size: 14px;
    text-align: left;
    padding-left: 15px;
    margin: 5px 0;
}}

QPushButton#dashboardButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton#logoutButton {{
    background-color: {COLORS['accent']};
}}

QPushButton#logoutButton:hover {{
    background-color: #e0366a;
}}
"""

# Login/Register specific style
AUTH_STYLE = f"""
QWidget#authWidget {{
    background-color: {COLORS['background']};
}}

QLabel#titleLabel {{
    color: white;
    font-size: 28px;
    font-weight: bold;
}}

QLabel#subtitleLabel {{
    color: #adb5bd;
    font-size: 16px;
}}

QFrame#formCard {{
    background-color: white;
    border-radius: 10px;
    padding: 25px;
}}

QLabel#fieldLabel {{
    color: {COLORS['text_primary']};
    font-weight: bold;
    font-size: 14px;
}}

QLabel#formHeader {{
    color: {COLORS['primary']};
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
}}

QLabel#sectionLabel {{
    color: {COLORS['primary']};
    font-size: 16px;
    font-weight: bold;
    margin-top: 15px;
}}

QPushButton#primaryButton {{
    background-color: {COLORS['primary']};
    padding: 12px;
    font-size: 15px;
    margin-top: 10px;
    width: 100%;
}}

QPushButton#linkButton {{
    background-color: transparent;
    color: {COLORS['primary']};
    border: none;
    text-decoration: underline;
}}

QPushButton#linkButton:hover {{
    color: {COLORS['primary_dark']};
}}

QLineEdit#registerField, QComboBox#registerField {{
    padding: 10px;
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    font-size: 14px;
}}

QLineEdit#registerField:focus, QComboBox#registerField:focus {{
    border: 2px solid {COLORS['primary']};
}}
"""

# Food log specific style
FOOD_LOG_STYLE = f"""
QWidget#foodLogWidget {{
    background-color: {COLORS['background']};
}}

QLabel#nutritionLabel {{
    color: white;
    font-size: 16px;
    font-weight: bold;
}}

QFrame#nutritionCard {{
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
}}

QPushButton#submitButton {{
    background-color: {COLORS['secondary']};
    padding: 12px;
    font-size: 15px;
}}

QPushButton#submitButton:hover {{
    background-color: #05c090;
}}

QLineEdit#searchField {{
    padding: 10px;
    border-radius: 6px;
    font-size: 14px;
}}

QLabel#mealHeader {{
    font-size: 18px;
    font-weight: bold;
    color: white;
}}
"""

# Progress specific style
PROGRESS_STYLE = f"""
QWidget#progressWidget {{
    background-color: {COLORS['background']};
}}

QFrame#chartCard {{
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
}}

QLabel#chartTitle {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS['text_primary']};
}}

QComboBox#chartFilter {{
    min-width: 120px;
    padding: 8px;
    border-radius: 6px;
}}

QLabel#noDataLabel {{
    color: {COLORS['text_secondary']};
    font-style: italic;
    padding: 15px;
}}

QLabel#pageTitle {{
    color: white;
    font-size: 22px;
    font-weight: bold;
    margin: 15px 0;
}}
"""

# Profile specific style
PROFILE_STYLE = f"""
QWidget#profileWidget {{
    background-color: {COLORS['background']};
}}

QLabel#sectionLabel {{
    font-size: 18px;
    font-weight: bold;
    color: white;
    margin-top: 15px;
}}

QPushButton#saveButton {{
    background-color: {COLORS['secondary']};
    padding: 12px;
    font-size: 15px;
    margin-top: 20px;
}}

QPushButton#saveButton:hover {{
    background-color: #05c090;
}}

QFrame#profileSection {{
    background-color: white;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
}}

QLabel#fieldLabel {{
    font-weight: bold;
    margin-bottom: 5px;
}}

QLabel#pageTitle {{
    color: white;
    font-size: 22px;
    font-weight: bold;
    margin: 15px 0;
}}
"""

def get_all_styles():
    """Return all styles combined for use in the application."""
    return MAIN_STYLE + DASHBOARD_STYLE + AUTH_STYLE + FOOD_LOG_STYLE + PROGRESS_STYLE + PROFILE_STYLE 