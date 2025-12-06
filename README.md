# Comp 3380 database project
Group project for our database.

## Setup

1. **Create virtual environment (if not already created):**
   ```bash
   python3 -m venv venv
   ```

2. **Install dependencies:**
   ```bash
   ./run.sh
   ```

3. **Configure database connection:**
   - Open `python_interface.py`
   - Update connection parameters in `get_db_connection()` (lines 22-25):
     - `server`: Your SQL Server name/IP
     - `database`: Your database name
     - `user`: Your SQL Server username
     - `password`: Your SQL Server password

4. **Run the application:**
   ```bash
   ./run.sh
   ```
   
   Or manually:
   ```bash
   source venv/bin/activate
   python python_interface.py
   ```
