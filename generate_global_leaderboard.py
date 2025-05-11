import os
import json
from typing import List, Dict


def time_to_minutes(time_str: str) -> int:
    """
    Convert a time string (e.g., '2 hrs 30 mins') to total minutes.

    Args:
        time_str (str): Time string to convert.

    Returns:
        int: Total time in minutes.
    """
    parts = time_str.split()
    total_minutes = 0
    for i in range(0, len(parts), 2):
        value = int(parts[i].replace(",", ""))
        unit = parts[i + 1]
        if "hr" in unit:
            total_minutes += value * 60
        elif "min" in unit:
            total_minutes += value
    return total_minutes


def minutes_to_time(minutes: int) -> str:
    """
    Convert total minutes into a formatted time string.

    Args:
        minutes (int): Total time in minutes.

    Returns:
        str: Formatted time string (e.g., '2 hrs 30 mins').
    """
    hours, mins = divmod(minutes, 60)
    if hours > 0 and mins > 0:
        return f"{hours:,} hrs {mins} mins"
    elif hours > 0:
        return f"{hours:,} hrs"
    else:
        return f"{mins} mins"


def load_user_data(user_data_dir: str) -> List[Dict[str, str]]:
    """
    Load user data from JSON files in the specified directory.

    Args:
        user_data_dir (str): Path to the directory containing user JSON files.

    Returns:
        List[Dict[str, str]]: List of users with their total time.
    """
    users = []

    for filename in os.listdir(user_data_dir):
        if filename.endswith(".json"):
            user_file_path = os.path.join(user_data_dir, filename)
            username = filename.replace(".json", "")

            with open(user_file_path, "r") as user_file:
                user_data = json.load(user_file)

            total_time = user_data.get("total_time", "0 mins")
            total_minutes = time_to_minutes(total_time)

            users.append({"username": username, "total_time": total_time, "total_minutes": total_minutes})

    return users


def generate_global_leaderboard(user_data_dir: str, output_file: str) -> None:
    """
    Generate a global leaderboard JSON file based on total_time.

    Args:
        user_data_dir (str): Path to the directory containing user JSON files.
        output_file (str): Path to the output JSON file.
    """
    users = load_user_data(user_data_dir)
    sorted_users = sorted(users, key=lambda x: x["total_minutes"], reverse=True)

    # Remove the "total_minutes" field for the final output
    for user in sorted_users:
        del user["total_minutes"]

    with open(output_file, "w") as output_json:
        json.dump(sorted_users, output_json, indent=4)

    print(f"Global leaderboard written to {output_file}")


def main() -> None:
    """
    Main function to generate the global leaderboard.
    """
    user_data_dir = "user_data"
    output_file = "global_leaderboard.json"

    generate_global_leaderboard(user_data_dir, output_file)


if __name__ == "__main__":
    main()
