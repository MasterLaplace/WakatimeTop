# WakatimeTop

The Wakatime user ranking site is available at the following address : [https://masterlaplace.github.io/WakatimeTop/](https://masterlaplace.github.io/WakatimeTop/)

## Description

This repository contains scripts to analyze Wakatime data and generate reports. It includes the following scripts:
- `wakalead.py`: Generates a json report on the top 100 users based on Wakatime ranking data plus data from previous users.
- `generate_user_data.py`: Generates a per-user report on the user's 16 most frequently used languages
- `generate_language_data.py`: Generates a top list of users by language.
- `generate_global_leaderboard.py`: Generates a global leaderboard of users based on their elo.
- `requirements.txt`: Contains the required Python packages for the scripts.

### Rules

#### To be on the leaderboard

The data is updated automatically 1 time per week on Monday at 00:00 UTC, using a cron job github action. The data is stored directly here in the repo, and Python scripts are used to generate tables from this data.

To be on this leaderboard, you must first be on the wakatime top 100 leaderboard at the time of the update.
at that time, all your languages with more than 150 minutes of code are taken into account for the calculation of your elo.

In other words, you need 2.5 hours of code in a language to be included in the leaderboard.

> [!NOTE]
> Your wakatime account must be public in order to fetch your profile data.

#### Elo calculation

A new player's elo is equal to the number of hours of code in all his valid languages.
It obviously increases by the amount accumulated since the last update. However, if there is a total period of inactivity of 2 weeks, he loses 2 elo points, i.e. 2 hours of code.

> [!NOTE]
> The "Other" language is not taken into account in the calculation of elo. it is also not available as a valid language for the leaderboard.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

## Running

```bash
# Install dependencies
pip install -r requirements.txt
# Run the scripts
python3 src/wakalead.py
python3 src/generate_user_data.py
python3 src/generate_language_data.py
python3 src/generate_global_leaderboard.py
```
