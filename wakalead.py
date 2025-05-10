import requests
import json
from typing import Optional, Dict, Any


def fetch_leaderboard_data(url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch leaderboard data from the given URL.

    Args:
        url (str): The API endpoint to fetch data from.

    Returns:
        Optional[Dict[str, Any]]: The JSON response data if the request is successful, otherwise None.
    """
    response = requests.get(url, headers={"Accept": "application/json"})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None


def load_existing_data(file_path: str) -> Dict[str, Any]:
    """
    Load existing data from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        Dict[str, Any]: The existing data if the file exists, otherwise an empty structure.
    """
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {"data": []}


def merge_data(existing_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge existing data with new data, avoiding duplicates.

    Args:
        existing_data (Dict[str, Any]): The existing data.
        new_data (Dict[str, Any]): The new data to merge.

    Returns:
        Dict[str, Any]: The merged data.
    """
    existing_users = {user["user"]["id"]: user for user in existing_data["data"]}
    for user in new_data["data"]:
        existing_users[user["user"]["id"]] = user
    return {"data": list(existing_users.values())}


def save_data(file_path: str, data: Dict[str, Any]) -> None:
    """
    Save data to a JSON file.

    Args:
        file_path (str): The path to the JSON file.
        data (Dict[str, Any]): The data to save.
    """
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def main() -> None:
    """
    Main function to fetch, merge, and save leaderboard data.
    """
    url: str = "https://wakatime.com/api/v1/leaders"
    file_path: str = "leaders_data.json"

    new_data: Optional[Dict[str, Any]] = fetch_leaderboard_data(url)
    if not new_data:
        return

    existing_data: Dict[str, Any] = load_existing_data(file_path)
    merged_data: Dict[str, Any] = merge_data(existing_data, new_data)
    save_data(file_path, merged_data)

    print("Data updated in leaders_data.json")


if __name__ == "__main__":
    main()
