# Fitness Tracker Application

A simple guide to get your Fitness Tracker up and running!

---

## 1. Requirements

You need to have these installed:

- **Python 3.9 or newer**  
  [Download Python](https://www.python.org/downloads/)
- **MySQL Server 8.0 or newer**  
  [Download MySQL](https://dev.mysql.com/downloads/installer/)
- **Git**  
  [Download Git](https://git-scm.com/downloads)

**Check if you have them:**  
Open Command Prompt (Windows) or Terminal (Mac/Linux) and type:
```bash
python --version
git --version
mysql --version
```
If you see version numbers, you're good!

---

## 2. Download the Project

Open your terminal and run:
```bash
git clone https://github.com/ALirezaSadeqii/FitnessTracker.git
cd FitnessTracker
```

---

## 3. Install Python Packages

**Step 1:** Create a virtual environment (recommended)
```bash
python -m venv venv
```
**Step 2:** Activate it  
- On Windows:
  ```bash
  .\venv\Scripts\activate
  ```


**Step 3:** Install all required packages:
```bash
pip install -r requirements.txt
```

---

## 4. Set Up the Database

**Copy and paste this command in your terminal (after installing MySQL):**
```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS fitness_db; CREATE USER IF NOT EXISTS 'fitness_user'@'localhost' IDENTIFIED BY 'Fitness123!'; GRANT ALL PRIVILEGES ON fitness_db.* TO 'fitness_user'@'localhost'; FLUSH PRIVILEGES;"
```

---

## 5. Run the Project

**Step 1: Start the API server**  
Open a terminal and run:
```bash
uvicorn main:app --reload
```
- This starts the backend at http://127.0.0.1:8000

**Step 2: (Optional) Seed the food table**  
If you want to seed the food table with default foods, run:
```bash
python main.py
```

**Step 3: Start the GUI**  
Open a new terminal window (keep the API server running) and run:
```bash
python auth.py
```
- This opens the graphical interface for login and registration.

---

## 6. Troubleshooting

- **Missing packages?**  
  Run: `pip install -r requirements.txt`
- **MySQL connection errors?**  
  Make sure MySQL is running and the username/password matches what's in the code.

---

## 7. Project Structure

- `main.py` - FastAPI API server
- `auth.py` - PyQt5 login/registration GUI
- `edit_profile.py`, `food_log.py`, `progress.py` - GUI modules
- `models/`, `schemas.py`, `database.py`, `db_operations.py` - Backend logic

---

**You're ready to go!**  
If you have any issues, check the Troubleshooting section above. 