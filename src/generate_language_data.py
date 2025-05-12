import os
import json
from collections import defaultdict
from typing import List, Dict, Any, DefaultDict


def create_directory(directory_path: str) -> None:
    """
    Create a directory if it does not already exist.

    Args:
        directory_path (str): Path to the directory to create.
    """
    os.makedirs(directory_path, exist_ok=True)


def load_user_data(user_data_dir: str) -> DefaultDict[str, List[Dict[str, str]]]:
    """
    Load user data from JSON files in the specified directory.
    Languages with "Other" or less than 150 minutes (2.5 hours) are ignored.

    Args:
        user_data_dir (str): Path to the directory containing user JSON files.

    Returns:
        DefaultDict[str, List[Dict[str, str]]]: A dictionary mapping languages to user data.
    """
    language_data: DefaultDict[str, List[Dict[str, str]]] = defaultdict(list)

    for filename in os.listdir(user_data_dir):
        if filename.endswith(".json"):
            user_file_path = os.path.join(user_data_dir, filename)
            username = filename.replace(".json", "")

            with open(user_file_path, "r") as user_file:
                user_data = json.load(user_file)

            for entry in user_data.get("languages", []):
                language = entry["language"]
                time = entry["time"]

                if language == "Other" or time_to_minutes(time) < 150:
                    continue

                if not any(user["username"] == username for user in language_data[language]):
                    language_data[language].append({"username": username, "time": time})

    return language_data


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


def merge_and_sort_users(existing_users: List[Dict[str, str]], new_users: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Merge existing user data with new user data and sort by time in descending order.

    Args:
        existing_users (List[Dict[str, str]]): List of existing user data.
        new_users (List[Dict[str, str]]): List of new user data.

    Returns:
        List[Dict[str, str]]: Merged and sorted list of user data.
    """
    user_dict = {user["username"]: user for user in existing_users}

    for user in new_users:
        user_dict[user["username"]] = user

    return sorted(user_dict.values(), key=lambda x: time_to_minutes(x["time"]), reverse=True)


def write_language_data(language_data: DefaultDict[str, List[Dict[str, str]]], output_dir: str) -> None:
    """
    Write language-specific user data to JSON files in the specified directory.

    Args:
        language_data (DefaultDict[str, List[Dict[str, str]]]): Dictionary mapping languages to user data.
        output_dir (str): Path to the directory where JSON files will be written.
    """
    for language, users in language_data.items():
        sanitized_language = language.replace(" ", "_").replace("/", "_")
        output_path = os.path.join(output_dir, f"{sanitized_language}.json")

        if os.path.exists(output_path):
            with open(output_path, "r") as lang_file:
                existing_users = json.load(lang_file)
        else:
            existing_users = []

        sorted_users = merge_and_sort_users(existing_users, users)

        with open(output_path, "w") as lang_file:
            json.dump(sorted_users, lang_file, indent=4)

        print(f"Data for language '{language}' written to {output_path}")


def write_language_list(language_data: DefaultDict[str, List[Dict[str, str]]], output_file: str) -> None:
    """
    Write a JSON file containing the list of all languages.

    Args:
        language_data (DefaultDict[str, List[Dict[str, str]]]): Dictionary mapping languages to user data.
        output_file (str): Path to the file where the JSON file will be written.
    """
    language_list = [language.replace(" ", "_").replace("/", "_") for language in language_data.keys()]

    with open(output_file, "w") as lang_list_file:
        json.dump(language_list, lang_list_file, indent=4)

    print(f"Language list written to {output_file}")


def main() -> None:
    """
    Main function to process user data and generate language-specific data files.
    """
    user_data_dir: str = "data/users"
    language_data_dir: str = "data/languages"
    language_data_list: str = "data/languages.json"

    create_directory(language_data_dir)
    language_data = load_user_data(user_data_dir)
    write_language_data(language_data, language_data_dir)
    write_language_list(language_data, language_data_list)


if __name__ == "__main__":
    main()
