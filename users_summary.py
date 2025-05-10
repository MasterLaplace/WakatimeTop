import json
import sys
from typing import List, Dict, Any


def load_json_file(file_path: str) -> Any:
    """
    Load data from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Any: Data loaded from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    with open(file_path, "r") as json_file:
        return json.load(json_file)


def save_json_file(file_path: str, data: Any) -> None:
    """
    Write data to a JSON file with an indentation of 4.

    Args:
        file_path (str): Path to the JSON file.
        data (Any): Data to write to the file.
    """
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def extract_users_summary(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract a list of dictionaries containing only "id" and "username"
    from the provided data.

    Args:
        data (dict): Data containing user information.

    Returns:
        list: List of dictionaries with "id" and "username".
    """
    return [{"id": user["user"]["id"], "username": user["user"]["username"]} for user in data["data"]]


def merge_users(existing_users: List[Dict[str, str]], new_users: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Merge existing users with new users. Updates users with the same "id".

    Args:
        existing_users (list): List of existing users.
        new_users (list): List of new users.

    Returns:
        list: Merged list of users.
    """
    existing_users_dict = {user["id"]: user for user in existing_users}
    for user in new_users:
        existing_users_dict[user["id"]] = user
    return list(existing_users_dict.values())


def add_user(user_id: str, username: str) -> None:
    """
    Add a new user to the users_summary.json file.

    Args:
        user_id (str): The unique ID of the user.
        username (str): The username of the user.
    """
    try:
        existing_users: List[Dict[str, str]] = load_json_file("users_summary.json")
    except FileNotFoundError:
        existing_users = []

    for user in existing_users:
        if user["id"] == user_id:
            print(f"User with ID {user_id} already exists.")
            return

    new_user = {"id": user_id, "username": username}
    existing_users.append(new_user)
    save_json_file("users_summary.json", existing_users)
    print(f"User {username} added successfully.")


def main() -> None:
    """
    Main entry point of the script. If "add" argument is provided, add a single user.
    Otherwise, fetch all users, merge data, and update the JSON file.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        user_id = input("Enter user ID: ")
        username = input("Enter username: ")
        add_user(user_id, username)
    else:
        try:
            data: Dict[str, Any] = load_json_file("leaders_data.json")
        except FileNotFoundError:
            print("Error: The file leaders_data.json was not found.")
            return

        users_summary: List[Dict[str, str]] = extract_users_summary(data)

        try:
            existing_users: List[Dict[str, str]] = load_json_file("users_summary.json")
        except FileNotFoundError:
            existing_users = []

        updated_users: List[Dict[str, str]] = merge_users(existing_users, users_summary)
        save_json_file("users_summary.json", updated_users)

        print("Users summary updated in users_summary.json")


if __name__ == "__main__":
    main()
