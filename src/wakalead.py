import requests
import json
from typing import Optional, List


def fetch_leaderboard_data(url: str) -> Optional[List[str]]:
    """
    Fetch leaderboard data from the given URL and extract usernames.

    Args:
        url (str): The API endpoint to fetch data from.

    Returns:
        Optional[List[str]]: A list of usernames if the request is successful, otherwise None.
    """
    response = requests.get(url, headers={"Accept": "application/json"})
    if response.status_code == 200:
        data = response.json()
        return [user["user"]["username"] for user in data["data"] if "user" in user and "username" in user["user"]]
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None


def load_existing_usernames(file_path: str) -> List[str]:
    """
    Load existing usernames from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        List[str]: The existing usernames if the file exists, otherwise an empty list.
    """
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []


def save_usernames(file_path: str, usernames: List[str]) -> None:
    """
    Save usernames to a JSON file.

    Args:
        file_path (str): The path to the JSON file.
        usernames (List[str]): The usernames to save.
    """
    with open(file_path, "w") as json_file:
        json.dump(usernames, json_file, indent=4)


def merge_usernames(existing_usernames: List[str], new_usernames: List[str]) -> List[str]:
    """
    Merge existing usernames with new usernames, avoiding duplicates and filtering out None values.

    Args:
        existing_usernames (List[str]): List of existing usernames.
        new_usernames (List[str]): List of new usernames.

    Returns:
        List[str]: Merged list of usernames.
    """
    filtered_existing = [username for username in existing_usernames if username]
    filtered_new = [username for username in new_usernames if username]
    return sorted(set(filtered_existing + filtered_new))


def main() -> None:
    """
    Main function to fetch, merge, and save leaderboard usernames.
    """
    url: str = "https://wakatime.com/api/v1/leaders"
    file_path: str = "data/users.json"

    new_usernames: Optional[List[str]] = fetch_leaderboard_data(url)
    if not new_usernames:
        return

    existing_usernames: List[str] = load_existing_usernames(file_path)
    merged_usernames: List[str] = merge_usernames(existing_usernames, new_usernames)
    save_usernames(file_path, merged_usernames)

    print("Usernames updated in users.json")


if __name__ == "__main__":
    main()
