import os
import json
import requests
from bs4 import BeautifulSoup


def load_users(file_path: str) -> list:
    """
    Load user data from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing user data.

    Returns:
        list: List of users.
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
    url = f"{base_url}?username={username}&layout=compact&langs_count=14&custom_title=WakaTime%20Stats%20since%20May%207%202023"
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


def merge_language_data(existing_data: list, new_data: list) -> list:
    """
    Merge existing language data with new data.

    Args:
        existing_data (list): List of existing data.
        new_data (list): List of new data.

    Returns:
        list: Merged list of data.
    """
    lang_dict = {entry["language"]: entry for entry in existing_data}

    for entry in new_data:
        if entry["language"] in lang_dict:
            existing_time = lang_dict[entry["language"]]["time"]
            new_time = entry["time"]
            total_minutes = time_to_minutes(existing_time) + time_to_minutes(new_time)
            lang_dict[entry["language"]]["time"] = f"{total_minutes // 60} hrs {total_minutes % 60} mins"
        else:
            lang_dict[entry["language"]] = entry

    return list(lang_dict.values())


def save_user_data(output_path: str, data: list) -> None:
    """
    Save user data to a JSON file.

    Args:
        output_path (str): Path to the output file.
        data (list): Data to save.
    """
    with open(output_path, "w") as output_file:
        json.dump(data, output_file, indent=4)


def process_users(users: list, base_url: str, output_dir: str) -> None:
    """
    Process users to fetch and save their WakaTime data.

    Args:
        users (list): List of users.
        base_url (str): Base URL for the API requests.
        output_dir (str): Output directory for JSON files.
    """
    for user in users:
        username = user.get("username")
        if not username:
            continue

        try:
            svg_content = fetch_user_data(username, base_url)
            lang_data = parse_language_data(svg_content)

            output_path = os.path.join(output_dir, f"{username}.json")
            if os.path.exists(output_path):
                with open(output_path, "r") as existing_file:
                    existing_data = json.load(existing_file)
            else:
                existing_data = []

            merged_data = merge_language_data(existing_data, lang_data)
            save_user_data(output_path, merged_data)

            print(f"Data for {username} written to {output_path}")
        except Exception as e:
            print(f"Failed to process {username}: {e}")


if __name__ == "__main__":
    # Path to the file containing user data
    users_file: str = "users_summary.json"
    output_directory: str = "user_data"
    base_api_url: str = "https://github-readme-stats.vercel.app/api/wakatime"

    users_list: list = load_users(users_file)
    create_output_directory(output_directory)
    process_users(users_list, base_api_url, output_directory)
