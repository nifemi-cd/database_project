#!/usr/bin/env python3
"""
F1 Database CLI Application
A command-line interface for querying Formula 1 data.
"""

import sys

# Database connection placeholder
# TODO: Replace with your actual database connection
# import mysql.connector
# or
# import psycopg2

def get_db_connection():
    """
    Establish and return a database connection.
    TODO: Implement your database connection here.
    """
    # Example for MySQL:
    # connection = mysql.connector.connect(
    #     host="localhost",
    #     user="your_username",
    #     password="your_password",
    #     database="f1_database"
    # )
    # return connection
    pass


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_header(title):
    """Print a centered header with separators."""
    print_separator()
    print(f"{title:^80}")
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
    print(f"{'WELCOME TO F1 DB':^80}")
    print_separator()
    print()
    # TODO: Replace with actual ASCII art logo
    print(get_f1_logo())
    print()


def print_menu():
    """Display the main menu options."""
    print_separator()
    print(f"{'MENU OPTIONS':^80}")
    print_separator()
    print()
    print("    D  :  Display Queries")
    print()
    print("    Q  :  Quit Program")
    print()
    print("    H  :  Display Menu Options")
    print()


def print_queries():
    """Display all available queries in a formatted table."""
    queries = get_query_definitions()
    
    print_separator()
    print(f"{'QUERY OPTIONS':^80}")
    print_separator()
    print()
    
    # Table formatting
    print("+-----+------------------------------------------------------------------------+")
    print("| QID | Title                                                                  |")
    print("+-----+------------------------------------------------------------------------+")
    
    for qid, query_info in queries.items():
        title = query_info["title"]
        print(f"| {qid:<3} | {title:<70} |")
        print("+-----+------------------------------------------------------------------------+")
    
    print()
    print('To use any query enter command "use <QID>"')
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
                -- TODO: Add your SQL query here
                -- SELECT driver_name, COUNT(*) as wins
                -- FROM results
                -- WHERE year = %s AND position = 1
                -- GROUP BY driver_name
                -- ORDER BY wins DESC
            """
        },
        2: {
            "title": "Constructors Who Never Won at a Specific Circuit",
            "description": "Find constructors that have participated at a circuit but never achieved a victory there.",
            "parameters": [
                {"name": "circuit", "prompt": "Enter circuit name", "type": str, "validation": None}
            ],
            "query": """
                -- TODO: Add your SQL query here
            """
        },
        3: {
            "title": "Circuits Where Pole Position Won Most Often",
            "description": "Identify circuits where starting from pole position most frequently results in a race win.",
            "parameters": [],
            "query": """
                -- TODO: Add your SQL query here
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
                -- TODO: Add your SQL query here
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
                -- TODO: Add your SQL query here
            """
        },
        8: {
            "title": "List All Circuits by Country and Name",
            "description": "Display all circuits organized by country.",
            "parameters": [],
            "query": """
                -- TODO: Add your SQL query here
            """
        },
        9: {
            "title": "Drivers with Fastest Average Pit Stop Duration",
            "description": "Rank drivers by their average pit stop times.",
            "parameters": [
                {"name": "year", "prompt": "Enter year", "type": int, "validation": lambda x: 1950 <= x <= 2024}
            ],
            "query": """
                -- TODO: Add your SQL query here
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
                -- TODO: Add your SQL query here
            """
        },
        12: {
            "title": "List All Statuses by Status ID",
            "description": "Display all race finish statuses (finished, retired, disqualified, etc.).",
            "parameters": [],
            "query": """
                -- TODO: Add your SQL query here
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
                -- TODO: Add your SQL query here
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
                -- TODO: Add your SQL query here
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
                -- TODO: Add your SQL query here
            """
        },
        16: {
            "title": "Constructor Average Points Per Race and Total Points Per Year",
            "description": "Analyze constructor performance with average and total points statistics.",
            "parameters": [
                {"name": "year", "prompt": "Enter year", "type": int, "validation": lambda x: 1950 <= x <= 2024}
            ],
            "query": """
                -- TODO: Add your SQL query here
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
            
            user_input = input(f"{prompt_text}: ")
            
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
    print(f"You've selected QID {qid}")
    print(f"Title: {query_info['title']}")
    print(f"Description: {query_info['description']}")
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
    print(f"Executing Query ID {qid}: {query_info['title']}")
    print("Results:")
    
    # TODO: Replace this placeholder with actual database execution
    # connection = get_db_connection()
    # cursor = connection.cursor()
    # cursor.execute(query_info["query"], param_values)
    # results = cursor.fetchall()
    
    # Placeholder results display
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


def format_results(headers, rows):
    """
    Format and print query results in a table.
    
    Args:
        headers: List of column headers
        rows: List of tuples containing row data
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
    header_row = "|" + "|".join(f" {h:<{col_widths[i]-1}}" for i, h in enumerate(headers)) + "|"
    print(header_row)
    print(separator)
    
    # Print rows
    for row in rows:
        row_str = "|" + "|".join(f" {str(row[i]) if i < len(row) else '':<{col_widths[i]-1}}" for i in range(len(headers))) + "|"
        print(row_str)
    
    print(separator)
    print(f"*{len(rows)} result(s)*")
    print("*end of results*")
    print()


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
        command = input("f1> ")
        
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