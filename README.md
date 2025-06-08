# Fitness Tracker Application

A comprehensive fitness and nutrition tracking application built with FastAPI and PyQt5. This application allows users to register, track their food intake, monitor weight progress, and manage their fitness goals.

## Features

- User registration and authentication
- Food logging with nutritional information
- Weight and BMI tracking
- Progress visualization
- Profile management
- Interactive GUI interface
- RESTful API endpoints

## System Requirements

- Python 3.9+
- MySQL Server 8.0+
- Git (for cloning the repository)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/fitness8.git
cd fitness8
```

### 2. Create and activate a virtual environment (recommended)

#### On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install MySQL

#### On macOS:
```bash
brew install mysql
brew services start mysql
```

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

#### On Windows:
Download and install MySQL from the [official website](https://dev.mysql.com/downloads/installer/).

### 4. Setup MySQL Database

```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS fitness_db; CREATE USER IF NOT EXISTS 'fitness_user'@'localhost' IDENTIFIED BY 'Fitness123!'; GRANT ALL PRIVILEGES ON fitness_db.* TO 'fitness_user'@'localhost'; FLUSH PRIVILEGES;"
```

### 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### 1. Start the API Server

Open a new terminal window and run:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This will start the API server at http://127.0.0.1:8000. You can access the API documentation at http://127.0.0.1:8000/docs.

### 2. Start the GUI Application

In a separate terminal window, run:
```bash
python auth.py
```

This will launch the PyQt5-based graphical user interface for the application.

## Configuration

The application uses the following default configuration:
- Database: MySQL
- Database Name: fitness_db
- Database User: fitness_user
- Database Password: Fitness123!
- API Server: http://127.0.0.1:8000

To modify these settings, you can update the database connection parameters in `models/base.py`.

## API Endpoints

- `/register` - Register a new user
- `/login` - Authenticate a user and get access token
- `/users/{user_id}` - Get user information
- `/foods` - List all available foods
- `/foodlogs` - Create a new food log entry
- `/progress/{user_id}` - Get a user's progress records
- `/progress` - Create a new progress record
- `/seed-foods` - Seed the food database with default food items

## Development

### Project Structure

- `main.py` - FastAPI application and API endpoints
- `database.py` - Database connection and utility functions
- `db_operations.py` - Database operations and food seeding
- `models/` - SQLAlchemy models
- `schemas.py` - Pydantic schemas for request/response validation
- `auth.py` - PyQt5 login/registration GUI
- `edit_profile.py` - Profile editing GUI
- `food_log.py` - Food logging GUI
- `progress.py` - Progress tracking GUI

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Make sure MySQL is running
   - Check that the database credentials in `models/base.py` are correct
   - Verify MySQL service is running: `sudo systemctl status mysql` (Linux) or `brew services list` (macOS)

2. **Missing Dependencies**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - If you encounter PyQt5 issues, try: `pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip` and then `pip install PyQt5`

3. **GUI Not Launching**:
   - Verify PyQt5 is installed correctly
   - On Linux, you might need additional packages: `sudo apt-get install python3-pyqt5`
   - Make sure you're running the application from the correct directory

4. **Port Already in Use**:
   - If port 8000 is already in use, you can specify a different port:
     ```bash
     uvicorn main:app --reload --port 8001
     ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[MIT License](LICENSE) 