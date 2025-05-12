import os
import json
import requests
from bs4 import BeautifulSoup
import sys
import math


def load_users(file_path: str) -> list:
    """
    Load user data from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing user data.

    Returns:
        list: List of usernames.
    """
    with open(file_path, "r") as json_file:
        return json.load(json_file)


def create_output_directory(directory: str) -> None:
    """
    Create a directory to store JSON files if it doesn't already exist.

    Args:
        directory (str): Path to the directory to create.
    """
    os.makedirs(directory, exist_ok=True)


def fetch_user_data(username: str, base_url: str) -> str:
    """
    Fetch WakaTime data for a given user.

    Args:
        username (str): GitHub username.
        base_url (str): Base URL for the API requests.

    Returns:
        str: SVG content of the response.
    """
    url = f"{base_url}?username={username}&layout=compact"
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def parse_language_data(svg_content: str) -> list:
    """
    Parse SVG content to extract language information.

    Args:
        svg_content (str): SVG content to parse.

    Returns:
        list: List of languages and time spent.
    """
    soup = BeautifulSoup(svg_content, "html.parser")
    lang_data = []

    for g in soup.find_all("g", {"transform": True}):
        text = g.find("text", {"data-testid": "lang-name"})
        if text:
            lang_info = text.get_text(strip=True)
            lang_name, time = lang_info.split(" - ")
            lang_data.append({"language": lang_name, "time": time})

    return lang_data


def time_to_minutes(time_str: str) -> int:
    """
    Convert a time string into minutes.

    Args:
        time_str (str): Time string (e.g., "2 hrs 30 mins").

    Returns:
        int: Time in minutes.
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
        str: Formatted time string (e.g., "2 hrs 30 mins").
    """
    hours, mins = divmod(minutes, 60)
    if hours > 0 and mins > 0:
        return f"{hours:,} hrs {mins} mins"
    elif hours > 0:
        return f"{hours:,} hrs"
    else:
        return f"{mins} mins"


def calculate_total_time(lang_data: list) -> str:
    """
    Calculate the total time from a list of language data.

    Args:
        lang_data (list): List of language data with time strings.

    Returns:
        str: Total time as a formatted string.
    """
    total_minutes = sum(time_to_minutes(entry["time"]) for entry in lang_data)
    return minutes_to_time(total_minutes)


def filter_languages(lang_data: list) -> list:
    """
    Filter out languages with less than 2.5 hours of time or named "Other".

    Args:
        lang_data (list): List of language data.

    Returns:
        list: Filtered list of language data.
    """
    return [
        entry for entry in lang_data
        if entry["language"] != "Other" and time_to_minutes(entry["time"]) >= 150
    ]


def merge_language_data(existing_data: list, new_data: list) -> list:
    """
    Merge existing language data with new data, replacing the time value.

    Args:
        existing_data (list): List of existing data.
        new_data (list): List of new data.

    Returns:
        list: Merged and sorted list of data.
    """
    lang_dict = {entry["language"]: entry for entry in existing_data}

    for entry in new_data:
        lang_dict[entry["language"]] = entry

    return sorted(lang_dict.values(), key=lambda x: x["language"])


def save_user_data(output_path: str, data: dict) -> None:
    """
    Save user data to a JSON file.

    Args:
        output_path (str): Path to the output file.
        data (dict): Data to save.
    """
    with open(output_path, "w") as output_file:
        json.dump(data, output_file, indent=4)


def reduce_elo(previous_elo: int, reduction: int = 2) -> int:
    """
    Reduce the elo by a specified amount, ensuring it does not go below 0.

    Args:
        previous_elo (int): The previous elo value in minutes.
        reduction (int): The amount to reduce the elo by (default is 2 hours).

    Returns:
        int: The reduced elo value, with a minimum of 0.
    """
    return max(0, previous_elo - reduction)


def calculate_new_elo(
    previous_elo: int,
    previous_total_time: int,
    total_time: str,
    updated: bool,
    filtered_data: list,
    existing_languages: list
) -> int:
    """
    Calculate the new ELO score for a user.

    Args:
        previous_elo (int): The previous ELO score.
        previous_total_time (int): The previous total time in hours.
        total_time (str): The new total time as a formatted string.
        updated (bool): Whether the data was marked as updated.
        filtered_data (list): The filtered list of language data.
        existing_languages (list): The existing list of language data.

    Returns:
        int: The new ELO score.
    """
    final_elo = previous_elo

    if not updated and filtered_data == existing_languages:
        final_elo = reduce_elo(previous_elo)
    elif filtered_data != existing_languages:
        new_total_time = math.ceil(time_to_minutes(total_time) / 60)
        diff = max(0, new_total_time - previous_total_time)
        final_elo = previous_elo + diff

    return final_elo


def process_user(username: str, base_url: str, output_dir: str) -> None:
    """
    Process a single user to fetch and save their WakaTime data.

    This function fetches the user's WakaTime data, compares it with existing data,
    calculates the total time spent, and updates the ELO score. If the data has not
    changed, the ELO is reduced by a fixed amount.

    Args:
        username (str): GitHub username.
        base_url (str): Base URL for the API requests.
        output_dir (str): Output directory for JSON files.
    """
    try:
        svg_content = fetch_user_data(username, base_url)
        lang_data = parse_language_data(svg_content)

        output_path = os.path.join(output_dir, f"{username}.json")
        if os.path.exists(output_path):
            with open(output_path, "r") as existing_file:
                existing_data = json.load(existing_file)
                existing_languages = existing_data.get("languages", [])
                str_previous_total_time = existing_data.get("total_time", "0 mins")
                previous_elo = existing_data.get("elo", 0)
                updated = existing_data.get("updated", True)
        else:
            existing_languages = []
            str_previous_total_time = "0 mins"
            previous_elo = 0
            updated = True

        previous_total_time = math.ceil(time_to_minutes(str_previous_total_time) / 60)

        merged_data = merge_language_data(existing_languages, lang_data)
        filtered_data = filter_languages(merged_data)
        total_time = calculate_total_time(filtered_data)

        final_elo = calculate_new_elo(
            previous_elo,
            previous_total_time,
            total_time,
            updated,
            filtered_data,
            existing_languages,
        )

        user_data = {
            "total_time": total_time,
            "updated": (filtered_data != existing_languages),
            "elo": final_elo,
            "languages": filtered_data,
        }

        save_user_data(output_path, user_data)
        print(f"Data for {username} written to {output_path}")
    except Exception as e:
        print(f"Failed to process {username}: {e}")


def process_users(usernames: list, base_url: str, output_dir: str) -> None:
    """
    Process multiple users to fetch and save their WakaTime data.

    This function iterates over a list of usernames, fetching and processing
    their WakaTime data individually.

    Args:
        usernames (list): List of Wakatime usernames.
        base_url (str): Base URL for the API requests.
        output_dir (str): Output directory for JSON files.
    """
    for username in usernames:
        process_user(username, base_url, output_dir)


def main() -> None:
    """
    Main function to process user data. If "add" argument is provided, add a single user.
    Otherwise, process all users.
    """
    users_file: str = "data/users.json"
    output_directory: str = "data/users"
    base_api_url: str = "https://github-readme-stats.vercel.app/api/wakatime"

    create_output_directory(output_directory)

    if len(sys.argv) > 1 and sys.argv[1] == "add":
        username = input("Enter username: ")
        process_user(username, base_api_url, output_directory)
    else:
        usernames: list = load_users(users_file)
        process_users(usernames, base_api_url, output_directory)


if __name__ == "__main__":
    main()
