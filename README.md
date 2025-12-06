# Comp 3380 database project
Group project for our database.

## Setup

1. **Create virtual environment (if not already created):**
   ```bash
   python3 -m venv venv
   ```
2. **Configure database connection:**
   - Open `python_interface.py`
   - Update connection parameters in `get_db_connection()` (lines 22-25):
     - `server`: uranium.cs.umanitoba.ca
     - `database`: cs3380
     - `user`: taiwoa5
     - `password`: 7980132

3. **Install dependencies and run application:**
   ```bash
   ./run.sh
   ```
