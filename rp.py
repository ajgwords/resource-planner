#!/usr/bin/env python3
import argparse
import yaml
from datetime import datetime, timedelta

def validate_priorities(projects):
    """
    Validate that the priorities in the project list are sequential integers starting at 1.

    Parameters:
    - projects (list): List of project dictionaries.

    Returns:
    - bool: True if priorities are valid, raises ValueError otherwise.
    """
    priorities = sorted([project.get("priority", 0) for project in projects])
    expected_priorities = list(range(1, len(projects) + 1))
    if priorities != expected_priorities:
        raise ValueError(
            f"Invalid priorities: {priorities}. "
            f"Priorities must be incremental integers starting at 1, up to {len(projects)}."
        )
    return True

def calculate_working_days(start_date, end_date, required_days, holidays=None, settings=None):
    """
    Calculate working days between start_date and end_date and check against required_days.
    Optionally spread working days evenly across the range if specified in settings.

    Parameters:
    - start_date (str): Project start date in "YYYY-MM-DD".
    - end_date (str): Project end date in "YYYY-MM-DD".
    - required_days (int): Number of working days required for the project.
    - holidays (list): List of public holidays in "YYYY-MM-DD" format. Default is None.
    - settings (dict): Settings for working days and hours.

    Returns:
    - available_days (int): Total working days available.
    - is_sufficient (bool): Whether the available days meet the required days.
    - working_days (list): List of working days available within the range.
    """

    # Parse dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    holidays2 = set(datetime.strptime(h, "%Y-%m-%d") for h in holidays) if holidays else set()

    # Default settings
    working_days_per_week = settings.get('working_days_per_week', 5)
    spread_days_evenly = settings.get('spread_days_evenly', False)

    # Initialize counters and list
    working_days = []

    # Determine valid working weekdays
    allowed_weekdays = list(range(5))[:working_days_per_week]  # E.g., [0, 1, 2, 3, 4] for 5 days/week

    # Collect all possible working days
    current = start
    while current <= end:
        if current.weekday() in allowed_weekdays and current not in holidays2:  # Weekdays and not a holiday
            working_days.append(current)
        current += timedelta(days=1)

    # Spread working days evenly if the option is enabled
    if spread_days_evenly and len(working_days) > required_days:
        interval = len(working_days) / required_days
        working_days = [working_days[int(round(i * interval))] for i in range(required_days)]

    # Determine if there are enough days
    is_sufficient = len(working_days) >= required_days

    return len(working_days), is_sufficient, working_days


def assign_project_dates(yaml_file):
    """
    Assign project names to working days within their date ranges, using priorities.

    Parameters:
    - yaml_file (str): Path to the YAML file.

    Returns:
    - assignment (dict): Mapping of dates to assigned project names.
    - unassigned_projects (list): Projects that could not be fully assigned due to conflicts.
    """
    # Load YAML data
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    projects = data.get('projects', [])
    holidays = data.get('holidays', [])
    settings = data.get('settings', {})

    # Validate project priorities
    validate_priorities(projects)

    # Sort projects by priority
    projects = sorted(projects, key=lambda p: p['priority'])

    assigned_dates = {}  # Track which dates are assigned to which projects
    unassigned_projects = []

    for project in projects:
        name = project['name']
        start_date = project['start_date']
        end_date = project['end_date']
        required_days = project['required_days']

        # Calculate working days for this project
        available_days, is_sufficient, working_days = calculate_working_days(
            start_date, end_date, required_days, holidays, settings
        )

        # Attempt to assign dates to this project
        assigned_count = 0
        for day in working_days:
            if assigned_count >= required_days:
                break
            if day not in assigned_dates:  # Only assign if the date is free
                assigned_dates[day] = name
                assigned_count += 1

        # Check if all required days were assigned
        if assigned_count < required_days:
            unassigned_projects.append({
                "name": name,
                "assigned_days": assigned_count,
                "required_days": required_days
            })

    return assigned_dates, unassigned_projects

def display_assignments(assigned_dates, unassigned_projects):
    """
    Display the assignment of dates to projects.

    Parameters:
    - assigned_dates (dict): Mapping of dates to assigned project names.
    - unassigned_projects (list): List of projects that could not be fully assigned.
    """
    print("\nDate Assignments:")
    print("-" * 40)
    for date, project in sorted(assigned_dates.items()):
        print(f"{date.strftime('%Y-%m-%d')}: {project}")

    print("\nUnassigned Projects:")
    print("-" * 40)
    if not unassigned_projects:
        print("All projects were successfully assigned.")
    else:
        for project in unassigned_projects:
            print(f"Project: {project['name']}")
            print(f"  Assigned Days: {project['assigned_days']}")
            print(f"  Required Days: {project['required_days']}")
            print("-" * 40)


def main():
    parser = argparse.ArgumentParser(description="Resource Scheduler Tool")
    parser.add_argument(
        "-f", "--file", required=True, help="Path to the YAML configuration file."
    )
    args = parser.parse_args()

    yaml_file = args.file

    try:
        assigned_dates, unassigned_projects = assign_project_dates(yaml_file)
        display_assignments(assigned_dates, unassigned_projects)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
