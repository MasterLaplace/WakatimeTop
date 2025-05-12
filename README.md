# WakatimeTop

## Description
This repository contains scripts to analyze Wakatime data and generate reports. It includes the following scripts:
- `wakalead.py`: Generates a json report on the top 100 users based on Wakatime ranking data plus data from previous users.
- `generate_user_data.py`: Generates a per-user report on the user's 16 most frequently used languages
- `generate_language_data.py`: Generates a top list of users by language.
- `generate_global_leaderboard.py`: Generates a global leaderboard of users based on their elo.
- `requirements.txt`: Contains the required Python packages for the scripts.

## Running

```bash
# Install dependencies
pip install -r requirements.txt
# Run the scripts
python3 wakalead.py
python3 generate_user_data.py
python3 generate_language_data.py
python3 generate_global_leaderboard.py
```
