#!/usr/bin/env python3
"""
F1 Database CLI Application
A command-line interface for querying Formula 1 data.
"""

import sys
import os
import re
import pymssql

def get_db_connection():
    """
    Establish and return a database connection to MSSQL Server.
    
    Returns:
        pymssql.Connection: Database connection object
    
    Note: Update the connection parameters below with your actual database credentials.
    """
    try:
        # MSSQL Server connection parameters
        # Update these with your actual database credentials
        server = "uranium.cs.umanitoba.ca"  # or your server name/IP address
        database = "cs3380"  # or your database name
        user = "taiwoa5"  # or your username
        password = "7980132"  # your password
        
        connection = pymssql.connect(
            server=server,
            database=database,
            user=user,
            password=password
        )
        return connection
    
    except pymssql.Error as e:
        print(f"Error connecting to database: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure SQL Server is running")
        print("2. Verify your server name, database name, username, and password")
        print("3. Check if SQL Server allows remote connections")
        raise


def print_separator(char="\033[34m=", length=80):
    """Print a separator line."""
    print(char * length)


def get_seed_directory():
    """Get the path to the seed directory."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "seed")


def convert_sqlite_to_mssql(sql_content):
    """
    Convert SQLite SQL syntax to MSSQL syntax.
    
    Args:
        sql_content: SQL content in SQLite format
    
    Returns:
        SQL content converted to MSSQL format
    """
    # Remove BEGIN TRANSACTION; and COMMIT; statements
    sql_content = re.sub(r'BEGIN TRANSACTION;?\s*', '', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'COMMIT;?\s*', '', sql_content, flags=re.IGNORECASE)
    
    # Replace double quotes with square brackets for identifiers
    # This regex finds "identifier" and replaces with [identifier]
    sql_content = re.sub(r'"([^"]+)"', r'[\1]', sql_content)
    
    return sql_content


def print_progress_bar(current, total, bar_length=40, prefix="Progress"):
    """
    Print a progress bar to the console.
    
    Args:
        current: Current progress count
        total: Total count
        bar_length: Length of the progress bar
        prefix: Prefix text for the progress bar
    """
    if total == 0:
        percent = 100
    else:
        percent = (current / total) * 100
    
    filled_length = int(bar_length * current // max(total, 1))
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    sys.stdout.write(f'\r{prefix}: |\033[32m{bar}\033[34m| \033[33m{percent:.1f}%\033[34m ({current}/{total})')
    sys.stdout.flush()
    
    if current >= total:
        print()  # New line when complete


def get_table_deletion_order():
    """
    Return the order in which tables should be deleted (dependent tables first).
    This respects foreign key constraints.
    """
    return [
        "lap",
        "pit_stops",
        "qualifying",
        "result",
        "constructor_results",
        "constructor_standings",
        "driver_standings",
        "race",
        "circuits",
        "constructors",
        "drivers",
        "status"
    ]


def get_seed_file_order():
    """
    Return the order in which seed files should be executed (parent tables first).
    This respects foreign key constraints.
    """
    return [
        "status.sql",
        "drivers.sql",
        "constructors.sql",
        "circuits.sql",
        "race.sql",
        "driver_standings.sql",
        "constructor_standings.sql",
        "constructor_results.sql",
        "result.sql",
        "qualifying.sql",
        "pit_stops.sql",
        "lap.sql"
    ]


def delete_all_data(connection):
    """
    Delete all data from all tables in the correct order.
    
    Args:
        connection: Database connection object
    
    Returns:
        bool: True if successful, False otherwise
    """
    print()
    print_header("DELETING ALL DATA")
    print()
    
    tables = get_table_deletion_order()
    cursor = connection.cursor()
    
    total_tables = len(tables)
    deleted_count = 0
    
    for i, table in enumerate(tables):
        try:
            # Try to delete from the table
            cursor.execute(f"DELETE FROM [{table}]")
            connection.commit()
            deleted_count += 1
            print_progress_bar(i + 1, total_tables, prefix=f"Deleting tables")
        except Exception as e:
            # Table might not exist, continue
            print_progress_bar(i + 1, total_tables, prefix=f"Deleting tables")
            continue
    
    print()
    print(f"✓ Deleted data from {deleted_count} tables")
    cursor.close()
    return True


def count_statements_in_file(file_path):
    """
    Count the number of INSERT statements in a SQL file.
    
    Args:
        file_path: Path to the SQL file
    
    Returns:
        int: Number of INSERT statements
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content.upper().count('INSERT INTO')
    except:
        return 0


def seed_from_file(connection, file_path, file_name):
    """
    Execute all SQL statements from a seed file in one query.
    
    Args:
        connection: Database connection object
        file_path: Path to the SQL file
        file_name: Name of the file (for display)
    
    Returns:
        tuple: (success_count, error_count)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 0, 1
    
    # Convert SQLite syntax to MSSQL
    content = convert_sqlite_to_mssql(content)
    
    # Split into individual statements
    statements = [s.strip() for s in content.split(';') if s.strip()]
    
    # Filter to only INSERT statements
    insert_statements = [s for s in statements if s.upper().startswith('INSERT')]
    
    if not insert_statements:
        return 0, 0
    
    cursor = connection.cursor()
    total = len(insert_statements)
    
    # Join ALL statements and execute in one query
    full_query = ';\n'.join(insert_statements)
    
    try:
        cursor.execute(full_query)
        connection.commit()
        cursor.close()
        return total, 0
    except Exception as e:
        # If full execution fails, return as error
        cursor.close()
        return 0, total


def seed_database(connection):
    """
    Seed the database with data from all seed files.
    Shows a single progress bar for all files.
    
    Args:
        connection: Database connection object
    
    Returns:
        bool: True if successful, False otherwise
    """
    print()
    print_header("\033[33mSEEDING DATABASE\033[34m")
    print()
    
    seed_dir = get_seed_directory()
    
    if not os.path.exists(seed_dir):
        print(f"\033[38;5;196m✗ Seed directory not found: {seed_dir}\033[34m")
        return False
    
    seed_files = get_seed_file_order()
    
    # Check which files exist
    existing_files = []
    for file_name in seed_files:
        file_path = os.path.join(seed_dir, file_name)
        if os.path.exists(file_path):
            existing_files.append((file_name, file_path))
    
    if not existing_files:
        print("✗ No seed files found")
        return False
    
    total_files = len(existing_files)
    print(f"Found {total_files} seed files to process")
    print()
    
    total_success = 0
    total_errors = 0
    failed_files = []
    
    for i, (file_name, file_path) in enumerate(existing_files):
        # Update progress bar with current file name
        print_progress_bar(i, total_files, prefix=f"\033[33mSeeding\033[34m ({file_name})")
        
        success, errors = seed_from_file(connection, file_path, file_name)
        total_success += success
        total_errors += errors
        
        if errors > 0:
            failed_files.append(file_name)
    
    # Final progress bar update
    print_progress_bar(total_files, total_files, prefix="Seeding (complete)      ")
    
    print()
    print_separator("-")
    print(f"\033[33mSEEDING COMPLETE:\033[34m {total_success} total records inserted")
    if total_errors > 0:
        print(f"                  {total_errors} total errors")
        print(f"  \033[33mFailed files:\033[34m {', '.join(failed_files)}")
    print()
    
    return True


def clear_database_menu():
    """
    Menu option to delete all data from all tables.
    Shows progress for the operation.
    """
    print()
    print_header("CLEAR DATABASE")
    print()
    
    print("⚠️  \033[38;5;196mWARNING:\033[34m This will delete ALL data from the database.")
    print("   This operation cannot be undone!")
    print()
    
    confirm = input("\033[33mAre you sure you want to continue? (yes/no):\033[34m ").strip().lower()
    
    if confirm != "yes":
        print()
        print("Operation cancelled.")
        return
    
    try:
        print()
        print("Connecting to database...")
        connection = get_db_connection()
        print("✓ Connected successfully")
        
        # Delete all data
        if not delete_all_data(connection):
            print("✗ Failed to delete data")
            connection.close()
            return
        
        connection.close()
        
        print_separator()
        print(f"{'DATABASE CLEARED SUCCESSFULLY':^80}")
        print_separator()
        print()
        
    except Exception as e:
        print(f"✗ Error during database clear: {e}")
        print()
        print("Troubleshooting tips:")
        print("1. Make sure the database connection is configured correctly")
        print("2. Check if you have sufficient permissions")


def seed_database_menu():
    """
    Menu option to seed the database from seed files.
    Shows progress for each file.
    """
    print()
    print_header("SEED DATABASE")
    print()
    
    print("\033[33mThis will load data from the seed files into the database.")
    print("Note:\033[34m Existing data will NOT be deleted. Use 'C' first to clear if needed.")
    print()
    
    confirm = input("\033[33mDo you want to continue? (yes/no):\033[34m ").strip().lower()
    
    if confirm != "yes":
        print()
        print("Operation cancelled.")
        return
    
    try:
        print()
        print("Connecting to database...")
        connection = get_db_connection()
        print("\033[32m✓ Connected successfully\033[34m")
        
        # Seed database
        if not seed_database(connection):
            print("✗ Failed to seed database")
            connection.close()
            return
        
        connection.close()
        
        print_separator()
        print(f"{'\033[33mDATABASE SEEDED SUCCESSFULLY\033[34m':^80}")
        print_separator()
        print()
        
    except Exception as e:
        print(f"\033[38;5;196m✗ Error during database seeding:\033[34m {e}")
        print()
        print("\033[33mTroubleshooting tips:\033[34m")
        print("\033[33m1.\033[34m Make sure the database connection is configured correctly")
        print("\033[33m2.\033[34m Check if you have sufficient permissions")
        print("\033[33m3.\033[34m Ensure the seed files are in the correct format")


def print_header(title):
    """Print a centered header with separators."""
    print_separator()
    print(f"\033[33m{title:^80}\033[34m")
    print_separator()

def get_f1_logo():
    """Return a stylized F1 racing logo."""
    logo = r"""
                                      _____ __
                                     / ___// /
                                    / /_/ / /
                                   / __/ / /
                                  /_/   /_/
    """

    return logo


def print_welcome():
    """Display the welcome screen."""
    print_separator()
    print(f"\033[33m{'WELCOME TO F1 DB':^80}\033[34m")
    print_separator()
    print()
    # TODO: Replace with actual ASCII art logo
    print(f"\033[38;5;196m{get_f1_logo()}\033[0m")
    print()


def print_menu():
    """Display the main menu options."""
    print_separator()
    print(f"\033[33m{'MENU OPTIONS':^80}\033[34m")
    print_separator()
    print()
    print("    \033[33mD\033[34m  :  Display Queries")
    print()
    print("    \033[33mC\033[34m  :  Clear Database (Delete all data)")
    print()
    print("    \033[33mS\033[34m  :  Seed Database (Load data from seed files)")
    print()
    print("    \033[33mQ\033[34m  :  Quit Program")
    print()
    print("    \033[33mH\033[34m  :  Display Menu Options")
    print()


def print_queries():
    """Display all available queries in a formatted table."""
    queries = get_query_definitions()
    
    print_separator()
    print(f"{'QUERY OPTIONS':^80}")
    print_separator()
    print()
    
    # Table formatting
    print("\033[34m+-----+------------------------------------------------------------------------+")
    print("| \033[33mQID\033[34m| \033[33mTitle\033[34m                                                                  |")
    print("+-----+------------------------------------------------------------------------+")
    
    for qid, query_info in queries.items():
        title = query_info["title"]
        print(f"|\033[33m {qid:<3} \033[0m\033[34m| {title:<70} |")
        print("+-----+------------------------------------------------------------------------+")
    
    print()
    print('To use any query enter command "\033[33muse <QID>\033[34m"')
    print()


def get_query_definitions():
    """
    Return a dictionary of all query definitions.
    Each query has: title, description, parameters, and the SQL query.
    """
    return {
        1: {
            "title": "Drivers with Most Wins in a Specific Year",
            "description": """This query allows an analyst to determine the all time best drivers/constructors in the franchise.
            By observing the winning tendencies of drivers, analysts can discover which driver is the most talented, compare driver performances throughout
            seasons and observe the impact of a team or car change on driver success.""",
            "parameters": [
                {"name": "year", "prompt": "Enter year", "type": int, "validation": lambda x: 1950 <= x <= 2024}
            ],
            "query": """
                WITH yearly_wins AS (
                    SELECT d.forename, d.surname AS driver, COUNT(*) AS wins
                    FROM result r 
                    JOIN drivers d ON r.driverId = d.driverId
                    JOIN race ra ON r.raceId = ra.raceId
                    WHERE ra.year = %s AND r.positionOrder = 1
                    GROUP BY r.driverId, d.forename, d.surname
                )
                SELECT top 5 *
                FROM yearly_wins 
                ORDER BY wins DESC;
            """
        },
        2: {
            "title": "Constructors Who Never Won at a Specific Circuit",
            "description": "Find constructors that have participated at a circuit but never achieved a victory there.",
            "parameters": [
                {"name": "circuitId", "prompt": "Enter circuit Id", "type": int, "validation": lambda x: x > 0 and x <= 77}
            ],
            "query": """
                WITH winners AS (
                    SELECT DISTINCT r.constructorId 
                    FROM result r 
                    JOIN race ra ON r.raceId = ra.raceId 
                    WHERE ra.circuitId = %s AND r.positionOrder = 1
                )
                SELECT c.name 
                FROM constructors c 
                WHERE c.constructorId NOT IN (SELECT constructorId FROM winners);
            """
        },
        3: {
            "title": "Circuits Where Pole Position Won Most Often",
            "description": "Identify circuits where starting from pole position most frequently results in a race win.",
            "parameters": [],
            "query": """
                WITH pole_wins AS (
                    SELECT ra.circuitId, COUNT(*) AS pole_win_count FROM result r
                    JOIN race ra ON r.raceId = ra.raceId 
                    WHERE r.grid = 1 AND r.positionOrder = 1 
                    GROUP BY ra.circuitId
                )
                SELECT c.name, c.country, pw.pole_win_count FROM pole_wins pw 
                JOIN circuits c ON pw.circuitId = c.circuitId 
                ORDER BY pw.pole_win_count DESC;
            """
        },
        4: {
            "title": "Drivers Who Improved Position Most from Grid to Finish",
            "description": "Find drivers who consistently gain the most positions during races.",
            "parameters": [
                {"name": "year", "prompt": "Enter year", "type": int, "validation": lambda x: 1950 <= x <= 2024}
            ],
            "query": """
                -- TODO: Add your SQL query here
            """
        },
        5: {
            "title": "Circuits with the Most Accidents",
            "description": "List circuits ordered by the number of accidents/retirements due to crashes.",
            "parameters": [],
            "query": """
                WITH accident_races AS (
                    SELECT r.raceId, COUNT(*) AS accidents 
                    FROM result r
                    JOIN status s ON r.statusId = s.statusId
                    WHERE s.status LIKE '%ccident%' OR s.status LIKE '%ollision%' OR s.status LIKE '%pin%'
                    GROUP BY r.raceId
                )
                SELECT TOP 15 ra.name, ra.year, c.name AS circuit, ar.accidents 
                FROM accident_races ar 
                JOIN race ra ON ar.raceId = ra.raceId 
                JOIN circuits c ON ra.circuitId = c.circuitId 
                ORDER BY ar.accidents DESC;
            """
        },
        6: {
            "title": "Drivers Who Consistently Finish in Points",
            "description": "Find drivers with the highest percentage of points finishes.",
            "parameters": [
                {"name": "min_races", "prompt": "Enter minimum number of races", "type": int, "validation": lambda x: x > 0}
            ],
            "query": """
                -- TODO: Add your SQL query here
            """
        },
        7: {
            "title": "List All Constructors by Name",
            "description": "Display all constructors in alphabetical order.",
            "parameters": [],
            "query": """
                SELECT name, nationality FROM constructors ORDER BY name;
            """
        },
        8: {
            "title": "List All Circuits by Country and Name",
            "description": "Display all circuits organized by country.",
            "parameters": [],
            "query": """
                SELECT name, country, location FROM circuits ORDER BY country, name;
            """
        },
        9: {
            "title": "Drivers with Fastest Average Pit Stop Duration",
            "description": "Rank drivers by their average pit stop times.",
            "parameters": [
                # {"name": "year", "prompt": "Enter year", "type": int, "validation": lambda x: 1950 <= x <= 2024}
            ],
            "query": """
                WITH pit_stats AS (
                    SELECT 
                        p.driverId, 
                        AVG(CAST(p.duration AS FLOAT)) AS avg_duration, 
                        COUNT(*) AS stops
                    FROM pit_stops p
                    GROUP BY p.driverId
                )
                SELECT TOP 10
                    d.forename, 
                    d.surname AS driver, 
                    ROUND(ps.avg_duration, 3) AS avg_seconds, 
                    ps.stops
                FROM pit_stats ps
                JOIN drivers d ON ps.driverId = d.driverId
                ORDER BY ps.avg_duration;
            """
        },
        10: {
            "title": "History of Constructor Performance on a Specific Circuit",
            "description": "Show how a constructor has performed at a particular circuit over the years.",
            "parameters": [
                {"name": "constructor", "prompt": "Enter constructor name", "type": str, "validation": None},
                {"name": "circuit", "prompt": "Enter circuit name", "type": str, "validation": None}
            ],
            "query": """
                -- TODO: Add your SQL query here
            """
        },
        11: {
            "title": "Highest Scoring Nationalities by Average Points Per Driver",
            "description": "Rank nationalities by the average points their drivers score.",
            "parameters": [],
            "query": """
                WITH nationality_stats AS (
                    SELECT d.nationality, 
                        COUNT(DISTINCT d.driverId) AS driver_count,
                        SUM(CASE WHEN r.positionOrder = 1 THEN 1 ELSE 0 END) AS total_wins,
                        SUM(r.points) AS total_points 
                    FROM drivers d
                    JOIN result r ON d.driverId = r.driverId
                    GROUP BY d.nationality
                )
                SELECT TOP 15 nationality, driver_count, total_wins, total_points, 
                    ROUND(total_points * 1.0 / driver_count, 1) AS avg_points_per_driver
                FROM nationality_stats 
                ORDER BY avg_points_per_driver DESC;
            """
        },
        12: {
            "title": "List All Statuses by Status ID",
            "description": "Display all race finish statuses (finished, retired, disqualified, etc.).",
            "parameters": [],
            "query": """
               SELECT statusID, status FROM status ORDER BY statusID;
            """
        },
        13: {
            "title": "Get Driver Standings from a Specific Race",
            "description": "Show the championship standings after a specific race.",
            "parameters": [
                {"name": "year", "prompt": "Enter year", "type": int, "validation": lambda x: 1950 <= x <= 2024},
                {"name": "round", "prompt": "Enter round number", "type": int, "validation": lambda x: x > 0}
            ],
            "query": """
                SELECT d.forename, d.surname AS driver, ds.position, 
                    ds.points AS race_points, ds.wins, ra.name AS race_name, ra.year
                FROM driver_standings ds
                JOIN drivers d ON ds.driverId = d.driverId
                JOIN race ra ON ds.raceId = ra.raceId
                WHERE ra.year = %s AND ra.round = %s
                ORDER BY ds.position;
            """
        },
        14: {
            "title": "Get Constructor Standings from a Specific Race",
            "description": "Show the constructor championship standings after a specific race.",
            "parameters": [
                {"name": "year", "prompt": "Enter year", "type": int, "validation": lambda x: 1950 <= x <= 2024},
                {"name": "round", "prompt": "Enter round number", "type": int, "validation": lambda x: x > 0}
            ],
            "query": """
                SELECT c.name AS constructor, cs.position, cs.points AS race_points, 
                    cs.wins, ra.name AS race_name, ra.year 
                FROM constructor_standings cs
                JOIN constructors c ON cs.constructorId = c.constructorId
                JOIN race ra ON cs.raceId = ra.raceId
                WHERE ra.year = %s AND ra.round = %s
                ORDER BY cs.position;
            """
        },
        15: {
            "title": "Obtain Qualifying Results of a Specific Race",
            "description": "Display qualifying session results for a particular race.",
            "parameters": [
                {"name": "year", "prompt": "Enter year", "type": int, "validation": lambda x: 1950 <= x <= 2024},
                {"name": "round", "prompt": "Enter round number", "type": int, "validation": lambda x: x > 0}
            ],
            "query": """
                SELECT d.forename, d.surname AS driver, r.raceId, c.name AS constructor, 
                    q.position AS qualifying_position, q.q1, q.q2, q.q3, 
                    r.name AS race_name, r.year
                FROM qualifying q
                JOIN drivers d ON q.driverId = d.driverId
                JOIN constructors c ON q.constructorId = c.constructorId
                JOIN race r ON q.raceId = r.raceId
                WHERE r.year = %s AND r.round = %s
                ORDER BY q.position;
            """
        },
        16: {
            "title": "Constructor Average Points Per Race and Total Points Per Year",
            "description": "Analyze constructor performance with average and total points statistics.",
            "parameters": [
                {"name": "year", "prompt": "Enter year", "type": int, "validation": lambda x: 1950 <= x <= 2024}
            ],
            "query": """
                SELECT TOP 10 
                    c.name AS constructor, 
                    COUNT(cr.raceId) AS races_entered, 
                    SUM(cr.points) AS total_points, 
                    ROUND(AVG(CAST(cr.points AS FLOAT)), 2) AS avg_points_per_race, 
                    MAX(cr.points) AS max_points_in_a_race, 
                    MIN(cr.points) AS min_points_in_a_race
                FROM constructor_results cr
                JOIN constructors c ON cr.constructorId = c.constructorId
                JOIN race r ON cr.raceId = r.raceId
                WHERE r.year = %s
                GROUP BY c.name
                ORDER BY avg_points_per_race DESC;
            """
        }
    }


def get_parameter_input(param):
    """
    Prompt user for a parameter value with validation.
    Returns the validated input value.
    """
    while True:
        try:
            prompt_text = param["prompt"]
            if param["type"] == int and param.get("validation"):
                # Add hint about valid range for year parameters
                if "year" in param["name"].lower():
                    prompt_text += " (Year should be between 1950 - 2024)"
            
            user_input = input(f"\033[33m{prompt_text}: \033[34m")
            
            # Convert to appropriate type
            if param["type"] == int:
                value = int(user_input)
            elif param["type"] == float:
                value = float(user_input)
            else:
                value = user_input
            
            # Validate if validation function exists
            if param.get("validation") and not param["validation"](value):
                if "year" in param["name"].lower():
                    print("You've entered an invalid year. Year should be between 1950 - 2024")
                else:
                    print("Invalid input. Please try again.")
                continue
            
            print(f"You have entered {param['name']}: {value}")
            return value
            
        except ValueError:
            print(f"Invalid input. Please enter a valid {param['type'].__name__}.")


def execute_query(qid):
    """
    Execute a query by its ID.
    Prompts for required parameters and displays results.
    """
    queries = get_query_definitions()
    
    if qid not in queries:
        print("Invalid QID. Please enter a valid QID from the list.")
        return
    
    query_info = queries[qid]
    
    print()
    print(f"\033[33mYou've selected QID {qid}")
    print(f"Title:\033[34m {query_info['title']}")
    print(f"\033[33mDescription:\033[34m {query_info['description']}")
    print()
    
    # Collect parameters
    param_values = []
    for param in query_info["parameters"]:
        hint = " ---------> And other options that will be prompted(depending on number of inputs needed for query)"
        if len(query_info["parameters"]) > 1 and param == query_info["parameters"][0]:
            print(f"{param['prompt']}: <value>{hint}")
        value = get_parameter_input(param)
        param_values.append(value)
        print()
    
    # Execute the query
    print(f"\033[33mExecuting Query ID {qid}:\033[34m {query_info['title']}")
    print("\033[33mResults:\033[34m")
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get the SQL query
        sql_query = query_info["query"].strip()
        
        # Skip if query is a placeholder (contains TODO or is empty)
        if not sql_query or "-- TODO" in sql_query or sql_query.startswith("--"):
            print("Query not yet implemented. Please add the SQL query to the query definition.")
            print_results_placeholder(qid, param_values)
            cursor.close()
            connection.close()
            return
        
        # Execute query with parameters
        # pymssql uses %s as placeholders (like MySQL)
        if param_values:
            cursor.execute(sql_query, param_values)
        else:
            cursor.execute(sql_query)
        
        # Fetch results
        results = cursor.fetchall()
        
        # Get column names
        columns = [column[0] for column in cursor.description] if cursor.description else []
        
        # Format and display results with pagination
        if columns:
            display_paginated_results(columns, results, page_size=10)
        else:
            print("Query executed successfully.")
            if results:
                print(f"Affected rows: {len(results)}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error executing query: {e}")
        print("Displaying placeholder results instead.")
        print_results_placeholder(qid, param_values)


def print_results_placeholder(qid, params):
    """
    Print placeholder results.
    TODO: Replace with actual result formatting based on query.
    """
    # Example table output format
    print("+------------------------+------------------+")
    print("| Driver Name            | Number of Wins   |")
    print("+------------------------+------------------+")
    print("| Lewis Hamilton         | 11               |")
    print("+------------------------+------------------+")
    print("*more results*")
    print("*end of results*")
    print()


def format_results(headers, rows, show_count=True):
    """
    Format and print query results in a table.
    
    Args:
        headers: List of column headers
        rows: List of tuples containing row data
        show_count: Whether to show result count at the end
    """
    if not rows:
        print("No results found.")
        return
    
    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(str(header))
        for row in rows:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width + 2)
    
    # Print header separator
    separator = "+" + "+".join("-" * w for w in col_widths) + "+"
    print(separator)
    
    # Print headers
    header_row = "|" + "|".join(f"\033[33m {h:<{col_widths[i]-1}}\033[34m" for i, h in enumerate(headers)) + "|"
    print(header_row)
    print(separator)
    
    # Print rows
    for row in rows:
        row_str = "|" + "|".join(f"\033[32m {str(row[i]) if i < len(row) else '':<{col_widths[i]-1}}\033[34m" for i in range(len(headers))) + "|"
        print(row_str)
    
    print(separator)
    if show_count:
        print(f"*{len(rows)} result(s)*")
        print("\033[33m*end of results*\033[34m")
        print()


def display_paginated_results(headers, rows, page_size=10):
    """
    Display results with pagination support.
    
    Args:
        headers: List of column headers
        rows: List of tuples containing row data
        page_size: Number of rows per page (default: 10)
    """
    if not rows:
        print("No results found.")
        return
    
    total_rows = len(rows)
    
    # If results fit on one page, just display them normally
    if total_rows <= page_size:
        format_results(headers, rows)
        return
    
    total_pages = (total_rows + page_size - 1) // page_size  # ceiling division
    current_page = 0
    
    while True:
        # Calculate slice for current page
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, total_rows)
        page_rows = rows[start_idx:end_idx]
        
        # Display current page
        print()
        format_results(headers, page_rows, show_count=False)
        
        # Show pagination info
        print(f"\033[33mPage {current_page + 1} of {total_pages}\033[34m (showing {start_idx + 1}-{end_idx} of {total_rows} results)")
        print()
        
        # Build navigation options
        options = []
        if current_page > 0:
            options.append("\033[33mP\033[34m - Previous page")
        if current_page < total_pages - 1:
            options.append("\033[33mN\033[34m - Next page")
        options.append("\033[33mQ\033[34m - Quit pagination")
        
        print(" | ".join(options))
        choice = input("\033[33mEnter choice:\033[34m ").strip().upper()
        
        if choice == 'N' and current_page < total_pages - 1:
            current_page += 1
        elif choice == 'P' and current_page > 0:
            current_page -= 1
        elif choice == 'Q':
            print()
            print(f"*{total_rows} total result(s)*")
            print("\033[33m*end of results*\033[34m")
            print()
            break
        else:
            print("\033[33mInvalid choice. Please try again.\033[34m")


def parse_command(command):
    """
    Parse user command and return action and arguments.
    """
    command = command.strip()
    
    if not command:
        return None, None
    
    parts = command.split(maxsplit=1)
    action = parts[0].upper()
    args = parts[1] if len(parts) > 1 else None
    
    return action, args


def main():
    """Main application loop."""
    print_welcome()
    print_menu()
    
    while True:
        print_separator()
        command = input("\033[33mf1> \033[34m")
        
        action, args = parse_command(command)
        
        if action is None:
            continue
        
        if action == "D":
            print_queries()
        
        elif action == "Q":
            print()
            print("Exiting F1 DB. Goodbye!")
            print_separator()
            print(f"{'EXITING F1 DB':^80}")
            print_separator()
            sys.exit(0)
        
        elif action == "H":
            print_menu()
        
        elif action == "C":
            clear_database_menu()
        
        elif action == "S":
            seed_database_menu()
        
        elif action == "USE":
            if args is None:
                print("Please specify a QID. Usage: use <QID>")
                continue
            try:
                qid = int(args)
                execute_query(qid)
            except ValueError:
                print("Invalid QID. Please enter a number.")
        
        else:
            print(f"Unknown command: {command}")
            print("Enter 'H' to see available commands.")


if __name__ == "__main__":
    main()