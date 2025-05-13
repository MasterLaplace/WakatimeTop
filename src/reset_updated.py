import os
import json


def reset_updated(directory):
    """
    Resets the “updated” value to true for all JSON files in a given directory.

    Args:
        directory (str): Path to the directory containing the JSON files.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as file:
                data = json.load(file)

            if "updated" in data:
                data["updated"] = True

            with open(filepath, "w") as file:
                json.dump(data, file, indent=4)
            print(f"Reset 'updated' to true in {filename}")


if __name__ == "__main__":
    users_directory = "data/users"
    reset_updated(users_directory)
